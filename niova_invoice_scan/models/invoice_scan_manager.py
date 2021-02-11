# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)

_invoice_scan_services = {}

class InvoiceScanManager(models.AbstractModel):
    _name = 'invoicescan.manager'
    _description = 'Invoice Scan Manager'
    
    def activate(self, client_secret):
        global _invoice_scan_services
        if client_secret not in _invoice_scan_services:
            scan_service = self.env['invoicescan.service']
            scan_service.set_client_secret(client_secret)
            status = scan_service.get_access_token()
            if not status:
                return False
            _invoice_scan_services[client_secret] = scan_service
        return True
        
    def reset(self, client_secret):
        global _invoice_scan_services
        if client_secret in _invoice_scan_services:
            del _invoice_scan_services[client_secret]
        return True
    
    def get_scan_service(self, client_secret):
        if client_secret and client_secret not in _invoice_scan_services:
            self.activate(client_secret)
        scan_service = _invoice_scan_services.get(client_secret, False)
        if scan_service == False:
            error_message  = 'Was not able get scan service. This is caused by non registered client secret.'
            raise Exception(_(error_message))
        return scan_service
    
    def redirect_to_invoicescan(self):
        return self.env['invoicescan.service'].redirect_to_invoicescan()