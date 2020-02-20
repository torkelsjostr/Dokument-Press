# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProductProduct(models.Model):
    _inherit = "product.product"

    count_invoice_qty  =  fields.Integer('Invoice Quantity', compute='_count_incoming_invoice_qty')
    count_incoming_invoice_qty  =  fields.Integer('Incoming Invoice Qty', compute='_count_incoming_invoice_qty')
    count_invoice_amount  =  fields.Float('Invoice Amount', compute='_count_invoice_amount')
    count_incoming_invoice_amount  =  fields.Float('Incoming Invoice Amount', compute='_count_invoice_amount')

    @api.multi
    def _count_incoming_invoice_qty(self):
        for product in self:
            incoming_invoice_qty = self.env['account.invoice.line'].search([('product_id','=',self.id)])
            customer_count = 0
            vendor_count = 0
            for invoice_qty in incoming_invoice_qty:
                if invoice_qty.invoice_id.type == "out_invoice" or  invoice_qty.invoice_id.type == "in_refund":
                    customer_count += invoice_qty.quantity
                else:
                    vendor_count += invoice_qty.quantity
            product.count_invoice_qty = int(customer_count)
            product.count_incoming_invoice_qty = int(vendor_count)

    @api.multi
    def invoice_qty_button(self):
	    self.ensure_one()
	    return {
			'name': 'Invoice Lines',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'account.invoice.line',
			'domain': [('product_id','=',self.id),('invoice_id.type','in',['out_invoice','in_refund'])],
		}

    @api.multi
    def incoming_invoice_qty_button(self):
        self.ensure_one()
        return {
            'name': 'Incoming Invoice Lines',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice.line',
            'domain': [('product_id','=',self.id),('invoice_id.type','in',['in_invoice','out_refund'])],
        }

    @api.multi
    def _count_invoice_amount(self):
        for product in self:
            invoice_amount = self.env['account.invoice.line'].search([('product_id','=',self.id)])
            customer_count = 0.0
            vendor_count = 0.0
            for amount in invoice_amount:
                if amount.invoice_id.type == "out_invoice" or amount.invoice_id.type == "in_refund":
                    customer_count += amount.price_subtotal
                else:
                    vendor_count += amount.price_subtotal
            product.count_invoice_amount = customer_count
            product.count_incoming_invoice_amount = vendor_count

    @api.multi
    def invoice_amount_button(self):
        self.ensure_one()
        return {
			'name': 'Invoice Amount',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'account.invoice.line',
			'domain': [('product_id','=',self.id),('invoice_id.type','in',['out_invoice','in_refund'])],
		}

    @api.multi
    def incoming_invoice_amount_button(self):
        self.ensure_one()
        return {
            'name': 'Incoming Invoice Amount',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice.line',
            'domain': [('product_id','=',self.id),('invoice_id.type','in',['in_invoice','out_refund'])],
        }

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: