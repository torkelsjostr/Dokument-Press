# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017-TODAY Aurium Technologies(<http://www.auriumtechnologies.com>).
#    Author: Jalal ZAHID, Aurium Technologies (<http://www.auriumtechnologies.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Update product cost on vendor bill",
    'summary': """This module udate product cost price on vendor bill validation. 
               Don't use this module if you use Odoo's dsfault costing methods     
               """,
    'version': '12.0.1.0.0',
    'description': """
       Update cost from purchase invoice
    """,
    'author': 'Jalal ZAHID',
    'company': 'Aurium Technologies',
    'website': "http://www.auriumtechnologies.com",
    'category': 'product',
    'depends': ['base', 'account'],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
