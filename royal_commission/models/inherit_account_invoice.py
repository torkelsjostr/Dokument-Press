from odoo import models, api, fields
from odoo.exceptions import UserError


class InheritAccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    commission_calculated = fields.Boolean('Commission Calculated')
    commission_id = fields.Many2one('commission')


