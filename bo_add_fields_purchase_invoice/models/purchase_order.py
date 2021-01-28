# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tax_adjustment = fields.Float(
        string='Ajuste de Impuesto'
    )
    other_discount = fields.Float(
        string='Otros descuentos'
    )

    @api.depends('tax_adjustment', 'other_discount')
    def _amount_all(self):
        # super(PurchaseOrder, self)._amount_all()
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax + self.tax_adjustment + self.other_discount,
            })

    @api.multi
    def action_view_invoice(self):
        res = super(PurchaseOrder, self).action_view_invoice()
        if res.get('context'):
            res['context'].update(
                default_tax_adjustment=self.tax_adjustment,
                default_other_discount=self.other_discount,
                default_date_invoice=self.date_order
            )
        return res
