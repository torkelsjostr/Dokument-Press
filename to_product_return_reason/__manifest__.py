# -*- coding: utf-8 -*-

{
    'name' : 'Product Return Reasons',
    'version': '1.0.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': 'https://v12demo-int.erponline.vn',
    'support': 'apps.support@viindoo.com',
    'summary': 'Base application for product return reasons management',
    'sequence': 30,
    'category': 'Sales',
    'description':"""
Summary
=======

This technical module offers a new model for users to define return reason. A return reason consists of the following information:

1. Name: The name of the Return Reason, for example: Bad quality, Customer changed mind, etc
2. Description: Description of the reason

NOTES
-----
This module does nothing. It aims to provide the base for other applications to extend. See

* Stock Return Reasons: https://apps.odoo.com/apps/modules/12.0/to_product_return_reason_stock/
* Point of Sales Return Reasons: https://apps.odoo.com/apps/modules/12.0/to_product_return_reason_pos/

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'depends': ['product'],
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/products_return_reason.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
