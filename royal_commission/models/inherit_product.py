from odoo import models, api, fields


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    commission_structure = fields.Many2one('commission.structure', string="Commission Structure")


class InheritAuthor(models.Model):
    _inherit = 'author'

    partner_id = fields.Many2one('res.partner', string="Partner")