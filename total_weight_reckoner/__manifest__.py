# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright © 2016 Techspawn Solutions. (<https://techspawn.com>).
#    Copyright (C) 2004-2016 OpenERP S.A. (<http://www.odoo.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Total Weight Reckoner",

    'summary': """
        Calculates Total Gross Weight and Total Net Weight.
        """,

    'description': """
        Total Weight Reckoner will calculate the total Gross Weight and Net Weight of every product in the order line and invoice lines.
        """,

    'author': "Techspawn Solutions",
    'website': "https://techspawn.com",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['base', 'sale', 'account', 'purchase', 'stock', 'sale_stock' ,'stock_account',],
    'images': [
        'images/main.jpg',
    ],
    'data': [
        'views/sale_order_weight.xml',
        'views/purchase_order_weight.xml',
        'views/acc_invoice_weight.xml',
        'views/delivery_order_weight.xml',
    ],
}
