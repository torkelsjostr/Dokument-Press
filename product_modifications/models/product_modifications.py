from odoo import models, fields, api


class ProductTemplateModifications(models.Model):
    _inherit = 'product.template'

    article_code = fields.Char(string='Article Code', translate=True)
    article_category_code = fields.Char(string='Article Category Code', translate=True)
    article_group_code = fields.Char(string='Article Group Code', translate=True)
    article_accounting_code_eu = fields.Integer(string='Article Accounting Code EU', translate=True)
    article_accounting_code_exp = fields.Integer(string='Article Accounting Code EXP', translate=True)
    article_accounting_code_vat = fields.Integer(string='Article Accounting Code VAT', translate=True)
    article_accounting_code_se = fields.Integer(string='Article Accounting Code SE', translate=True)
    article_vat_percentage = fields.Float(string='Article VAT Percentage', translate=True)
    article_supplier = fields.Char(string='Article Supplier', translate=True)
    article_manufacturer = fields.Char(string='Article Manufacturer', translate=True)
    manufacturer = fields.Integer(string='Manufacturer', translate=True)
    average_cost = fields.Float(string='Average Cost', translate=True)
    delivery_cost = fields.Float(string='Delivery Cost', translate=True)
    total_cost_in_sek = fields.Float(string='Total Cost in SEK', translate=True)
    total_cost_in_currency = fields.Float(string='Total Cost in "Currency"', translate=True)
    height = fields.Float(string='Height (Vertical)', translate=True)
    width = fields.Float(string='Width (Horizontal)', translate=True)
    length = fields.Float(string='Length (Horizontal)', translate=True)
    length_in_minutes = fields.Integer(string='Length in Minutes', translate=True)
    accounting_code = fields.Char(string='Accounting Code', translate=True)
    object = fields.Char(string='Object', translate=True)
    suppliers_article_code = fields.Char(string="Suppliers' Article Code", translate=True)
    supplier_code = fields.Integer(string='Supplier Code', translate=True)
    bonus = fields.Char(string='Bonus', translate=True)
    distribution = fields.Boolean(string='Distribution', translate=True)
    not_included_in_web_store = fields.Boolean(string='Not Included in Web Store', translate=True)
    marked_as_product_sold_on_commission = fields.Boolean(string='Marked as "Product Sold on Commission"',translate=True)
    date_of_arrival = fields.Date(string='Date of Arrival', translate=True)
    quantity = fields.Integer(string='Quantity', translate=True)
    year_of_production = fields.Char(string='Year of Production', translate=True)
    number_of_pages = fields.Integer(string='Number of Pages', translate=True)
    author_by = fields.Text(string='Author/By', translate=True)
    country_id = fields.Char(string='Country', translate=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=False, store=True, translate=True)
    binding_swe = fields.Char(string='Binding (SWE)', translate=True)
    binding_eng = fields.Char(string='Binding (ENG)', translate=True)
    product_group = fields.Char(string='Product Group', translate=True)
    number_of_illustrations = fields.Integer(string='Number of Illustrations', translate=True)
    colour = fields.Char(string='Colour', translate=True)
    language_1 = fields.Char(string='Language 1', translate=True)
    language_2 = fields.Char(string='Language 2', translate=True)
    description_eng = fields.Text(string='Description (English)', translate=True)
    description_swd = fields.Text(string='Description (Swedish)', translate=True)
    comment_on_purchase = fields.Text(string='Comment On Purchase', translate=True)
    general_comment = fields.Text(string='General Comment', translate=True)
    keywords_related_to_search = fields.Char(string='Keywords Related to Search', translate=True)
    storeable = fields.Boolean(string='Stock-able', translate=True)
    amount_in_stock = fields.Integer(string='Amount in stock', translate=True)
    size = fields.Selection(selection=[
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL'),
        ('xxl', 'XXL')], string='Size', translate=True)

