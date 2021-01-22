# -*- coding: utf-8 -*-
#Vanneri
{
    'name': "SO Delivery Status",

    'summary': """
        Invoice and delivery status in SO Line""",

    'description': """
        Easly we can track line wise invocie and delivery status
    """,

    'author': "VaNnErI",
    'license': "LGPL-3",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '12.0.2',

    # any module necessary for this one to work correctly
    'depends': ['sale_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale.xml',
        # 'views/product.xml',
        'views/templates.xml',
    ],
   'images': ['static/description/Banner.jpg'],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False
}