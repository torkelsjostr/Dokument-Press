from odoo import models, fields, api


class InheritStockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    default_sales_create_in_ongoing = fields.Boolean(string="Default Create in SO in Ongoing", default=False)
    default_purchase_create_in_ongoing = fields.Boolean(string="Default Create in PO in Ongoing", default=False)