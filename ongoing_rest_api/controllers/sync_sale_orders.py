from odoo import fields, models, api
import requests
import json
from base64 import b64encode
from odoo.exceptions import UserError


class TransportServiceCode(models.Model):
    _name = 'transporter.service.code'
    _rec_name = 'reference'

    reference = fields.Char(string="Name", required=True)
    name = fields.Char(string="Transporter Code", required=True)
    code = fields.Char(string="Transporter Service Code", required=True)


class CustomerType(models.Model):
    _name = 'customer.type'

    name = fields.Char(string="Name", required=True)


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    ongoing_order_ref = fields.Integer("Ongoing Product Ref", copy=False)
    carrier_tracking_ref = fields.Char(string='Tracking Reference')
    sales_order_remark = fields.Text("Purchase Order Remark")
    email = fields.Boolean("Email Notification")
    sms = fields.Boolean("SMS Notification")
    email_message = fields.Text("Email Message")
    sms_message = fields.Text("SMS Message")
    delivery_instruction = fields.Char("Delivery Instruction")
    delivery_information = fields.Char("Delivery Information")
    transport_service_code_id = fields.Many2one('transporter.service.code', "Transporter Service Code")
    customer_type_id = fields.Many2one('customer.type', "Customer Type")
    # priority = fields.Selection([('0', 'Not urgent'), ('1', 'Normal'), ('2', 'Urgent'), ('3', 'Very Urgent')], string='Priority', default='1')

    def select_all(self):
        """Select all the Order lines"""
        for line in self.order_line:
            line.write({
                "create_in_ongoing": True
            }),
        if self.state == 'sale':
            self.env['sync.sale.order'].create_sale_order_in_ongoing(self)

    def action_confirm(self):
        """Overiding odoo button_confirm function and adding function to create SO to ongoing orders, note that
        only confirmed SO are sent"""
        sale_order_obj = super(InheritSaleOrder, self).action_confirm()
        self.env['sync.sale.order'].create_sale_order_in_ongoing(self)
        return sale_order_obj

    @api.multi
    def write(self, vals):
        """Overiding odoo write function and adding function to create SO to ongoing orders, note that
        only confirmed SO are sent"""
        sale_order_obj = super(InheritSaleOrder, self).write(vals)
        if not self._context.get('noupdate'):
            if self.state == 'sale':
                self.env['sync.sale.order'].create_sale_order_in_ongoing(self)
        return sale_order_obj

    @api.multi
    def sync_all_orders(self):
        """Syncing all SOs at once"""
        for order in self.env['sale.order'].search([('ongoing_order_ref', '=', False), ('state', '=', 'sale')]):
            self.env['sync.sale.order'].create_sale_order_in_ongoing(order)


class SyncSaleOrder(models.TransientModel):
    _name = 'sync.sale.order'

    def create_sale_order_in_ongoing(self, sale_order_id):
        """Function that sends SO to Ongoing"""
        api_obj = self.env['api.form'].sudo().search([('name', '=', 'sale_order')], limit=1)
        if not api_obj:
            raise UserError("Missing Content In API Configuration, Please Contact Administrator.")
        encoded_username_and_password = b64encode((api_obj.username + ":" + api_obj.password).encode('ascii')).decode(
            'ascii')
        goods_owner_id = api_obj.goods_owner_id
        headers = {'Authorization': 'Basic %s' % encoded_username_and_password}
        url = api_obj.url
        headers.update({'Accept': '*/*', 'Content-Type': 'application/json'})
        order_line = []
        count = 0
        for line in sale_order_id.order_line:
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
            'orderNumber': sale_order_id.name,
            'deliveryDate': str(sale_order_id.confirmation_date),
            'consignee': {
                'name': sale_order_id.partner_id.name,
                'address1': sale_order_id.partner_shipping_id.street or None,
                'address2': sale_order_id.partner_shipping_id.street2 or None,
                'postCode': sale_order_id.partner_shipping_id.zip or None,
                'city': sale_order_id.partner_shipping_id.city or None,
                'countryCode': sale_order_id.partner_shipping_id.country_id.code or None,
                'countryStateCode': sale_order_id.partner_shipping_id.state_id.code or None,
                'customerNumber': sale_order_id.partner_shipping_id.ref or None,
                'remark': sale_order_id.delivery_information or None
            },
            'freeText1': sale_order_id.picking_policy or None,
            'orderLines': order_line,
            'salesCode': sale_order_id.client_order_ref or None,
            'wayBill': sale_order_id.carrier_tracking_ref or None,
            'deliveryInstruction': sale_order_id.delivery_instruction or None,
            'transporter': {
                'transporterCode': sale_order_id.transport_service_code_id.name or None,
                'transporterServiceCode': sale_order_id.transport_service_code_id.code or None
            },
            'orderRemark': sale_order_id.sales_order_remark or None,
            'orderType': {
                'name': sale_order_id.customer_type_id.name
            },
            'emailNotification': {
                'toBeNotified': sale_order_id.email,
                'value': sale_order_id.email_message or None
            },
            'smsNotification': {
                'toBeNotified': sale_order_id.email,
                'value': sale_order_id.sms_message or None
            }
        }
        if order_line:
            return_response = requests.put(url, headers=headers, json=data)
            if return_response.status_code in [200, 201]:
                if not sale_order_id.ongoing_order_ref:
                    sale_order_id.write({
                        "ongoing_order_ref": json.loads(return_response.text).get('orderId')
                    })
            else:
                raise UserError(str(sale_order_id.id) + " - " + str(sale_order_id.name) + " ------ " + str(
                    json.loads(return_response.text).get('message')) + " - " + str(
                    json.loads(return_response.text).get('modelState')))


class InheritSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    create_in_ongoing = fields.Boolean(string="Create in Ongoing", default=True, store=True)