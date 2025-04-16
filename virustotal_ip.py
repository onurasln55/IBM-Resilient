# -*- coding: utf-8 -*-
# <<PUT YOUR COPYRIGHT TEXT HERE>>
# Generated with resilient-sdk v51.0.4.0.1351

"""AppFunction implementation"""

from resilient_circuits import AppFunctionComponent, app_function, FunctionResult
from resilient_lib import IntegrationError, validate_fields
import logging
from json import loads
import requests
import urllib3

PACKAGE_NAME = "onur_virustotal_ip"
FN_NAME = "virustotal_ip"

# Log ayarları
logging.basicConfig(filename='virustotal_ip.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class FunctionComponent(AppFunctionComponent):
    """Component that implements function 'virustotal_ip'"""

    def __init__(self, opts):
        super(FunctionComponent, self).__init__(opts, PACKAGE_NAME)

    @app_function(FN_NAME)
    def _app_function(self, fn_inputs):
        """
        Function: IP adresini virustotal üzerinde sorgular.
        Inputs:
            -   fn_inputs.ip
            -   fn_inputs.api_key
        """

        yield self.status_message(f"Starting App Function: '{FN_NAME}'")

        ip = fn_inputs.ip_for_virustotal
        key_vt=fn_inputs.api_key
 

        try:

            ##################################################################################
            url = "https://www.virustotal.com/api/v3/ip_addresses/"+ip
            headers = {
                "Accept": "application/json",
                "x-apikey": key_vt
            }
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            try:
                response = requests.get(url, headers=headers,verify=False)
                json_response = loads(response.text)
                try:
                    malicious=json_response["data"]["attributes"]["last_analysis_stats"]["malicious"]
                except:
                    malicious=""
                try:
                    suspicious=json_response["data"]["attributes"]["last_analysis_stats"]["suspicious"]
                except:
                    suspicious=""
                try:
                    whois=json_response["data"]["attributes"]["whois"]
                    whois=whois.replace("\n", "<br>")
                except:
                    whois=""
                yield self.status_message(f"Başarılı sorgu")
                yield FunctionResult({"success": True,"ip":ip, "malicious": malicious,"suspicious":suspicious,"whois":whois})
                return 
            except:
                yield FunctionResult({"success": False, "reason": "Try da hata var"})
                return

            ##################################################################################
        except Exception as e:
            yield FunctionResult({"success": False, "reason": str(e)})

 
