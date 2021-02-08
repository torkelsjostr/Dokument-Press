from odoo import models, fields, api
from odoo.exceptions import UserError
from base64 import b64encode
import requests
import json


class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", compute='get_order_id')
    ongoing_sale_ref = fields.Integer("Ongoing Sale Ref", related='sale_order_id.ongoing_order_ref', store=True)
    ongoing_int_sale_ref = fields.Integer("Ongoing Internal Sale Ref", store=True)
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order", compute='get_order_id')
    ongoing_purchase_ref = fields.Integer("Ongoing Purchase Ref", related='purchase_order_id.ongoing_order_ref', store=True)
    ongoing_int_purchase_ref = fields.Integer("Ongoing Internal Purchase Ref", store=True)
    source_type = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase'), ('internal', 'Internal')], "Source Type", compute='get_order_id', store=True)
    create_sale_order = fields.Boolean('Create Sale Order')
    create_purchase_order = fields.Boolean('Create Purchase Order')
    partial_transfer = fields.Boolean('Partial Transfer')
    order_remark = fields.Text("Order Remark")

    ongoing_order_ref = fields.Integer("Ongoing Product Ref", copy=False)
    carrier_tracking_ref = fields.Char(string='Tracking Reference')
    email = fields.Boolean("Email Notification")
    sms = fields.Boolean("SMS Notification")
    email_message = fields.Text("Email Message")
    sms_message = fields.Text("SMS Message")
    delivery_instruction = fields.Char("Delivery Instruction")
    delivery_information = fields.Char("Delivery Information")
    transport_service_code_id = fields.Many2one('transporter.service.code', "Transporter Service Code")
    customer_type_id = fields.Many2one('customer.type', "Customer Type")

    @api.one
    @api.depends('origin')
    def get_order_id(self):
        """Getting origin ID and origin type"""
        if self.origin and self.picking_type_code != 'internal':
            sale_order = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
            purchase_order = self.env['purchase.order'].search([('name', '=', self.origin)], limit=1)
            if sale_order or self.create_sale_order:
                self.sale_order_id = sale_order.id
                self.source_type = 'sale'
            if purchase_order or self.create_purchase_order:
                self.purchase_order_id = purchase_order.id
                self.source_type = 'purchase'
        else:
            pass

    def run_manually(self):
        """Function to retrieve data from Ongoing"""
        if self.ongoing_sale_ref or self.ongoing_purchase_ref:
            ongoing_id = self.ongoing_sale_ref if self.source_type == 'sale' else self.ongoing_purchase_ref
            self.env['sync.sale.transfers'].retrieve_values_from_ongoing(ongoing_id, self.source_type, self)
        elif self.ongoing_int_sale_ref or self.ongoing_int_purchase_ref:
            ongoing_id = self.ongoing_int_sale_ref if self.source_type == 'sale' else self.ongoing_int_purchase_ref
            self.env['sync.sale.transfers'].retrieve_values_from_ongoing(ongoing_id, self.source_type, self)

    def scheduled_run(self):
        """Function to retrieve data from Ongoing in Scheduled Action"""
        unconfirmed_pickings = self.env['stock.picking'].search([('state', 'not in', ['draft', 'done', 'cancel'])])
        for item in unconfirmed_pickings:
            item.run_manually()

    @api.multi
    def action_confirm(self):
        """Inheriting MarkASTodo button and calling API Function"""
        if self.create_purchase_order and self.create_sale_order:
            raise UserError("There cannot be both sale and purchase order for a transfer.")
        return_obj = super(InheritStockPicking, self).action_confirm()
        if self.create_purchase_order:
            self.env['sync.sale.transfers'].sync_purchase_internal_transfers(self)
            return return_obj
        if self.create_sale_order:
            self.env['sync.sale.transfers'].sync_sale_internal_transfers(self)
            return return_obj


