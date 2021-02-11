# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _get_alias_contact(self):
        invoicescan_alias = self.env.ref('niova_invoice_scan.mail_alias_invoice_scan')
        return invoicescan_alias._fields['alias_contact'].selection
    
    module_niova_invoice_scan = fields.Boolean(string='Allow the invoice to be synchronize by invoice scan')
    invscan_client_secret = fields.Char("Activation Key")
    invscan_active = fields.Boolean("Invoice Scan Activated", readonly=True, default=False)
    invscan_mail_prefix = fields.Char(string='Default Alias Name for Invoice Scan')
    invscan_mail_contact = fields.Selection(selection=_get_alias_contact, string='Alias Contact Security', help="Policy to post a message on the document using the mailgateway.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            invscan_client_secret = get_param('invoice_scan_client_secret', default=False),
            invscan_active = get_param('invoice_scan_active', default=False),
            invscan_mail_prefix = self.env.ref('niova_invoice_scan.mail_alias_invoice_scan').alias_name,
            invscan_mail_contact = self.env.ref('niova_invoice_scan.mail_alias_invoice_scan').alias_contact,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env.ref('niova_invoice_scan.mail_alias_invoice_scan').write({'alias_name': self.invscan_mail_prefix, 'alias_contact': self.invscan_mail_contact})