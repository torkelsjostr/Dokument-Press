from odoo import models, api, fields
from odoo.exceptions import UserError


class Commission(models.Model):
    _name = 'commission'

    name = fields.Char(string="Name", default="New")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    commission_struct_id = fields.Many2one('commission.structure')
    previous_commission_struct_id = fields.Many2one('commission')
    author_id = fields.Many2one('author', string="Author")
    partner_id = fields.Many2one('res.partner', related="author_id.partner_id", string="Partner")
    product_id = fields.Many2one('product.product', string="Product", domain=[('type', '=', 'product')])
    state = fields.Selection([('draft', 'Draft'), ('calculated', 'Calculated'), ('confirm', 'Confirmed'), ('paid', 'Paid'), ('cancel', 'Cancel')], default='draft')
    commission_lines = fields.One2many('commission.lines', 'line_id')
    deduction_lines = fields.One2many('commission.deductions', 'line_id')
    allowance_lines = fields.One2many('commission.allowances', 'line_id')
    total_qty = fields.Float('Total Quantity', compute='_get_total_qty')
    total_margin = fields.Monetary('Total Margin', compute='_get_total_margin')
    total_sales = fields.Monetary('Total Sales', compute='_get_total_sales')
    commission = fields.Monetary('Commission')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id,
                                  string="Currency")
    total_allowances = fields.Monetary('Total Allowances', compute='_get_total_allowances')
    total_deductions = fields.Monetary('Total Deductions', compute='_get_total_deductions')
    total_commission = fields.Monetary('Total Commission', compute='_get_total_commission')
    paid_amount = fields.Float('Paid Amount')
    paid_currency_id = fields.Many2one('res.currency', string="Paid Currency")
    payment_ids = fields.Many2many('account.payment')
    carry_forward_qty = fields.Float('Carry Forward Total')

    def open_payments(self):
        """Opening related finished product screen in Lot and  serial"""
        self.ensure_one()
        action = self.env.ref('account.action_account_payments_payable').read()[0]
        action['domain'] = [('id', '=', self.payment_ids.ids)]
        action['view_mode'] = 'form'
        return action

    @api.model
    def create(self, vals):
        return_obj = super(Commission, self).create(vals)
        return_obj.name = self.env['ir.sequence'].next_by_code('commission')
        return return_obj

    def _get_total_commission(self):
        for line in self:
            line.total_commission = line.commission + line.total_allowances - line.total_deductions

    def _get_total_allowances(self):
        for line in self:
            line.total_allowances = sum(line.allowance_lines.mapped('amount'))

    def _get_total_deductions(self):
        for line in self:
            line.total_deductions = sum(line.deduction_lines.mapped('amount'))

    def _get_total_qty(self):
        for line in self:
            line.total_qty = sum(line.commission_lines.mapped('quantity'))

    def _get_total_margin(self):
        for line in self:
            line.total_margin = sum(line.commission_lines.mapped('margin'))

    def _get_total_sales(self):
        for line in self:
            line.total_sales = sum(line.commission_lines.mapped('subtotal'))

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.author_id = self.product_id.author_id.id
        self.commission_struct_id = self.product_id.commission_structure.id

    def calculate_commission(self):
        lines = self.env['account.invoice.line'].search([('product_id', '=', self.product_id.id), ('price_subtotal', '>', 0),
                                                         ('invoice_id.state', '=', 'paid'), ('invoice_id.date_invoice', '>=', str(self.start_date))
                                                         , ('invoice_id.date_invoice', '<=', str(self.end_date)), ('commission_calculated', '=', False)])
        for line in lines:
            self.commission_lines.create({
                'account_move_line_id': line.id,
                'invoice_id': line.invoice_id.id,
                'quantity': line.quantity,
                'subtotal': line.price_subtotal_signed,
                'margin': line.product_id.standard_price * line.quantity,
                'line_id': self.id
            })
        lines.write({'commission_id': self.id})
        self.write({
            'state': 'calculated',
            'commission': self._get_commission(),
        })

    def _get_commission(self):
        if self.commission_struct_id.commission_type == 'percentage' and self.commission_struct_id.commission_base == 'gross_amount':
            return (self.total_sales * (self.commission_struct_id.commission_rate / 100))
        elif self.commission_struct_id.commission_type == 'percentage' and self.commission_struct_id.commission_base == 'fixed_amount':
            return (self.total_qty * self.commission_struct_id.commission_fixed_rate * (self.commission_struct_id.commission_rate / 100))
        elif self.commission_struct_id.commission_type == 'percentage' and self.commission_struct_id.commission_base == 'net_amount':
            return ((self.total_sales - self.total_margin) * (self.commission_struct_id.commission_rate / 100))
        elif self.commission_struct_id.commission_type == 'sections' and self.commission_struct_id.commission_base == 'fixed_amount':
            previous_total = 0
            commission = 0
            if self.previous_commission_struct_id:
                previous_total = self.previous_commission_struct_id.carry_forward_qty + self.total_qty
            count = 1
            for line in self.commission_struct_id.commission_structure_ids.filtered(lambda x: x.maximum_amount >= self.previous_commission_struct_id.carry_forward_qty).sorted(key=lambda y: y.minimum_amount):
                current_total = previous_total
                if line.maximum_amount <= (current_total or self.total_qty):
                    previous_stop = 0
                    if count == 1:
                        previous_stop = self.previous_commission_struct_id.carry_forward_qty - line.minimum_amount
                    commission += (line.rate / 100) * line.fixed_amount * (line.maximum_amount - line.minimum_amount - previous_stop)
                elif line.maximum_amount >= (current_total or self.total_qty):
                    previous_stop = 0
                    if count == 1:
                        previous_stop = self.previous_commission_struct_id.carry_forward_qty - line.minimum_amount
                    commission += (line.rate / 100) * line.fixed_amount * ((current_total or self.total_qty) - line.minimum_amount - previous_stop)
                    break
                else:
                    commission += 0
                count += 1
            return commission
        return 0

    def reset_to_draft(self):
        self.commission_lines.mapped('account_move_line_id').write({
            'commission_id': self.id
        })
        self.commission_lines.unlink()
        self.write({
            'state': 'draft',
            'commission': 0,
        })

    def confirm(self):
        if self.commission < 0:
            raise UserError("Commission amount should be greater than 0")
        self.commission_lines.mapped('account_move_line_id').write({
            'commission_calculated': True
        })
        self.write({
            'state': 'confirm',
            'carry_forward_qty': self.previous_commission_struct_id.carry_forward_qty + self.total_qty,
        })

    def set_as_paid(self):
        self.write({
            'state': 'paid'
        })

    def cancel(self):
        self.write({
            'state': 'cancel'
        })


class CommissionLines(models.Model):
    _name = 'commission.lines'

    account_move_line_id = fields.Many2one('account.invoice.line', string="Invoice Line")
    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    line_id = fields.Many2one('commission')
    quantity = fields.Float(string="Quantity")
    subtotal = fields.Monetary(string="Subtotal")
    margin = fields.Monetary(string="Margin")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id,
                                  string="Currency")


class CommissionAllowances(models.Model):
    _name = 'commission.allowances'

    name = fields.Char('Name')
    amount = fields.Monetary('Amount')
    line_id = fields.Many2one('commission')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id,
                                  string="Currency")


class CommissionDeductions(models.Model):
    _name = 'commission.deductions'

    name = fields.Char('Name')
    amount = fields.Monetary('Amount')
    line_id = fields.Many2one('commission')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id,
                                  string="Currency")
