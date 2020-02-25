# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class inherit_purchase(models.Model):
	_inherit = "purchase.order"
	
	check_partially_delivery = fields.Boolean(string="Partially Shipped",readonly=1,copy=False)
	check_fully_delivery = fields.Boolean(string="Fully Shipped",readonly=1,copy=False)
	check_partially_paid = fields.Boolean(string="Partially Paid",readonly=1,copy=False)
	check_fully_paid = fields.Boolean(string="Fully Paid",readonly=1,copy=False)

class inherit_stock_picking(models.Model):
	_inherit = "stock.picking"

	pick_bool = fields.Boolean(string="demo bool",compute="_compute_purchase_fully_picking",store=True)

	@api.multi
	@api.depends("move_ids_without_package.quantity_done")
	def _compute_purchase_fully_picking(self):
		
		for i in self:
			purchase_order = i.env['purchase.order'].search([])
			for j in purchase_order:
				if j.name == i.origin:
					counter_qty = 0.0
					main_qty = 0.0

					for ids in j.picking_ids:
						for lines in ids.move_ids_without_package:
							counter_qty += lines.quantity_done

					for main in j.order_line:
						main_qty += main.product_qty

					if counter_qty > 0.0:

						if counter_qty < main_qty:
							j.write({
								"check_partially_delivery":True
									})

						if counter_qty == main_qty:
							j.write({
								"check_fully_delivery":True,
								"check_partially_delivery":False
									})

					i.pick_bool = True 

class inherit_invoicing(models.Model):
	_inherit = "account.invoice"

	invoice_bool = fields.Boolean(string="demo bool",compute="_compute_purchase_invoice",store=True)

	@api.depends("residual")
	def _compute_purchase_invoice(self):
	
		for i in self:
			purchase_order = i.env['purchase.order'].search([])
			for j in purchase_order:
				
				if j.name == i.origin:

					for ids in j.invoice_ids:

						if ids.residual > 0 and ids.residual < ids.amount_total:
							j.write({
								"check_partially_paid":True
									})

						if ids.state == "paid":
							j.write({
								"check_partially_paid":False,
								"check_fully_paid":True
									})
					i.invoice_bool = True
