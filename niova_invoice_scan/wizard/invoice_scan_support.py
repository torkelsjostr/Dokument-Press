# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, api, fields

EMAIL_PAPERFLOW_SUPPORT = 'support@bilagscan.dk'
EMAIL_PAPERFLOW_FEEDBACK = 'feedback@bilagscan.dk'
EMAIL_NIOVA_SUPPORT = 'invoice_scan_support@niovait.atlassian.net'

class InvoiceScanSupport(models.TransientModel):
    _name = 'invoicescan.support'
    _description = 'Invoice Scan Support'
    
    name = fields.Char(string='Name')
    voucher_id = fields.Many2one('invoicescan.voucher', required=True, readonly=True)
    email_to = fields.Char(string='To Email')
    email_from = fields.Char(string='From Email')
    note = fields.Text(string='Note', required=True)
    type_supported = fields.Boolean(string='Type Supported', compute='_compute_supported_types', readonly=True)
    voucher_type = fields.Selection([
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('out_receipt', 'Sales Receipt'),
        ('in_receipt', 'Purchase Receipt')
        ],
        string='What kind of document?', required=True)
    scanning_type = fields.Selection([
        ('hdr', 'High guaranteed accuracy (Standard)'),
        ('ai', 'AI without guaranteed high accuracy (Special Agreement)')
        ],
        string='Type of product?',
        required=True)
    error_type = fields.Selection([
        # Niova Support
        ('niova_partner', 'Partner was not selected or selected incorrect'),
        ('niova_flow', 'Vendor bill was not processed automatic'),
        
        # Paper flow support
        ('paperflow_type', 'Incorrect document Type'),
        ('paperflow_amount', 'Incorrect amount/s'),
        ('paperflow_partner', 'Wrong scanned vendor/partner/VAT'),
        ('paperflow_line', 'Missing scanned lines'),
        ('paperflow_line_data', 'Incorrect data for scanned lines'),
    
        # Niova Support
        ('niova_other', 'Other')
        ],
        string='What kind of issue?',
        required=True)
    name_voucher_type = fields.Char(compute='_compute_selection_name')
    name_scanning_type = fields.Char(compute='_compute_selection_name')
    name_error_type = fields.Char(compute='_compute_selection_name')

    @api.depends('voucher_type')
    def _compute_supported_types(self):
        for support in self:
            if support.voucher_type in ('in_invoice', 'in_refund'):
                support.type_supported = True
            else:
                support.type_supported = False

    @api.depends('voucher_type', 'scanning_type', 'error_type')
    def _compute_selection_name(self):
        for support in self:
            if support.voucher_type:
                support.name_voucher_type = dict(support._fields.get('voucher_type').selection).get(support.voucher_type)
            if support.scanning_type:
                support.name_scanning_type = dict(support._fields.get('scanning_type').selection).get(support.scanning_type)
            if support.error_type:
                support.name_error_type = dict(support._fields.get('error_type').selection).get(support.error_type)
    
    @api.multi        
    def action_send_email(self):
        self.name = self.env.user.name
        self.email_to = self._get_mail_to()
        self.email_from = self.env.user.login if self.env.user.login else self.env.user.company_id.email
        template = self.env.ref('niova_invoice_scan.email_template_invoice_scan')
        self.env['mail.template'].browse(template.id).send_mail(self.id)

    def _get_mail_to(self):
        email = EMAIL_NIOVA_SUPPORT
        if 'paperflow' in self.error_type:
            if self.scanning_type == 'hdr':
                email = EMAIL_PAPERFLOW_SUPPORT
            else:
                email = EMAIL_PAPERFLOW_FEEDBACK
        return email