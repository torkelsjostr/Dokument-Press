from odoo import models, api, fields
from odoo.exceptions import UserError
from datetime import date


class CommissionAuthors(models.Model):
    _name = 'commission.authors'

    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner', string="Partner")

    @api.model
    def create(self, vals):
        """Creating a partner when an author is created"""
        create_obj = super(CommissionAuthors, self).create(vals)
        create_obj.partner_id = self.env['res.partner'].create({'name': create_obj.name, 'supplier': True}).id
        return create_obj

    @api.multi
    def write(self, vals):
        """Modifying a partner when an author is modified"""
        write_obj = super(CommissionAuthors, self).write(vals)
        if self.partner_id:
            self.partner_id.write({'name': self.name})
        return write_obj