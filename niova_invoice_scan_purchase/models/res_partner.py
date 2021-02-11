# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova IT ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova IT ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class Partner(models.Model):
    _inherit = 'res.partner'

    # Automation
    property_invoice_automation_purchase = fields.Boolean(string='Match Purchase Orders With Vendor Bills',
                                                     default=False,
                                                     company_dependent=True,
                                                     help="Activate the use of purchase order lines if orders are found. If no orders are found, the normal behaviour will be used.")