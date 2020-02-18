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
from odoo import api,fields,models,_

class Warehouse(models.Model):
    _inherit="stock.warehouse"
 
    warehouse_product_ids = fields.One2many('stock.quant','location_id',string='Available Products',compute='compute_warehouse_products')

    @api.multi
    def compute_warehouse_products(self):
        for products in self:
            warehouse_all_products = self.env['stock.quant'].search([('location_id', 'child_of', self.code)])
            for i in warehouse_all_products:	
                products.warehouse_product_ids = warehouse_all_products
	    
	
