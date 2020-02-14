import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_virtual_stock = fields.Float(related='product_id.virtual_available')

