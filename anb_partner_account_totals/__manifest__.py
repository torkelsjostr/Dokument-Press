# -*- coding: utf-8 -*-
# Copyright 2019-TODAY Juan Formoso Vasco <jfv@anuia.es>
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Partner Credit/Debit Totals',
    'summary': 'Shows the receivable and payable accounting total amounts',
    'description': """Description in HTML file.
- total
- payable
- receivable
- total payable / payable total
- total receivable / receivable total
- amount
- total amount / amount total
- total debit / debit total
- total credit / credit total
- amount credit / credit amount
- debit / credit
- total in partner / amount in partner
- receivable in partner / payable in partner
""",
    'category': 'Accounting',
    'version': '12.0.0.1',
    'author': 'Anubía Soluciones en la Nube, S.L.',
    'maintainer': 'Anubía Soluciones en la Nube, S.L.',
    'contributors': [
        'Juan Formoso Vasco <jfv@anubia.es>',
    ],
    'website': 'http://www.anubia.es',
    'depends': [
        'account',
    ],
    'data': [
        'views/partner_view.xml',
    ],
    'demo': [],
    'test': [],
    'images': [
        'static/description/main_screenshot.png',
        'static/description/main_1.png',
        'static/description/main_2.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 0,
    'currency': 'EUR',
}
