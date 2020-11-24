# -*- coding: utf-8 -*-
##############################################################################
#
#       Copyright © SUREKHA TECHNOLOGIES PRIVATE LIMITED, 2019.
#
#       You can not extend,republish,modify our code,app,theme without our
#       permission.
#
#       You may not and you may not attempt to and you may not assist others
#       to remove, obscure or alter any intellectual property notices on the
#       Software
#
##############################################################################

{
    'name': 'Dynamic List',
    'version': '12.0.0.1',
    'author': 'Surekha Technologies Pvt. Ltd.',
    'category': 'Dynamic ListView',
    'website': 'https://www.surekhatech.com',
    'summary': 'Dynamic List',
    'description': """

Dynamic List
============
Dynamic List module is made to show/hide the column(s) on the list/tree view of ODOO. After installing the module a "Select Columns" button will be show to the list view before the pagination.

    """,
    'images': ['images/dynamiclist_homepage.png'
               ],
    'depends': ['web'],
    'data': [
        'views/listview_button.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': ['static/src/xml/listview_button_view.xml'],
    'license': 'Other proprietary'
}
