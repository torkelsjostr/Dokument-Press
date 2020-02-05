# -*- coding: utf-8 -*-
# Copyright 2019 Linescripts Softwares (<http://www.linescripts.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Add Columns Dynamically",

    'summary': """
        Add Columns in the existing Tree View
        """,

    'description': """
        A dropdown provides a list of column names. On selection of any column name, the respective 
        Column will be added into the respective tree view. 
    """,

    'author': "Linescripts Softwares",
    'website': "http://www.linescripts.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Utility',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/wizard.xml',
        'views/templates.xml',
    ],

    'qweb': ['static/src/xml/add_button.xml'],
    'images': ['static/description/banner.png'],
}