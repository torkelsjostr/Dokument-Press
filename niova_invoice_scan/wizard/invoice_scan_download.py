# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, api, fields

def convert_date(date):
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


class InvoiceScanDownload(models.TransientModel):
    _name = 'invoicescan.download'
    _description = 'Invoice Scan Download'
    
    date_from = fields.Datetime(string='Date From', required=True)
    date_to = fields.Datetime(string='Date To')

    @api.multi
    def action_download(self):
        search = {'created': convert_date(self.date_from)}
        if self.date_to:
            search['created'] += '&' + convert_date(self.date_to)    
        self.env['invoicescan.voucher'].receive_scanned_vouchers(search=search, seen='both')
        return {}