from odoo import models, api, fields
from odoo.exceptions import UserError
from datetime import date


class Commission(models.Model):
    _name = 'commission'

    name = fields.Char(string="Name", default="New")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    commission_struct_id = fields.Many2one('commission.structure', string="Commission Structure", related='commission_plan_id.commission_structure')
    previous_commission_struct_id = fields.Many2one('commission')
    commission_plan_id = fields.Many2one('commission.plan', string="Royalty Configuration")
    author_id = fields.Many2one('commission.authors', string="Author", related='commission_plan_id.author_id')
    partner_id = fields.Many2one('res.partner', string="Partner", related='author_id.partner_id')
    product_id = fields.Many2one('product.product', string="Product", domain=[('type', '=', 'product')], related='commission_plan_id.product_id')
    state = fields.Selection([('draft', 'Draft'), ('calculated', 'Calculated'), ('confirm', 'Confirmed'), ('vendor_bill', 'Vendor Bill'), ('paid', 'Paid'), ('cancel', 'Cancel')], default='draft')
    commission_lines = fields.One2many('commission.lines', 'line_id')
    deduction_lines = fields.One2many('commission.deductions', 'line_id')
    allowance_lines = fields.One2many('commission.allowances', 'line_id')
    total_qty = fields.Float('Total Quantity', compute='_get_total_qty')
    total_margin = fields.Monetary('Total Margin', compute='_get_total_margin')
    total_sales = fields.Monetary('Total Sales', compute='_get_total_sales')
    commission = fields.Monetary('Commission')
    currency_id = fields.Many2one('res.currency', related='commission_struct_id.currency_id',
                                  string="Currency")
    company_currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id,
                                  string="Company Currency")

    exchange_rate_date = fields.Date(string="Exchange Rate Date", default=fields.Date.context_today, required=True)
    total_allowances = fields.Monetary('Total Allowances', compute='_get_total_allowances')
    total_deductions = fields.Monetary('Total Deductions', compute='_get_total_deductions')
    total_commission = fields.Monetary('Total Commission', compute='_get_total_commission')
    company_commission = fields.Monetary('Commission', compute='_get_company_total_commission')
    paid_amount = fields.Float('Paid Amount')
    paid_currency_id = fields.Many2one('res.currency', string="Paid Currency")
    payment_ids = fields.Many2many('account.payment')
    carry_forward_qty = fields.Float('Carry Forward Total')
    invoice_id = fields.Many2one('account.invoice', string="Vendor Bill")
    previous_stop = fields.Many2one('commission.structure.lines', string="Vendor Bill")

    def create_vendor_bill(self):
        """Creating a vendor bill for the author and loading the vendor bill"""
        purchase_journal = self.env['account.journal'].sudo().search([('type', '=', 'purchase')])
        if not purchase_journal:
            raise UserError("Please setup a Journal for Vendor Bills(Type=Purchase).")
        if not self.partner_id:
            raise UserError("Please create a partner for the Author.")
        account_val = {
            'partner_id': self.partner_id.id,
            'date_invoice': date.today(),
            'type': 'in_invoice',
            'commission_id': self.id,
            'invoice_line_ids': [],
            'currency_id': self.currency_id.id,
            'journal_id': purchase_journal.id
        }
        account_val['invoice_line_ids'].append((0, 0, {
            'name': "Commission of " + self.name,
            'quantity': 1,
            'price_unit': self.total_commission,
            'account_id': purchase_journal.default_debit_account_id.id,
        }))
        record = self.env['account.invoice'].create(account_val)
        self.write({
            'invoice_id': record.id,
            'state': 'vendor_bill'
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'target': 'current',
            'res_id': record.id,
        }

    def open_vendor_bill(self):
        """Opening related finished product screen in Lot and  serial"""
        self.ensure_one()
        action = self.env.ref('account.action_vendor_bill_template').read()[0]
        action['domain'] = [('id', '=', self.invoice_id.id)]
        action['view_mode'] = 'form'
        return action

    @api.model
    def create(self, vals):
        """Creating sequence"""
        return_obj = super(Commission, self).create(vals)
        return_obj.name = self.env['ir.sequence'].next_by_code('commission')
        return return_obj

    def _get_total_commission(self):
        """Calculating final total of commission"""
        for line in self:
            line.total_commission = line.commission + line.total_allowances - line.total_deductions

    @api.depends('total_commission')
    def _get_company_total_commission(self):
        """Calculating Commission in company currency"""
        for line in self:
            line.company_commission = line.currency_id.with_context(date=line.exchange_rate_date).compute(line.total_commission, line.company_currency_id) if line.currency_id.id != line.company_currency_id.id else line.total_commission

    def _get_total_allowances(self):
        """Calculating total of allowances"""
        for line in self:
            line.total_allowances = sum(line.allowance_lines.mapped('amount'))

    def _get_total_deductions(self):
        """Calculating total of deductions"""
        for line in self:
            line.total_deductions = sum(line.deduction_lines.mapped('amount'))

    def _get_total_qty(self):
        """Calculating total of quantity"""
        for line in self:
            line.total_qty = sum(line.commission_lines.mapped('quantity'))

    def _get_total_margin(self):
        """Calculating total margin"""
        for line in self:
            line.total_margin = sum(line.commission_lines.mapped('margin'))

    def _get_total_sales(self):
        """Calculating total sales"""
        for line in self:
            line.total_sales = sum(line.commission_lines.mapped('subtotal'))

    def calculate_commission(self):
        """Calculating commissions, advances, and deductions"""
        lines = self.env['account.invoice.line'].search([('product_id', '=', self.product_id.id),
                                                         ('price_subtotal', '>', 0),
                                                         ('invoice_id.state', 'in', ['open']),
                                                         ('invoice_id.date_invoice', '>=', str(self.start_date)),
                                                         ('invoice_id.date_invoice', '<=', str(self.end_date)),
                                                         ('invoice_id.type', '=', 'out_invoice')])
        # getting eligible invoice lines and filtering them.
        default_deduction_lines = self.commission_plan_id.deduction_ids.filtered(lambda x: self.start_date <= x.date <= self.end_date and x.commission_id.id == False)
        default_allowance_lines = self.commission_plan_id.allowance_ids.filtered(lambda x: self.start_date <= x.date <= self.end_date and x.commission_id.id == False)
        lines = lines.filtered(lambda x: self.author_id.id not in x.author_ids.ids)
        for line in lines:
            self.commission_lines.create({
                'account_move_line_id': line.id,
                'invoice_id': line.invoice_id.id,
                'quantity': line.quantity,
                'subtotal': line.price_subtotal_signed,
                'margin': line.product_id.standard_price * line.quantity,
                'line_id': self.id
            })
        for ded in default_deduction_lines:
            self.deduction_lines.create({
                'name': ded.name,
                'amount': ded.amount,
                'line_id': self.id
            })
        for all in default_allowance_lines:
            self.allowance_lines.create({
                'name': all.name,
                'amount': all.amount,
                'line_id': self.id
            })
        default_deduction_lines.write({'commission_id': self.id})
        default_allowance_lines.write({'commission_id': self.id})
        lines.write({'author_ids': [(4, self.author_id.id)]})
        self.write({
            'state': 'calculated',
            'commission': self._get_commission(),
        })

    def _get_commission(self):
        """Calculating commissions according to the equations and returning amounts"""
        self._get_total_sales()
        if self.commission_struct_id.commission_type == 'percentage' and self.commission_struct_id.commission_base == 'gross_amount':
            return (self.total_sales * (self.commission_struct_id.commission_rate / 100))
        elif self.commission_struct_id.commission_type == 'percentage' and self.commission_struct_id.commission_base == 'fixed_amount':
            return (self.total_qty * self.commission_struct_id.commission_fixed_rate * (self.commission_struct_id.commission_rate / 100))
        elif self.commission_struct_id.commission_type == 'percentage' and self.commission_struct_id.commission_base == 'net_amount':
            return ((self.total_sales - self.total_margin) * (self.commission_struct_id.commission_rate / 100))
        elif self.commission_struct_id.commission_type == 'sections' and self.commission_struct_id.commission_base == 'fixed_amount':
            previous_total = 0
            commission = 0
            previous_commission_obj = None
            if self.previous_commission_struct_id:
                previous_total = self.previous_commission_struct_id.carry_forward_qty + self.total_qty
                previous_commission_obj = self.previous_commission_struct_id.previous_stop
            count = 1
            for line in self.commission_struct_id.commission_structure_ids.filtered(lambda x: x.maximum_amount >= self.previous_commission_struct_id.carry_forward_qty).sorted(key=lambda y: y.minimum_amount):
                current_total = previous_total
                if previous_commission_obj:
                    self.write({'previous_stop': previous_commission_obj.id})
                if line.maximum_amount <= (current_total or self.total_qty):
                    previous_stop = 0
                    if count == 1:
                        previous_stop = self.previous_commission_struct_id.carry_forward_qty - line.minimum_amount
                    commission += (line.rate / 100) * line.fixed_amount * (line.maximum_amount - line.minimum_amount - previous_stop)
                elif line.maximum_amount >= (current_total or self.total_qty):
                    previous_stop = 0
                    if count == 1:
                        previous_stop = self.previous_commission_struct_id.carry_forward_qty - (self.previous_stop.maximum_amount)
                    commission += (line.rate / 100) * line.fixed_amount * ((current_total or self.total_qty) - previous_commission_obj.maximum_amount - previous_stop)
                    break
                else:
                    commission += 0
                count += 1
                previous_commission_obj = line
            return commission
        return 0

    def reset_to_draft(self):
        """Reset to draft function"""
        self.commission_lines.mapped('account_move_line_id').write({
            'author_ids': [(3, self.author_id.id)]
        })
        self.commission_plan_id.deduction_ids.filtered(lambda x: x.commission_id.id == self.id).write({'commission_id': False})
        self.commission_plan_id.allowance_ids.filtered(lambda x: x.commission_id.id == self.id).write({'commission_id': False})
        self.deduction_lines.unlink()
        self.allowance_lines.unlink()
        self.commission_lines.unlink()
        self.write({
            'state': 'draft',
            'commission': 0,
        })

    def confirm(self):
        """Confirm commission function"""
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
        """Set as paid function"""
        self.write({
            'state': 'paid'
        })

    def cancel(self):
        """Set as cancel function"""
        self.write({
            'state': 'cancel'
        })


class CommissionLines(models.Model):
    _name = 'commission.lines'

    account_move_line_id = fields.Many2one('account.invoice.line', string="Invoice Line")
    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    line_id = fields.Many2one('commission')
    quantity = fields.Float(string="Quantity")
    subtotal = fields.Float(string="Subtotal")
    margin = fields.Float(string="Margin")
    currency_id = fields.Many2one('res.currency', related='line_id.currency_id', string="Currency")


class CommissionAllowances(models.Model):
    _name = 'commission.allowances'

    name = fields.Char('Name')
    amount = fields.Monetary('Amount')
    line_id = fields.Many2one('commission')
    currency_id = fields.Many2one('res.currency', related='line_id.currency_id', string="Currency")


class CommissionDeductions(models.Model):
    _name = 'commission.deductions'

    name = fields.Char('Name')
    amount = fields.Monetary('Amount')
    line_id = fields.Many2one('commission')
    currency_id = fields.Many2one('res.currency', related='line_id.currency_id', string="Currency")
