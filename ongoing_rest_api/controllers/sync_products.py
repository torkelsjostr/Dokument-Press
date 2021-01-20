from odoo import fields, models, api
import requests
import json
from base64 import b64encode
from odoo.exceptions import UserError


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    ongoing_product_ref = fields.Integer("Ongoing Product Ref")

    @api.model
    def create(self, vals):
        """Overiding odoo create function and adding function to create products to ongoing articles, note that
        only product type is product"""
        product_obj = super(InheritProductTemplate, self).create(vals)
        if product_obj.type == 'product':
            self.env['sync.products'].create_product_in_ongoing(product_obj)
        return product_obj

    @api.multi
    def write(self, vals):
        """Overiding odoo create function and adding function to write products to ongoing articles, note that
        only product type is product"""
        product_obj = super(InheritProductTemplate, self).write(vals)
        if self.type == 'product':
            sql = """UPDATE product_template SET  ongoing_product_ref = %s where id = %s"""
            values = (self.env['sync.products'].create_product_in_ongoing(self), self.id)
            self._cr.execute(sql, values)
        return product_obj

    @api.multi
    def sync_all_products(self):
        """This is a schedule action function to sync all products at once"""
        for product in self.env['product.template'].search([('type', '=', 'product')]):
            self.env['sync.products'].create_product_in_ongoing(product)


class SyncProducts(models.TransientModel):
    _name = 'sync.products'

    def create_product_in_ongoing(self, product_id):
        """Function where products are sent to ongoing"""
        product_api_obj = self.env['api.form'].sudo().search([('name', '=', 'product')], limit=1)
        if not product_api_obj:
            raise UserError("Missing Content In API Configuration, Please Contact Administrator.")
        encoded_username_and_password = b64encode((product_api_obj.username + ":" + product_api_obj.password).encode('ascii')).decode('ascii')
        goods_owner_id = product_api_obj.goods_owner_id
        headers = {'Authorization': 'Basic %s' % encoded_username_and_password}
        url = product_api_obj.url
        headers.update({'Accept': '*/*', 'Content-Type': 'application/json'})
        quantity_per_package = 0
        for package in product_id.packaging_ids:
            quantity_per_package += package.qty
        data = {
            'articleGroup': {
                'name': product_id.product_group_id.name or None
            },
            'articleCategory': {
                'name': product_id.categ_id.name
            },
            'articleColour': {
                'name': product_id.colour_id.name
            },
            'articleSize': {
                'name': product_id.size
            },
            'barCodeInfo': {
                'barCode': product_id.barcode
            },
            'quantityPerPackage': round(quantity_per_package),
            'goodsOwnerId': goods_owner_id,
            'articleNumber': product_id.default_code,
            'articleName': product_id.name,
            'weight': product_id.weight,
            'width': product_id.width,
            'length': product_id.length,
            'height': product_id.height,
            'volume': product_id.volume,
            'statisticsNumber': product_id.intrastat_id.code
        }
        return_response = requests.put(url, headers=headers, json=data)
        if return_response.status_code == 200:
            return json.loads(return_response.text).get('articleSystemId')
        else:
            raise UserError(str(product_id.id) + " - " + str(product_id.name) + " ------ " + str(json.loads(return_response.text).get('message')) + " - " + str(json.loads(return_response.text).get('modelState')))

