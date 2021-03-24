# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	total_weight = fields.Float(string="Total Weight",compute='_total_weight_')

	@api.multi
	def _total_weight_(self):
		total = 0
		for order_line_id in self.order_line:
			total += order_line_id.weight
		self.total_weight = total

class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'

	weight = fields.Float(string="Weight")

	@api.onchange('price_subtotal')
	def _onchange_product_quantity(self):
		product_weight = self.product_id.weight
		quantity = self.product_uom_qty
		if not self.product_uom.factor == 0:
			if not self.product_uom.uom_type == "reference":
				quantity = quantity / self.product_uom.factor

		self.weight =product_weight * quantity
