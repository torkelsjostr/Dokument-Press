# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2019-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    total_purchase_product = fields.Integer(string='Total Products:',compute='_total_purchase_product',help="total Products")
    total_purchase_quantity = fields.Integer(string='Total Quantities:',compute='_total_purchase_product_qty',help="total Quantity")

    def _total_purchase_product(self):
        for record in self:
            list_of_product=[]
            for line in record.order_line:
                list_of_product.append(line.product_id)
            record.total_purchase_product = len(set(list_of_product))

    def _total_purchase_product_qty(self):
        for record in self:
            total_qty = 0
            for line in record.order_line:
                total_qty = total_qty + line.product_qty
            record.total_purchase_quantity = total_qty
