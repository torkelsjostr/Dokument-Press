from odoo import models, fields, api

class PickingTotalQty(models.Model):
    _inherit = 'sale.order'

    tot_sale_qty = fields.Float(compute='_calculate_sale_qty', string='Total Sale Quantity', help="Total sale quantity in active document")
    tot_delivered_qty = fields.Float(compute='_calculate_delivered_qty', string='Total Delivered Quantity',
                                help="Total Delivered quantity in active document")
    tot_invoiced_qty = fields.Float(compute='_calculate_invoiced_qty', string='Total Invoiced Quantity',
                                help="Total Invoiced quantity in active document")

    def _calculate_sale_qty(self):
        for rs in self:
            sumqty = 0
            for line in rs.order_line:
                sumqty += line.product_uom_qty
        rs.tot_sale_qty = sumqty

    def _calculate_delivered_qty(self):
        for rs in self:
            sumqty = 0
            for line in rs.order_line:
                sumqty += line.qty_delivered
        rs.tot_delivered_qty = sumqty

    def _calculate_invoiced_qty(self):
        for rs in self:
            sumqty = 0
            for line in rs.order_line:
                sumqty += line.qty_invoiced
        rs.tot_invoiced_qty = sumqty

