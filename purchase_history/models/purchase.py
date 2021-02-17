# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018-today Ascetic Business Solution <www.asceticbs.com>
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

from odoo import api, models, fields

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    last_price1 = fields.Float('Last Purchase Price 1', help="Shows the last purchase price of the product for selected supplier from the Past two Purchase order")
    last_price2 = fields.Float('Last Purchase Price 2', help="Shows the second last purchase price of the product for selected supplier from the Past two Purchase order")

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(PurchaseOrderLine, self).onchange_product_id()
        result = {}
        last_price1 = 0.0
        last_price2 = 0.0
        for record in self:
            line_ids = []
            if record.product_id:
                purchase_lines = self.env['purchase.order.line'].sudo().search([('partner_id', '=', record.partner_id.id),('product_id', '=', record.product_id.id),('order_id.state','in',('purchase','done'))])
                if purchase_lines:
                    for lines in purchase_lines:
                        line_ids.append(lines.id)
            final_list = sorted(line_ids, key=int, reverse=True)
            if len(final_list)>=1:
                last_price1 = self.env['purchase.order.line'].sudo().browse(final_list[0])
                record.last_price1 = last_price1.price_unit
            if len(final_list)>=2:
                last_price2 = self.env['purchase.order.line'].sudo().browse(final_list[1])
                record.last_price2 = last_price2.price_unit










