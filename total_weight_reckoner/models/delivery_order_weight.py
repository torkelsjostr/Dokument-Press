from odoo import models, fields, api

class SaleWeight(models.Model):

   _inherit = 'stock.move'

   do_weight = fields.Float(string='Gross Weight',
                             store=True,
                               related='product_id.weight')
   # do_net_weight = fields.Float(string='Net Weight',
   #                             store=True,
   #                             related='product_id.weight_net')
   do_quantity = fields.Float(string='Quantity',
                               store=True,
                               related='product_uom_qty')

class SaleWeightOrder(models.Model):

    _inherit = 'stock.picking'
    @api.depends('move_lines.do_weight')
    # @api.depends('move_lines.do_net_weight')
    @api.depends('move_lines.do_quantity')
    def _calcweight(self):
        currentweight = 0
        for move_lines in self.move_lines:
            currentweight = currentweight + (move_lines.do_weight * move_lines.do_quantity)

        self.do_weight_total = currentweight

    do_weight_total = fields.Float(compute='_calcweight', string='Total Gross Weight')

    # def _calcweight_net(self):
    #     currentweight_net = 0
    #     for move_lines in self.move_lines:
    #         currentweight_net = currentweight_net + (move_lines.do_net_weight * move_lines.do_quantity)

    #     self.do_net_weight_total = currentweight_net

    # do_net_weight_total = fields.Float(compute='_calcweight_net', string='Total Net Weight')
