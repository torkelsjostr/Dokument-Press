# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class AccountInvoiceChangeType(models.TransientModel):
    _name = 'account.invoice.change.type'
    _description = 'Account Invoice Change Type'
    
    new_type = fields.Selection([
                ('in_invoice','Vendor Bill'),
                ('in_refund','Vendor Credit Note'),
            ],
            required=True)
        
    @api.multi
    def _change_type(self, invoice, new_type):
        invoice = invoice.sudo()
        if invoice.state != 'draft' or new_type == invoice.type:
            return False
        
        # Change type
        invoice.type = new_type
        return True
        
    @api.multi        
    def action_change_type(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        
        for invoice in self.env['account.invoice'].browse(active_ids):
            status = self._change_type(invoice, self.new_type)
            if status:
                invoice._cr.commit()
            elif len(active_ids) == 1:
                    raise UserError(_("Not able to change type in state different from draft or has the same type."))
            else:
                invoice._cr.rollback()
        return {'type': 'ir.actions.act_window_close'}