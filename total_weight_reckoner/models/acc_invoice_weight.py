from odoo import models, fields, api

class InvoiceWeight(models.Model):

   _inherit = 'account.invoice.line'

   in_weight = fields.Float(string='Gross Weight',
                               store=True,
                               related='product_id.weight')
   # in_net_weight = fields.Float(string='Net Weight',
   #                             store=True,
   #                             related='product_id.weight_net')
   in_quantity = fields.Float(string='Quantity',
                               store=True,
                               related='quantity')

class InvoiceWeightOrder(models.Model):
  
    _inherit = 'account.invoice'
    @api.depends('invoice_line_ids.in_weight')
    @api.depends('invoice_line_ids.in_quantity')
    # @api.depends('invoice_line_ids.in_net_weight')
    def _calcweight(self):
        currentweight = 0
        for invoice_line in self.invoice_line_ids:
            currentweight = currentweight + (invoice_line.in_weight * invoice_line.in_quantity)

        self.in_weight_total = currentweight

    in_weight_total = fields.Float(compute='_calcweight', string='Total Gross Weight')

    # def _calcweight_net(self):
    #     currentweight_net = 0
    #     for invoice_line in self.invoice_line_ids:
    #         currentweight_net = currentweight_net + (invoice_line.in_net_weight * invoice_line.in_quantity)

    #     self.in_net_weight_total = currentweight_net

    # in_net_weight_total = fields.Float(compute='_calcweight_net', string='Total Net Weight')