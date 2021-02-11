# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova IT ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova IT ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    invscan_purchase_sequence = fields.Many2one('ir.sequence',
                                                config_parameter="invoice_scan_purchase_sequence",
                                                string='Purchase Sequence',
                                                help="Choose the sequence the purchase orders use. This will be used to search purcahse orders in the Vendor Bills.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        invoice_scan_purchase_sequence = get_param('invoice_scan_purchase_sequence', default=False)
        if invoice_scan_purchase_sequence:
            res.update(invscan_purchase_sequence = int(invoice_scan_purchase_sequence))
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].set_param
        set_param('invoice_scan_purchase_sequence', self.invscan_purchase_sequence.id)