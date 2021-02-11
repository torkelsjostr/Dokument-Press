# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class InvoiceScanUpload(models.TransientModel):
    _name = 'invoicescan.upload'
    _description = 'Invoice Scan Upload'
    
    type = fields.Selection(selection=[
            ('in_invoice', 'Vendor Bill'),
            ('in_refund', 'Vendor Credit Note'),
            #('out_invoice', 'Customer Invoice'),
            #('out_refund', 'Customer Credit Note'),
            #('out_receipt', 'Sales Receipt'),
            #('in_receipt', 'Purchase Receipt')
        ], string='Type', required=True, default="in_invoice")
    company_id = fields.Many2one('res.company', string='Company')
    payment_method = fields.Char(string="Payment Method", default='')
    note = fields.Char('Note')
    attachment_ids = fields.Many2many('ir.attachment', 'invoice_scan_upload_ir_attachments_rel', 'wizard_id', 'attachment_id', string='Attachments', required=True)

    @api.multi
    def action_upload(self):
        if not self.type:
            raise UserError(_("Please select type before uploading files."))
        if not self.attachment_ids:
            raise UserError(_("Please add files to upload."))
        
        default_vals = self._prepare_voucher_values(self._uid)
        vouchers = self.env['invoicescan.voucher']
        for attachment in self.attachment_ids:
            vals = default_vals.copy()
            vouchers += self.env['invoicescan.voucher'].upload_attachment_2_voucher(False, attachment, vals)
        return {
            'name': _('Vouchers'),
            'domain': [('id', 'in', vouchers.ids)],
            'view_type': 'form',
            'res_model': 'invoicescan.voucher',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'main',
            'view_mode': 'tree,form'
        }

    @api.multi
    def _prepare_voucher_values(self, user_id):
        return {
            'state': 'upload',
            'voucher_type': self.type,
            'catalog_debitor_id': self.company_id.id if self.company_id else '',
            'payment_method': self.payment_method,
            'note': self.note,
            'upload_user_id': user_id
        }