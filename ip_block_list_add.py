# -*- coding: utf-8 -*-
# <<PUT YOUR COPYRIGHT TEXT HERE>>
# Generated with resilient-sdk v51.0.4.0.1351

"""AppFunction implementation"""

from resilient_circuits import AppFunctionComponent, app_function, FunctionResult
from resilient_lib import IntegrationError, validate_fields
import paramiko
import logging

PACKAGE_NAME = "onur_ip_block"
FN_NAME = "ip_block"

# Log ayarları
logging.basicConfig(filename='ip_blocker.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class FunctionComponent(AppFunctionComponent):
    """Component that implements function 'ip_block'"""

    def __init__(self, opts):
        super(FunctionComponent, self).__init__(opts, PACKAGE_NAME)

    @app_function(FN_NAME)
    def _app_function(self, fn_inputs):
        """
        Function: IP adresini uzak bir sunucudaki blocklist dosyasına ekler.
        Inputs:
            -   fn_inputs.ip_to_block
        """

        yield self.status_message(f"Starting App Function: '{FN_NAME}'")

        ip_to_block = fn_inputs.ip_to_block

        remote_ip = "<YOUR_SSH_IP>"
        username = "<YOUR_SSH_USERNAME>"
        password = "<YOUR_SSH_PASSWORD>"
        blocklist_path = "/var/www/html/list.txt"

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=remote_ip, username=username, password=password)

            # Dosya içeriğini oku
            check_command = f'cat {blocklist_path}'
            stdin, stdout, stderr = ssh.exec_command(check_command)
            file_content = stdout.read().decode().splitlines()
            error = stderr.read().decode().strip()

            if error:
                logging.error(f"Dosya okuma hatası: {error}")
                ssh.close()
                yield FunctionResult({"success": False, "reason": error})
                return

            # IP zaten varsa ekleme ama yine de True dön
            if ip_to_block in file_content:
                # Boş satırları temizle
                ssh.exec_command(f"sed -i '/^$/d' {blocklist_path}")
                ssh.close()
                yield self.status_message(f"IP already exists in blocklist: {ip_to_block}")
                yield FunctionResult({"success": True, "ip": ip_to_block, "already_exists": True})
                return

            # IP'yi ekle
            add_command = f'echo "{ip_to_block}" >> {blocklist_path}'
            ssh.exec_command(add_command)

            # Boş satırları temizle
            ssh.exec_command(f"sed -i '/^$/d' {blocklist_path}")

            ssh.close()
            yield self.status_message(f"Successfully added IP to blocklist: {ip_to_block}")
            yield FunctionResult({"success": True, "ip": ip_to_block, "already_exists": False})

        except Exception as e:
            logging.error(f"SSH bağlantısı veya komut yürütme hatası: {str(e)}")
            yield FunctionResult({"success": False, "reason": str(e)})

 
