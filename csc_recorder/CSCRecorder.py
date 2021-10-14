import json
from http import client as http_client
from typing import OrderedDict, Tuple

import xmltodict
from jinja2 import Environment, PackageLoader, select_autoescape

from csc_recorder.APIHandler import APIHandler

env = Environment(
    loader=PackageLoader("csc_recorder.CSC"), autoescape=select_autoescape()
)


class CSCRecorder(APIHandler):
    def __init__(self, host, username, password):
        self._api_handler = APIHandler(
            host,
            username,
            password,
            headers={"Content-Type": "application/xml", "Accept": "*/*"},
        )

    def _clean_response(self, r: str) -> str:
        r = r.encode("ascii", "ignore").decode("unicode_escape")
        r = r.replace('<?xml version="1.0" encoding="UTF-8"?>', "")
        r = r[1:]
        r = r[:-1]
        return r

    def _parse_xml_string(self, xml):
        ...

    def _get_fips(self):
        ...

    def send_package(
        self,
        client_package_id: str,
        fips: int,
        assigned_office: str,
        params: dict = {},
        service_type: str = None,
        no_document: bool = False,
        debug: bool = False,
    ) -> Tuple[OrderedDict, http_client.HTTPResponse]:
        """
        Sends a request to generate a package to CSC eRecorder

        Ex param dictionary:
        params = {
            "document_name": "some_name",
            "document_type": "Deed",
        }

        :param client_package_id: the package ID that we will be uploading
        :param fips: the FIPS code of the county
        :param assigned_office: the name of the office to assign the package to
        :param params: dict of parameters to send to CSC
        :param service_type: currently only 'paperfulfillment' option
        :param no_document: bool, if true, will send no document info
        :return: dict of package information
        """
        template = env.get_template("CreatePackage.xml")
        params["no_document"] = no_document
        params["client_package_id"] = client_package_id
        params["fips"] = fips  # TODO generate FIPS
        params["assigned_office"] = assigned_office
        payload = template.render(**params)

        if debug:
            print(payload)

        url = "/v1/package?contentType=xml"

        if service_type:
            url = f"{url}&serviceType={service_type}"

        response = self._api_handler.send_request("POST", url, payload)

        cleaned_response = self._clean_response(str(response))

        return xmltodict.parse(cleaned_response)

    def get_document_type(self, fips: str) -> Tuple[dict, http_client.HTTPResponse]:
        response = self._api_handler.send_request("GET", f"/v1/documentType/{fips}")

        return json.loads(response)

    def get_package_status(
        self, binder_id: str
    ) -> Tuple[dict, http_client.HTTPResponse]:
        """
        Returns a packages status with file and fees.

        :param binder_id: the binder ID of the package
        """
        response = self._api_handler.send_request(
            "GET",
            (
                f"/v3/package/{binder_id}?returnFileType=pdf"
                "&embed=true&contentType=json&includeImage=true"
            ),
        )

        return xmltodict.parse(response)

    def get_mortgage_tax_req(
        self, county_id: str
    ) -> Tuple[dict, http_client.HTTPResponse]:
        """ """
        response = self._api_handler.send_request(
            "GET",
            (
                f"/v1/county/{county_id}"
                "/AdditionalMortgageTaxNoRecordingFee/requirements"
            ),
        )
        return json.loads(response)

    def get_assigned_office(self) -> Tuple[dict, http_client.HTTPResponse]:
        """
        Returns the current selected office from the CSC Platform.
        """
        response = self._api_handler.send_request("GET", "/v1/office/assigned")

        return json.loads(response)

    def get_offices(self) -> Tuple[dict, http_client.HTTPResponse]:
        """
        Returns all offices that have been created for your account.
        """
        response = self._api_handler.send_request("GET", "/v1/office")

        return json.loads(response)

    def get_state_offices(
        self, state: str, service_type=None
    ) -> Tuple[dict, http_client.HTTPResponse]:
        """
        Returns a list of county offices for that given state.

        :param state: the state to get county offices for
        :param service_type: the service type to filter by Ex: 'paper'
        """
        url = f"/v1/state/{state}"
        if service_type:
            url += f"?serviceType={service_type}"

        response = self._api_handler.send_request("GET", url)

        return json.loads(response)
