from odoo import models, api, fields


class InheritProductTemplate(models.Model):
    _inherit = 'product.product'

    commission_plan_ids = fields.One2many('commission.plan', 'product_id')


class CommissionPlan(models.Model):
    _name = 'commission.plan'

    name = fields.Char(string="Name")
    author_id = fields.Many2one('commission.authors', string="Author")
    commission_structure = fields.Many2one('commission.structure', string="Commission Structure")
    product_id = fields.Many2one('product.product', string="Product")
    deduction_ids = fields.One2many('commission.pre.deductions', 'line_id')
    allowance_ids = fields.One2many('commission.pre.allowances', 'line_id')


class CommissionPreDeductions(models.Model):
    _name = 'commission.pre.deductions'

    date = fields.Date(string="Date")
    name = fields.Char(string="Name")
    amount = fields.Float(string="Amount")
    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    line_id = fields.Many2one('commission.plan')
    commission_id = fields.Many2one('commission', string="Commission")


class CommissionPreAllowances(models.Model):
    _name = 'commission.pre.allowances'

    date = fields.Date(string="Date")
    name = fields.Char(string="Name")
    amount = fields.Float(string="Amount")
    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    line_id = fields.Many2one('commission.plan')
    commission_id = fields.Many2one('commission', string="Commission")


