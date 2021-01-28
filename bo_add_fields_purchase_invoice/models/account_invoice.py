# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    tax_adjustment = fields.Float(
        string='Ajuste de Impuesto'
    )
    other_discount = fields.Float(
        string='Otros Descuentos'
    )

    @api.one
    @api.depends('tax_adjustment', 'other_discount')
    def _compute_amount(self):
        # super(AccountInvoice, self)._amount_all()
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax + self.tax_adjustment + self.other_discount
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id
            amount_total_company_signed = currency_id._convert(
                self.amount_total,
                self.company_id.currency_id,
                self.company_id,
                self.date_invoice or fields.Date.today()
            )
            amount_untaxed_signed = currency_id._convert(
                self.amount_untaxed,
                self.company_id.currency_id,
                self.company_id,
                self.date_invoice or fields.Date.today()
            )
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if self.purchase_id:
            self.tax_adjustment = self.purchase_id.tax_adjustment
            self.other_discount = self.purchase_id.other_discount
            self.date_invoice = fields.Datetime.to_string(self.purchase_id.date_order)
        return super(AccountInvoice, self).purchase_order_change()

    @api.onchange('amount_total')
    def _onchange_amount_total(self):
        if self.tax_adjustment or self.other_discount:
            pass
        else:
            return super(AccountInvoice, self)._onchange_amount_total()

    @api.multi
    def action_invoice_open(self):
        obj_account = self.env['account.account']
        count_tax_adjustment = obj_account.search_count([('is_tax_adjustment', '=', True)])
        count_other_discount = obj_account.search_count([('is_other_discount', '=', True)])
        if self.tax_adjustment and not count_tax_adjustment:
            raise UserError("Debe Asignar una cuenta para Ajuste de Impuesto")
        if self.other_discount and not count_other_discount:
            raise UserError("Debe Asignar una cuenta para Otros Descuentos")
        return super(AccountInvoice, self).action_invoice_open()

    @api.model
    def tax_line_move_line_get(self):
        res = super(AccountInvoice, self).tax_line_move_line_get()
        if self.tax_adjustment:
            tax_adjustment_account_id = self.env['account.account'].search([('is_tax_adjustment', '=', True)], limit=1)
            res.append({
                'type': 'src',
                'name': "Ajuste de Immpuesto",
                'price_unit': self.tax_adjustment,
                'quantity': 1,
                'price': self.tax_adjustment,
                'account_id': tax_adjustment_account_id.id,
                'invoice_id': self.id,
            })

        if self.other_discount:
            other_discount_account_id = self.env['account.account'].search([('is_other_discount', '=', True)], limit=1)
            res.append({
                'type': 'src',
                'name': "Otros Descuentos",
                'price_unit': self.other_discount,
                'quantity': 1,
                'price': self.other_discount,
                'account_id': other_discount_account_id.id,
                'invoice_id': self.id,
            })

        return res
