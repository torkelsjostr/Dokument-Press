import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ProductReturnReason(models.Model):
    _name = 'product.return.reason'
    _inherit = 'mail.thread'
    _description = 'Products Return Reason'

    name = fields.Char(string='Title', required=True, translate=True, track_visibility='onchange', help="The title of the reason,"
                       " e.g. Bad quality, Customer changed mind, etc")
    active = fields.Boolean(string='Active', default=True, help="If unchecked, it will allow you to hide"
                            " the reason without removing it.")
    product_ids = fields.Many2many('product.product', 'product_return_reason_rel', 'reason_id', 'product_id', compute='_compute_product_ids', store=True,
                                   string='Returned Products', help="The products that have been returned with this reason")

    products_count = fields.Integer(string='Products Count', compute='_compute_products_count')

    description = fields.Text(string='Description')

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The Title of the reason must be unique"),
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the reason should not be the description"),
    ]

    def _compute_product_ids(self):
        _logger.error("The method `_compute_product_ids()` has not been implemented yet!")

    @api.depends('product_ids')
    def _compute_products_count(self):
        for r in self:
            r.products_count = len(r.product_ids)
