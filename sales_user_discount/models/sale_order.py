# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018-Today Ascetic Business Solution <www.asceticbs.com>
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

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        super(SaleOrderLine, self)._onchange_discount()
        for record in self:
            allow_discount = self.env['ir.model.access'].check_groups("sale.group_discount_per_so_line")
            if record.product_id and record.order_partner_id.id and allow_discount:
                user_lines = self.env['user.partner.discount'].sudo().search([('partner_id', '=', record.order_partner_id.id),('user_id', '=', self.env.user.id)])
                if user_lines:
                    partner_discount_obj = user_lines[0]
                    discount = partner_discount_obj.discount
                    record.discount = discount


