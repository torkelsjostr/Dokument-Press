# -*- coding: utf-8 -*-

{
    # Theme information
    'name': 'ADD Fields in purchase and invoice models',
    'category': 'purchase',
    'version': '1.0',
    'summary': 'ADD Fields in purchase and invoice models',
    'description': """ADD Fields in purchase and invoice models""",
    # 'license': 'OPL-1',
    'depends': [
        'account',
        'purchase',
    ],
    'data': [
        'views/account_account_view.xml',
        'views/purchase_order_view.xml',
        'views/account_invoice_view.xml',
    ],
    'author': 'Bitodoo',
    'website': 'http://www.bitodoo.com',
    'installable': True,
    'application': True,
}
