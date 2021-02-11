# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova IT ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova IT ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, api
import re
import logging

_logger = logging.getLogger(__name__)

SEPERATOR_CHARACTERS = ['-', ' ']


class ScannedVoucher(models.Model):
    _inherit = 'invoicescan.voucher'

    @api.depends('currency')
    def _compute_currency(self):
        super(ScannedVoucher, self)._compute_currency()
        if self.invoice_id.partner_id:
            if self.invoice_id.partner_id.property_purchase_currency_id:
                self.currency_id = self.invoice_id.partner_id.property_purchase_currency_id.id        

    @api.multi
    def get_purchase_references(self):
        regexs = self._get_purchase_regexs()
        purchase_orders = []
        # If no purchase orders was found, then search the hole document
        if regexs and self.raw_voucher_text:
            purchase_orders += self._find_purchase_orders(regexs, self.raw_voucher_text)
        return purchase_orders

    @api.multi
    def _find_purchase_orders(self, regexs, text_string):
        purchase_orders = set()
        ignore_characters = self._get_regex_ignore()
        for regex in regexs:
            found_purchase_orders = re.findall(regex, text_string)
            for purchase_order_ref in found_purchase_orders:
                purchase_order_ref = re.sub(ignore_characters, "", purchase_order_ref)
                purchase_orders.add(purchase_order_ref)
        return list(purchase_orders)

    @api.multi
    def _get_regex_ignore(self):
        return "|".join(SEPERATOR_CHARACTERS)

    @api.multi
    def _get_purchase_regexs(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        purchase_sequence_id = get_param('invoice_scan_purchase_sequence', default=False),
        regexs = []
        if purchase_sequence_id:
            purchase_sequence = self.env['ir.sequence'].browse(int(purchase_sequence_id[0]))
            padding = str(purchase_sequence.padding)
            actual_length = str(len(str(purchase_sequence.number_next_actual)))
            if actual_length < padding:
                actual_length = padding
            regexs +=  [r''+ purchase_sequence.prefix + '\d{' + padding + ',' + actual_length + '}']
            for character in SEPERATOR_CHARACTERS:
                regexs += [r''+ purchase_sequence.prefix + character + '\d{' + padding + ',' + actual_length + '}']
        return regexs