class SyncSaleTransfer(models.TransientModel):
    _name = 'sync.sale.transfers'

    def retrieve_values_from_ongoing(self, ongoing_id, source_type, stock_picking_id):
        """Retrieving data from Ongoing"""
        if source_type == "sale":
            api_obj = self.env['api.form'].sudo().search([('name', '=', 'get_sale_order')], limit=1)
        else:
            api_obj = self.env['api.form'].sudo().search([('name', '=', 'get_purchase_order')], limit=1)
        if not api_obj:
            raise UserError("Missing Content In API Configuration, Please Contact Administrator.")
        encoded_username_and_password = b64encode((api_obj.username + ":" + api_obj.password).encode('ascii')).decode(
            'ascii')
        headers = {'Authorization': 'Basic %s' % encoded_username_and_password}
        url = api_obj.url + str(ongoing_id)
        headers.update({'Accept': '*/*'})
        return_response = requests.get(url, headers=headers)
        print(json.loads(return_response.text))
        response_converted_json = json.loads(return_response.text)
        if response_converted_json:
            if source_type == 'purchase':
                # if type is purchase
                order_status_code = response_converted_json.get('purchaseOrderInfo').get('purchaseOrderStatus').get('number')
                if order_status_code == 900:
                    stock_picking_id.action_cancel()
                elif 400 < order_status_code < 900:
                    if stock_picking_id.state != 'done':
                        for line in stock_picking_id.move_ids_without_package:
                            for item in response_converted_json.get('purchaseOrderLines'):
                                if item.get('article').get('articleSystemId') == line.product_id.ongoing_product_ref and item.get('advisedNumberOfItems') == line.product_uom_qty:
                                    line.with_context(noupdate=True).write({'quantity_done': item.get('receivedNumberOfItems')})
                    if stock_picking_id.state != 'done':
                        stock_picking_id.button_validate()
                elif order_status_code == 400:
                    if stock_picking_id.state != 'done':
                        for line in stock_picking_id.move_ids_without_package:
                            for item in response_converted_json.get('purchaseOrderLines'):
                                if item.get('article').get('articleSystemId') == line.product_id.ongoing_product_ref and item.get('advisedNumberOfItems') == line.product_uom_qty:
                                    line.with_context(noupdate=True).write({'quantity_done': item.get('receivedNumberOfItems')})
                elif 100 < order_status_code < 400:
                    print("Open")
                elif order_status_code <= 100:
                    print("Draft")
                else:
                    raise UserError("Status Not Found")
            else:
                # if type is sales
                order_status_code = response_converted_json.get('orderInfo').get('orderStatus').get('number')
                if order_status_code == 1000:
                    stock_picking_id.action_cancel()
                elif 400 < order_status_code < 1000:
                    if stock_picking_id.state != 'done':
                        for line in stock_picking_id.move_ids_without_package:
                            for item in response_converted_json.get('orderLines'):
                                if int(item.get('article').get('articleSystemId')) == line.product_id.ongoing_product_ref and item.get('orderedNumberOfItems') == line.product_uom_qty:
                                    line.with_context(noupdate=True).write({'quantity_done': item.get('pickedNumberOfItems')})
                    if stock_picking_id.sale_order_id:
                        sql = """UPDATE sale_order SET carrier_tracking_ref = %s where id = %s"""
                        values = (
                        response_converted_json.get('orderInfo').get('wayBill'), stock_picking_id.sale_order_id.id)
                        self._cr.execute(sql, values)
                    else:
                        stock_picking_id.write({
                            "carrier_tracking_ref": response_converted_json.get('orderInfo').get('wayBill')
                        })
                    if stock_picking_id.state != 'done':
                        stock_picking_id.button_validate()
                elif order_status_code == 400:
                    if stock_picking_id.state != 'done':
                        for line in stock_picking_id.move_ids_without_package:
                            for item in response_converted_json.get('orderLines'):
                                if int(item.get('article').get('articleSystemId')) == line.product_id.ongoing_product_ref and item.get('orderedNumberOfItems') == line.product_uom_qty:
                                    line.with_context(noupdate=True).write({'quantity_done': item.get('pickedNumberOfItems')})
                    if stock_picking_id.sale_order_id:
                        sql = """UPDATE sale_order SET carrier_tracking_ref = %s where id = %s"""
                        values = (response_converted_json.get('orderInfo').get('wayBill'), stock_picking_id.sale_order_id.id)
                        self._cr.execute(sql, values)
                        print("Picked")
                    else:
                        stock_picking_id.write({
                            "carrier_tracking_ref": response_converted_json.get('orderInfo').get('wayBill')
                        })
                elif order_status_code == 380:
                    if stock_picking_id.state != 'done':
                        for line in stock_picking_id.move_ids_without_package:
                            for item in response_converted_json.get('orderLines'):
                                if int(item.get('article').get(
                                        'articleSystemId')) == line.product_id.ongoing_product_ref and item.get(
                                        'orderedNumberOfItems') == line.product_uom_qty:
                                    line.with_context(noupdate=True).write(
                                        {'quantity_done': item.get('pickedNumberOfItems')})
                    if stock_picking_id.sale_order_id:
                        sql = """UPDATE sale_order SET carrier_tracking_ref = %s where id = %s"""
                        values = (
                        response_converted_json.get('orderInfo').get('wayBill'), stock_picking_id.sale_order_id.id)
                        self._cr.execute(sql, values)
                        print("Picked")
                    else:
                        stock_picking_id.write({
                            "carrier_tracking_ref": response_converted_json.get('orderInfo').get('wayBill')
                        })
                    cancel_backorder_obj = self.env['stock.backorder.confirmation'].create({'pick_ids': [(4, stock_picking_id.id)]})
                    cancel_backorder_obj.process_cancel_backorder()
                    stock_picking_id.write({
                        'partial_transfer': True
                    })
                else:
                    raise UserError("Status Not Found")

    def sync_purchase_internal_transfers(self, purchase_order_id):
        """Function that sends PO to Ongoing"""
        api_obj = self.env['api.form'].sudo().search([('name', '=', 'purchase_order')], limit=1)
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
        for line in purchase_order_id.move_ids_without_package:
            if line.product_id.type == 'product':
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
            'supplierOrderNumber': purchase_order_id.origin,
            'deliveryDate': str(purchase_order_id.scheduled_date),
            'supplierInfo': {
                'supplierName': purchase_order_id.partner_id.name
            },
            'purchaseOrderLines': order_line,
            'purchaseOrderRemark': purchase_order_id.order_remark
        }
        return_response = requests.put(url, headers=headers, json=data)
        if return_response.status_code in [200, 201]:
            if not purchase_order_id.ongoing_purchase_ref:
                purchase_order_id.write({
                    "ongoing_purchase_ref": json.loads(return_response.text).get('purchaseOrderId'),
                    "ongoing_int_purchase_ref": json.loads(return_response.text).get('purchaseOrderId'),
                    "source_type": 'purchase',
                })
        else:
            raise UserError(str(purchase_order_id.id) + " - " + str(purchase_order_id.name) + " ------ " + str(
                json.loads(return_response.text).get('message')) + " - " + str(
                json.loads(return_response.text).get('modelState')))

    def sync_sale_internal_transfers(self, sale_order_id):
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
        for line in sale_order_id.move_ids_without_package:
            if line.product_id.type == 'product':
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
            'deliveryDate': str(sale_order_id.scheduled_date),
            'consignee': {
                'name': sale_order_id.partner_id.name,
                'address1': sale_order_id.partner_id.street or None,
                'address2': sale_order_id.partner_id.street2 or None,
                'postCode': sale_order_id.partner_id.zip or None,
                'city': sale_order_id.partner_id.city or None,
                'countryCode': sale_order_id.partner_id.country_id.code or None,
                'countryStateCode': sale_order_id.partner_id.state_id.code or None,
                'customerNumber': sale_order_id.partner_id.ref or None,
                'remark': sale_order_id.delivery_information or None
            },
            # 'freeText1': sale_order_id.picking_policy or None,
            'orderLines': order_line,
            # 'salesCode': sale_order_id.client_order_ref or None,
            'wayBill': sale_order_id.carrier_tracking_ref or None,
            'deliveryInstruction': sale_order_id.delivery_instruction or None,
            'transporter': {
                'transporterCode': sale_order_id.transport_service_code_id.name or None,
                'transporterServiceCode': sale_order_id.transport_service_code_id.code or None
            },
            'orderRemark': sale_order_id.order_remark or None,
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
        return_response = requests.put(url, headers=headers, json=data)
        if return_response.status_code in [200, 201]:
            if not sale_order_id.ongoing_sale_ref:
                sale_order_id.write({
                    "ongoing_sale_ref": json.loads(return_response.text).get('orderId'),
                    "ongoing_int_sale_ref": json.loads(return_response.text).get('orderId'),
                    "source_type": 'sale',
                })
        else:
            raise UserError(str(sale_order_id.id) + " - " + str(sale_order_id.name) + " ------ " + str(
                json.loads(return_response.text).get('message')) + " - " + str(
                json.loads(return_response.text).get('modelState')))

