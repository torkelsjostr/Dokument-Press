from odoo import models, fields, api


class ResCustomerModification(models.Model):
    _inherit = 'res.partner'

    customer_group = fields.Many2one('customer.group', string='Customer Group', translate=True)
    customer_vat_type = fields.Many2one('customer.vat.type', string='Customer VAT Type', translate=True)
    vat_of_the_client = fields.Char(string='The VAT of The Client', translate=True)
    currency = fields.Many2one('res.currency', string='Currency', translate=True)
    important_notes = fields.Text(string='Important Notes', translate=True)
    # primary = fields.Char(string='Primary Contact: Name')
    email_2 = fields.Char(string='Primary contact: Email', translate=True)
    primary_phone = fields.Char(string='Primary contact: Phone number', translate=True)
    customer_code = fields.Char(string='Customer Code', translate=True)
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Billing address'),
         ('delivery', 'Delivery address'),
         ('other', 'Other address'),
         ("private", "Private Address"),
         ], string='Address Type',
        default='contact',
        help="Used by Sales and Purchase Apps to select the relevant address depending on the context.")
    primary_name = fields.Char(string='Primary Contact: Name', translate=True)

class CustomerGroups(models.Model):
    _name = 'customer.group'

    name = fields.Char(string='Customer Group Name', translate=True)
    customer_group_id = fields.Char(string='ID', translate=True)


class CustomerVatType(models.Model):
    _name = 'customer.vat.type'

    name = fields.Char(string='Customer VAT Type', translate=True)
    customer_vat_id = fields.Char(string='ID', translate=True)
