# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class InvoiceScanActivation(models.TransientModel):
    _name = 'invoicescan.activation'
    _description = 'Activate Invoice Scan'
    
    client_secret = fields.Char("Activation Key")
    
    @api.multi
    def action_activate_invoice_scan(self):
        if not self.client_secret:
            raise UserError(_("Please insert an activation key."))
        
        # Save secret
        set_param = self.env['ir.config_parameter'].set_param
        set_param('invoice_scan_client_secret', (self.client_secret or '').strip())
        
        # Create invoice scan instance
        response = self.env['invoicescan.manager'].activate(self.client_secret)
        if not response:
            raise UserError(_("Activation failed. This may due to wrong secret."))
        
        # Activate cron job
        self._activate_cron()
        return self.env.ref('base_setup.action_general_configuration').read()[0]
    
    @api.multi
    def action_dactivate_invoice_scan(self):
        if not self.client_secret:
            raise UserError(_("There are no key registered and there are therefore nothing to deactivate."))
        
        # Clear invoice scan instance
        self.env['invoicescan.manager'].reset(self.client_secret)
        
        # Clear saved parameters
        set_param = self.env['ir.config_parameter'].set_param
        set_param('invoice_scan_client_secret', '')
        set_param('invoice_scan_active', False)
        
        # Deactivate cron job
        self._activate_cron(False)
        return self.env.ref('base_setup.action_general_configuration').read()[0]
    
    @api.multi
    def _activate_cron(self, activate=True):
        scan_service = self.env.ref('niova_invoice_scan.ir_crone_invoice_scan_service')
        if scan_service:
            cron = self.env['ir.cron'].browse(scan_service.id)
            if cron:
                cron.try_write({'active': activate})

    @api.multi        
    def recieve_activation_key(self):
        return self.env['invoicescan.manager'].redirect_to_invoicescan()