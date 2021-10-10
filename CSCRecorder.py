import requests
from jinja2 import (
    Environment,
    PackageLoader,
    select_autoescape
)
import xmltodict
import xml.etree.ElementTree as ET
import json


env = Environment(
    loader=PackageLoader("CSC"),
    autoescape=select_autoescape()
)

class CSCRecorder():
    TEST_URL = 'https://ep4-uat.erecording.com/api/'
    PROD_URL = 'http://'
    headers = {
        'Content-Type': 'application/xml'
    }

    def __init__(self, username, password, test=False):
        if not test:
            self.url = self.TEST_URL
        else:
            self.url = self.PROD_URL

        self.username = username
        self.password = password

    def _clean_response(self, r):
        r = r.encode('ascii', 'ignore').decode('unicode_escape')
        r = r.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
        r = r[1:]
        r = r[:-1]
        return r

    def _parse_xml_string(self, xml):
        return None
    
    def _get_fips(self):
        ...

    def send_package(self, params: dict):
        template = env.get_template('CreatePackage.xml')
        payload = template.render(**params)
        response = requests.request(
            "POST", 
            f"{self.url}/v1/package?contentType=xml", 
            headers=self.headers, 
            data=payload,
            auth=(self.username, self.password)
        )

        if response.status_code not in [200, 201]:
            return None

        cleaned_response = self._clean_response(str(response.text))
        
        return xmltodict.parse(cleaned_response)
    
    def get_document_type(self, fips: dict):
        url = f"{self.url}/v1/documentType/{fips}"
        response = requests.request(
            "GET", 
            url, 
            headers=self.headers, 
            auth=(self.username, self.password)
        )

        if response.status_code not in [200, 201]:
            return None
        
        return json.loads(response.content)
    
    def get_package_status(self, binder_id: str):
        url = f"{self.url}/v3/package/{binder_id}?returnFileType=pdf&embed=true&contentType=json&includeImage=true"
        response = requests.request(
            "GET", 
            url,
            headers=self.headers,
            auth=(self.username, self.password)
        )
    
        if response.status_code not in [200, 201]:
            return None
    
        return xmltodict.parse(response.content)
    
    def additonal_mortgage_tax_requirements(self, county_id: str):
        url = f"{self.url}/v1/county/{county_id}/AdditionalMortgageTaxNoRecordingFee/requirements"
        response = requests.request(
            "GET", 
            url, 
            headers=self.headers, 
            auth=(self.username, self.password)
        )

        if response.status_code not in [200, 201]:
            return None
        
        return json.loads(response.content)