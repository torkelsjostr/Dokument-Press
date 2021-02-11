# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova IT ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova IT ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
{
    'name': "Purchase Order Matching (Invoice Scan)",
    'version': '1.0.2',
    'author': "Niova IT",
    'category': 'Generic Modules',
    'website': 'niova.dk',
    'summary': 'This module is an addon to the Invoice-Scan module. The module auto apply purchase orders to the scanned vendor bills.',
    'demo': [],
    'depends': ['niova_invoice_scan', 'purchase'],
    'description': """This module is an addon to the Invoice-Scan module. The module auto apply purchase orders to the scanned vendor bills.""",
    'data': ['views/account_invoice_views.xml',
             'views/res_config_settings_views.xml',
             'views/res_partner_views.xml'],
    'installable': True,
    'application': False,
    "license":"OPL-1"
}