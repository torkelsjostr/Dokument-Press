# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2019-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, fields, models, _

#Class is Extended for new features, which are displaying two tables for total customer invoice and total vendor bills on particular product form, also display its button with total amount of that product.
class ProductTemplateInvoiceAmount(models.Model):
    _inherit = "product.template"

    cust_invoice_line_ids = fields.One2many('account.invoice.line','template_id', string='Customer Invoice',compute='_compute_get_customer_invoices_in_product',help='get particular products invoice id from all customers invoices')
    
    vendor_bill_line_ids = fields.One2many('account.invoice.line','template_id', string='Vendor Bill Line',compute='_compute_get_vendor_bills_in_product',help='get particular products invoice id from all vendors bills')

    #compute customers invoices on product, which is related to that product.  
    def _compute_get_customer_invoices_in_product(self):
        for record in self:
            if record.id:
                cust_invoice=self.env['account.invoice.line'].search([('product_id.product_tmpl_id','=',self.id),('invoice_id.type','=','out_invoice')])
                record.cust_invoice_line_ids = cust_invoice

    #compute vendor bills invoices on product, which is related to that product.  
    def _compute_get_vendor_bills_in_product(self):
        for record in self:
            if record.id:
                vendor_bill=self.env['account.invoice.line'].search([('product_id.product_tmpl_id','=',self.id),('invoice_id.type','=','in_invoice')])
                record.vendor_bill_line_ids = vendor_bill

#Class is Extended for new features,take template_id and invoice_state from account.invoice.line to product.template.
class AccountInvoiceIn(models.Model):
    _inherit = "account.invoice.line"

    template_id = fields.Many2one('product.template',string="template ids",compute='get_template_id',help='This field is in relation with customer invoice and vendor bills')

    invoice_state = fields.Selection([('draft','Draft'),('proforma', 'Pro-forma'),('proforma2', 'Pro-forma'),('open', 'Open'),('paid', 'Paid'),('cancel', 'Cancelled'),], string='Status',compute='get_template_id', index=True, readonly=True, default='draft',track_visibility='onchange', copy=False,help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"" * The 'Pro-forma' status is used when the invoice does not have an invoice number.\n"" * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"" * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"" * The 'Cancelled' status is used when user cancel invoice.")

    ### Add one field for invoice number and vendor bill number
    number = fields.Char(compute='get_template_id')

    #Create template_id(product_id.product_tmpl_id) from product_id and create invoice_state from invoice_id.
    def get_template_id(self):
        for record in self:
            if record.product_id:
                record.template_id = record.product_id.product_tmpl_id
        for record in self:
            if record.invoice_id:
                record.invoice_state = record.invoice_id.state
        for record in self:
            if record.invoice_id:
                record.number = record.invoice_id.number


