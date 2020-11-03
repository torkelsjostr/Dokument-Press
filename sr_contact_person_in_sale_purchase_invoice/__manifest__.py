# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': "Contact Person in Sale, Purchase and Invoice Orders",
    'version': "12.0.0.0",
    'summary': "Contact Person in Sale, Purchase and Invoice Orders",
    'category': 'Extra Addons',
    'description': """
    Contact person in sale order
    Contact person in purchase order
    Contact person in invoice order
    Contact person in sale order report
    Contact person in invoice order report
    Contact person in purchase order report
    
    Alternet contact in sale order
    Alternet contact in purchase order
    Alternet contact in invoice order
    Alternet contact in sale order report
    Alternet contact in invoice order report
    Alternet contact in purchase order report
    
    reference contact in sale order
    reference contact in purchase order
    reference contact in invoice order
    reference contact in sale order report
    reference contact in invoice order report
    reference contact in purchase order report
    
    inherit sale.order
    inherit account.move
    inherit purchase.order
    
    """,
    'author': "Sitaram",
    'website':"www.sitaramsolutions.in",
    'depends': ['base','sale','account','purchase'],
    'data': [
        'views/sr_inherited_sale_order.xml',
        'views/sr_inherited_invoice_order.xml',
        'views/sr_inherited_purchase_order.xml',
        'reports/sr_inherited_sale_order_report.xml',
        'reports/sr_inherited_invoice_order_report.xml',
        'reports/sr_inherited_purchase_order_report.xml'
    ],
    'demo': [],
    "external_dependencies": {},
    "license": "AGPL-3",
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/aEc1a6rOhv4',
    'images': ['static/description/banner.png'],
}
