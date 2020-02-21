from odoo import models, fields, api

class SaleWeight(models.Model):

   _inherit = 'sale.order.line'

   so_weight = fields.Float(string='Gross Weight',
                               store=True,
                               related='product_id.weight')
   # so_net_weight = fields.Float(string='Net Weight',
   #                             store=True,
   #                             related='product_id.weight_net')
   so_quantity = fields.Float(string='Quantity',
                               store=True,
                               related='product_uom_qty')

class SaleWeightOrder(models.Model):

    _inherit = 'sale.order'
    @api.depends('order_line.so_weight')
    # @api.depends('order_line.so_net_weight')
    @api.depends('order_line.so_quantity')
    def _calcweight(self):
        currentweight = 0
        for order_line in self.order_line:
            currentweight = currentweight + (order_line.so_weight * order_line.so_quantity)

        self.so_weight_total = currentweight

    so_weight_total = fields.Float(compute='_calcweight', string='Total Gross Weight')

    # def _calcweight_net(self):
    #     currentweight_net = 0
    #     for order_line in self.order_line:
    #         currentweight_net = currentweight_net + (order_line.so_net_weight * order_line.so_quantity)

    #     self.so_net_weight_total = currentweight_net

    # so_net_weight_total = fields.Float(compute='_calcweight_net', string='Total Net Weight')
