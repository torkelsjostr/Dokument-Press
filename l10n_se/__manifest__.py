# -*- coding: utf-8 -*-
{
    'name': 'Swedish - Accounting',
    'summary': """Swedish chart of account EU BAS2017""",
    'description': """
This is the module to manage the accounting chart for Sweden in Odoo.
==============================================================================

Install some swedish chart of accounts.
    """,
    'author': 'Linserv AB',
    'website': 'https://www.linserv.se',
    'category': 'Localization/Account Charts',
    'version': '11.0.0.1',
    'depends': [
        'account',
    ],
    'data': [
        'data/account_chart.xml',
        'data/account_tax.xml',
        'data/account_fiscal.xml',
        # 'static/yml/account_chart_template.yml',
    ],
    'installable': True,
}
