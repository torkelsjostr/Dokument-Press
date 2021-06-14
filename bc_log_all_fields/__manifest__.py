# -*- coding: utf-8 -*-
{
    'name': "Log All Fields",

    'summary': """log all fields changed in chatter.""",

    'description': """
        track all fields changes in chatter
    """,

    'author': "kevinkong",
    'website': "https://github.com/block-cat",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ]
}