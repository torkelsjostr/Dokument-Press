from odoo import models, api, fields
from odoo.exceptions import UserError


class InheritAccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    author_ids = fields.Many2many('commission.authors', string="Commission Authors")


class InheritAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    commission_id = fields.Many2one('commission')

    def write(self, vals):
        """Updating Commission when invoice is paid"""
        write_obj = super(InheritAccountInvoice, self).write(vals)
        if self.state == 'paid':
            if self.commission_id:
                self.commission_id.write({'state': 'paid'})
        return write_obj


