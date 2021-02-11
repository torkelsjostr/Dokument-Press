# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import api, fields, models


class AccountInvoiceControl(models.TransientModel):
    _name = 'account.invoice.control'
    _description = 'Invoice Control'
    
    invoice_id = fields.Many2one('account.invoice', readonly=True)
        
    @api.multi
    def action_invoice_open(self):
        return self.invoice_id.with_context(force_validate_invoice=True).action_invoice_open()