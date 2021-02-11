# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
{
    'name': "Invoice Scan (Full Automatic Vendor Bill Flow)",
    'version': '1.4.0',
    'author': "Niova IT",
    'category': 'Accounting',
    'website': 'niova.dk',
    'summary': 'Invoice Scan automatically scans all relevant data from documents with high accuracy, so digitalization of your Vendor Bill workflow in Odoo becomes complete.',
    'demo': [],
    'depends': ['base_setup', 'account', 'document'],
    'description': """Invoice Scan automatically scans all relevant data from documents with high accuracy, so digitalization of your Vendor Bill workflow in Odoo becomes complete.""",
    'data': [
        'security/invoice_scan_security.xml',
        'security/ir.model.access.csv',
        'data/invoicescan_data.xml',
        'data/ir_crone_data.xml',
        'data/mail_data.xml',
        'data/mail_template_data.xml',
        'wizard/account_invoice_change_company_view.xml',
        'wizard/account_invoice_change_type_view.xml',
        'wizard/account_invoice_control_view.xml',
        'wizard/invoice_scan_activation_view.xml',
        'wizard/invoice_scan_debitor_view.xml',
        'wizard/invoice_scan_download_view.xml',
        'wizard/invoice_scan_support_view.xml',
        'wizard/invoice_scan_upload_view.xml',
        'views/account_invoice_views.xml',
        'views/assets.xml',
        'views/invoice_scan_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/invoice_scan_menuitem.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'qweb': [
        "static/src/xml/account_invoice.xml"
    ],
    'installable': True,
    'application': True,
    "license":"OPL-1"
}