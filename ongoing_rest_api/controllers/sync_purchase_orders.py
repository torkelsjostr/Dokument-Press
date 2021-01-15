from odoo import fields, models, api
import requests
import json
from base64 import b64encode
from odoo.exceptions import UserError


class InheritPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    ongoing_order_ref = fields.Integer("Ongoing Product Ref", copy=False)
    purchase_order_remark = fields.Text("Purchase Order Remark")

    def select_all(self):
        """Select all the Order lines"""
        for line in self.order_line:
            line.write({
                "create_in_ongoing": True
            })
        if self.state == 'purchase':
            self.env['sync.purchase.order'].create_purchase_order_in_ongoing(self)

    def button_confirm(self):
        """Overiding odoo button_confirm function and adding function to create PO to ongoing inorders, note that
        only confirmed PO are sent"""
        purchase_order_obj = super(InheritPurchaseOrder, self).button_confirm()
        self.env['sync.purchase.order'].create_purchase_order_in_ongoing(self)
        return purchase_order_obj

    @api.multi
    def write(self, vals):
        """Overiding odoo write function and adding function to create PO to ongoing inorders, note that
        only confirmed PO are sent"""
        purchase_order_obj = super(InheritPurchaseOrder, self).write(vals)
        if not self._context.get('noupdate'):
            if self.state == 'purchase':
                self.env['sync.purchase.order'].create_purchase_order_in_ongoing(self)
        return purchase_order_obj

    @api.multi
    def sync_all_orders(self):
        """Syncing all POs at once"""
        for order in self.env['purchase.order'].search([('state', '=', 'purchase')]):
            self.env['sync.purchase.order'].create_purchase_order_in_ongoing(order)


class SyncPurchaseOrder(models.TransientModel):
    _name = 'sync.purchase.order'

    def create_purchase_order_in_ongoing(self, purchase_order_id):
        """Function that sends PO to Ongoing"""
        api_obj = self.env['api.form'].sudo().search([('name', '=', 'purchase_order')], limit=1)
        if not api_obj:
            raise UserError("Missing Content In API Configuration, Please Contact Administrator.")
        encoded_username_and_password = b64encode((api_obj.username + ":" + api_obj.password).encode('ascii')).decode('ascii')
        goods_owner_id = api_obj.goods_owner_id
        headers = {'Authorization': 'Basic %s' % encoded_username_and_password}
        url = api_obj.url
        headers.update({'Accept': '*/*', 'Content-Type': 'application/json'})
        order_line = []
        count = 0
        for line in purchase_order_id.order_line:
            if line.product_id.type == 'product' and line.create_in_ongoing:
                count += 1
                order = {
                    "rowNumber": count,
                    "articleNumber": line.product_id.default_code,
                    "numberOfItems": line.product_uom_qty,
                    "comment": line.product_id.name
                }
                order_line.append(order)
        data = {
            'goodsOwnerId': goods_owner_id,
            'purchaseOrderNumber': purchase_order_id.name,
            'supplierOrderNumber': purchase_order_id.partner_ref,
            'deliveryDate': str(purchase_order_id.date_planned),
            'supplierInfo': {
                'supplierName': purchase_order_id.partner_id.name
            },
            'purchaseOrderLines': order_line,
            'purchaseOrderRemark': purchase_order_id.purchase_order_remark
        }
        if order_line:
            return_response = requests.put(url, headers=headers, json=data)
            if return_response.status_code in [200, 201]:
                if not purchase_order_id.ongoing_order_ref:
                    purchase_order_id.write({
                        "ongoing_order_ref": json.loads(return_response.text).get('purchaseOrderId')
                    })
            else:
                raise UserError(str(purchase_order_id.id) + " - " + str(purchase_order_id.name) + " ------ " + str(
                    json.loads(return_response.text).get('message')) + " - " + str(
                    json.loads(return_response.text).get('modelState')))


class InheritPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    create_in_ongoing = fields.Boolean(string="Create in Ongoing", default=True)