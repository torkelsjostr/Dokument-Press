from odoo import models, api, fields
from odoo.exceptions import UserError


class CommissionStructure(models.Model):
    _name = 'commission.structure'

    name = fields.Char(string="Name")
    commission_base = fields.Selection([('gross_amount', 'Gross Amount (Total Sales Revenue)'), ('net_amount', 'Net Amount (Total Sales Less Cost)'), ('fixed_amount', 'Fixed Amount (qty sold + fixed amount)')], string="Base")
    commission_type = fields.Selection([('percentage', 'Percentage'), ('sections', 'Sections')], string="Type")
    commission_rate = fields.Float(string="Rate (%)")
    commission_fixed_rate = fields.Float(string="Fixed Rate")
    commission_structure_ids = fields.One2many('commission.structure.lines', 'line_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id, string="Currency")


class CommissionStructureLines(models.Model):
    _name = 'commission.structure.lines'

    line_id = fields.Many2one('commission.structure')
    minimum_amount = fields.Float('Minimum')
    maximum_amount = fields.Float('Maximum')
    rate = fields.Float('Rate')
    fixed_amount = fields.Float('Fixed Amount')

    @api.model
    def create(self, vals):
        """Validation to avoid minimum greater than maximum"""
        obj = super(CommissionStructureLines, self).create(vals)
        if obj.minimum_amount >= obj.maximum_amount:
            raise UserError("Minimum should be less than Maximum")
        return obj





