# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
import sys
from odoo import models, api, fields, _, tools
import logging
import base64
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)

VOUCHER_RECORD_COUNT = 20
MONETARIES = ('total_vat_amount_scanned',
              'total_amount_incl_vat',
              'total_amount_excl_vat',
              'amount',
              'unit_price',
              'ex_vat_amount',
              'incl_vat_amount',
              'discount_amount')

# Do the invert check of self.state in ('waiting', 'failed_engine')
# to be backward compatible
NO_REFRESH_STATES = ('upload', 'ready', 'generated', 'failed', 'deleted')

# Mapping scanned voucher to invoice type
VOUCHER2INVOICE = {
    'receipt': 'in_invoice',
    'invoice': 'in_invoice',
    'creditnote': 'in_refund',
    'unknown': 'in_invoice',
    'reminder': 'in_invoice',
    'account_statement': 'in_invoice',
    'accountstatement': 'in_invoice',
}

# Mapping scanned voucher status to odoo voucher state
STATUS2STATE = {
    'received': 'waiting',
    'account_suggest_processing': 'waiting',
    'processing_failed': 'waiting',
    'processed_successfully': 'waiting',
    'integration_processing': 'waiting',
    'integration_processing_failed': 'waiting',
    'integration_processing_failed_internal_error': 'waiting',
    'integration_processed_successfully': 'waiting',
    'hdr_processing': 'waiting',
    'processing': 'waiting',
    'successful': 'ready',
    'failed': 'failed_engine',
    'queued': 'waiting',
    'unknown': 'waiting',
}


class ScannedVoucher(models.Model):
    _name = 'invoicescan.voucher'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Invoice Scan Voucher'
    _order = 'create_date desc'
    
    invoice_scan_provider = None
    
    # Uploads
    upload_user_id = fields.Many2one('res.users', string='Uploaded by User', readonly=True)
    upload_email = fields.Char(string="Uploaded by Email", default='')

    # Manual Fields
    note = fields.Char(string="Note", default='')
    payment_method = fields.Char(string="Payment Method", default='')
    catalog_debitor_id = fields.Char(string="Scanned Debitor ID", default='')
    voucher_type = fields.Selection([('in_invoice', 'Vendor Bill'),
                                    ('in_refund', 'Vendor Credit Note'),
                                    ('out_invoice', 'Customer Invoice'),
                                    ('out_refund', 'Customer Credit Note'),
                                    ('out_receipt', 'Sales Receipt'),
                                    ('in_receipt', 'Purchase Receipt')], string="Voucher Type")

    # Scanned Fields
    voucher_id = fields.Integer(string='Scanning Provider ID', help="Reference id to provider of scanning service", default=0, required=False, readonly=True)
    raw_voucher_text = fields.Text(string='Raw Voucher Text', default='', readonly=True, help="Unstructured textual content of a voucher. This is useful for performing full text searching in vouchers.")
    state = fields.Selection([('upload', 'Uploading Document'),
                              ('waiting', 'Waiting Voucher Data'),
                              ('ready', 'Ready for Invoice Generation'),
                              ('generated', 'Invoice Generated'),
                              ('failed_engine', 'Scan Engine Failed'),
                              ('failed', 'Invoice Generation Failed'),
                              ('deleted', 'Invoice Deleted')],
                              string='Processing State',
                              default='waiting',
                              readonly=True,
                              required=False)
    
    # Scanned Header Fields
    company_name = fields.Char(string="Scanned Partner Name", default='', readonly=True)
    country = fields.Char(string="Sender Country", default='')
    joint_payment_id = fields.Char(string="Joint Payment Id", default='', readonly=True)
    company_vat_reg_no = fields.Char(string="Vat", default='')
    danish_industry_code = fields.Char(string="Danish Industry Code", default='')
    payment_id = fields.Char(string="Payment Id", default='')
    total_vat_amount_scanned = fields.Monetary(string="Tax Amount", default=0, currency_field='currency_id')
    vat_percentage_scanned = fields.Float(string="Vat Percentage ", default=0.0)
    currency = fields.Char(string="Currency", default='')
    voucher_number = fields.Char(string='Voucher Number', default='', readonly=True)
    total_amount_incl_vat = fields.Monetary(string="Gross Amount", default=0, currency_field='currency_id')
    payment_date = fields.Date(string='Scanned Due Date', default='')
    payment_code_id = fields.Char(string="Payment Code", default='')
    invoice_date = fields.Date(string='Invoice Date', default='')
    total_amount_excl_vat = fields.Monetary(string="Net Amount", default=0, currency_field='currency_id')
    creditor_number = fields.Char(string="Creditor Number", default='')
    order_number = fields.Char(string="Order Number", default='')
    purchase_order_number = fields.Char(string="Purchase Order Number", default='')
    gln_number = fields.Char(string="GLN number", default='')
    payment_reg_number = fields.Char(string="Payment Registration Number", default='')
    payment_account_number = fields.Char(string="Account Number", default='')
    payment_iban = fields.Char(string="Payment Iban Number", default='')
    payment_swift_bic = fields.Char(string="Payment Swift or Bic Number", default='')
    reference = fields.Char(string='Other Reference', default='')
    vat_rate = fields.Char(string="Vat Rate", default='')
    penny_difference = fields.Float(string="Payment Rounding ", default=0.0)
    catalog_creditor_id = fields.Char(string="Scanned Creditor ID", default='')
    account_id = fields.Char(string="Scanned Account ID", default='')
    voucher_line_ids = fields.One2many('invoicescan.voucher.line', 'voucher_id', string="Voucher Line Ids", readonly=True)
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'invoicescan.voucher')], string='Attachments')

    # Administration Fields
    seen = fields.Boolean(string='Voucher Reported', default=False)
    
    # Invoice Fields
    invoice_id = fields.Many2one('account.invoice', string='Invoice Id', readonly=True)
    error_message = fields.Text(string='Invoice Generation Error', readonly=True)

    # Computed Fields
    default_currency = fields.Boolean(string='Default Currency is Used', compute='_compute_currency', default=False, readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', string='Currency Id', compute='_compute_currency', readonly=True, store=True)
    company_id = fields.Many2one('res.company', string='Debitor', compute='_compute_company', store=True)

    @api.multi
    def unlink(self):
        for voucher in self:
            if voucher.state == 'generated' or voucher.invoice_id:
                raise UserError(_('Cannot delete voucher(s) which are already generated to an invoice.'))
        return super(ScannedVoucher, self).unlink()

    @api.depends('catalog_debitor_id')
    def _compute_company(self):
        for record in self:
            if record.catalog_debitor_id:
                company_id = int((self.env['res.company'].search([('id', '=', int(record.catalog_debitor_id))], limit=1)).id)
                if company_id:
                    record.company_id = company_id
    
    @api.depends('currency')
    def _compute_currency(self):
        for voucher in self:
            currency = self.env['res.currency'].search([('name', '=', voucher.currency)])
            if currency:
                voucher.currency_id = currency.id
                voucher.default_currency = False
            else:
                voucher.currency_id = self.env['account.invoice'].with_context(type='in_invoice')._default_currency().id
                voucher.default_currency = True
    
    @api.multi
    def upload_vouchers(self):
        vouchers = self.search([('state', '=', 'upload')])
        provider = self._get_scan_provider()
        # Upload vouchers
        for voucher in vouchers:
            attachment = voucher._get_attachment()
            if attachment:
                try:
                    provider_voucher = provider.upload_voucher(attachment)
                    if provider_voucher:
                        voucher.write({
                            'voucher_id': provider_voucher.get('id'),
                            'state': 'waiting'})
                except:
                    self.env.cr.rollback()
                    error_message  = 'The upload failed with following error: {error}'.format(error=sys.exc_info()[1])
                    _logger.exception(error_message)
                    voucher.write({
                            'error_message': error_message,
                            'state': 'failed_engine'})
                self.env.cr.commit()

    @api.multi
    def receive_scanned_vouchers(self, offset=0, search={}, seen='not_seen'):
        content = self._get_scan_provider().get_conditional_vouchers(offset, search, VOUCHER_RECORD_COUNT, seen)
        if content:
            vouchers = content['data']
            vouchers_total_count = content['meta']['count']
            
            # Create vouchers
            for raw_voucher in vouchers:
                self.create_voucher(raw_voucher)

            # Repeat if there are more vouchers
            new_offset = offset + VOUCHER_RECORD_COUNT
            if vouchers_total_count > new_offset: 
                self.receive_scanned_vouchers(new_offset)
    
    @api.multi
    def report_as_done(self):
        # Report to voucher provider that we have computed vouchers to invoices
        vouchers = self.search([('seen', '=', False), ('state', '=', 'generated'), ('invoice_id', '!=', False)])
        if not vouchers:
            return
        voucher_ids = vouchers.mapped('voucher_id')
        status, _, _ = self._get_scan_provider().set_vouchers_as_seen(voucher_ids)
        if not status:
            vouchers.write({'seen': False})
            _logger.exception('Invoice scan: Failed to report {count} vouchers to voucher provider: {voucher_ids}'.format(count=len(voucher_ids), voucher_ids=", ".join(str(i) for i in voucher_ids)))
        else:
            vouchers.write({'seen': True})
            _logger.info('Invoice scan: Successfully reported {count} vouchers to voucher provider: {voucher_ids}'.format(count=len(voucher_ids), voucher_ids=", ".join(str(i) for i in voucher_ids)))
    
    @api.multi
    def get_ready_vouchers(self):
        if self._context.get('create_voucher_ids', False):
            return self.search([('state', 'in', ('deleted', 'failed')), ('invoice_id', '=', False), ('id', 'in', self._context.get('create_voucher_ids')._ids)])
        return self.search([('state', '=', 'ready'), ('invoice_id', '=', False)])
        
    @api.multi
    def create_voucher(self, raw_voucher):
        try:
            vals = self._convert_voucher_values(raw_voucher.get('header_fields', ''), self)
            vals['voucher_id'] = raw_voucher.get('id')
            vals['state'] = STATUS2STATE.get(raw_voucher.get('status'), 'waiting')

            voucher = self.search([('voucher_id', '=', vals.get('voucher_id'))], limit=1)
            if voucher and voucher.state not in NO_REFRESH_STATES and not voucher.invoice_id:
                # Ignore manuel values
                vals = voucher._ignore_manual_fields(vals)
                
                # Set raw voucher text
                vals['raw_voucher_text'] = voucher._get_raw_voucher_text(voucher.voucher_id)
               
                # Update voucher
                voucher.write(vals)
                self._update_line_items(voucher.id, raw_voucher.get('line_items', []))
                self.env.cr.commit()
            elif not voucher:
                # Set raw voucher text
                vals['raw_voucher_text'] = voucher._get_raw_voucher_text(vals['voucher_id'])

                # Create voucher
                voucher = self.create(vals)
                voucher._attach_pdf()
                self._create_line_items(voucher.id, raw_voucher.get('line_items', []))
                self.env.cr.commit()
            elif voucher.invoice_id:
                voucher.state = 'generated'
        except:
            self.env.cr.rollback()
            error_message  = 'Something went wrong when generating voucher.: {error}'.format(error=sys.exc_info()[1]) 
            _logger.exception(error_message)
    
    @api.multi
    def _move_attachment(self, attachment):
        attachment.write({'res_model': self._name, 'res_id': self.id})

    @api.multi
    def _get_attachment(self):
        attachment = False
        if self.attachment_ids:
            attachment = self.attachment_ids[0].datas.decode('utf-8')
        return attachment

    @api.multi
    def _set_attachment(self, file_name, file_data, mimetype=False):
        self.ensure_one()
        attachment = {
                'name': file_name,
                'datas': base64.encodestring(file_data),
                'datas_fname': file_name,
                'res_model': 'invoicescan.voucher',
                'res_id': self.id,
                'type': 'binary',
                'mimetype': mimetype
            }
        try:
            self.env['ir.attachment'].create(attachment)
        except AccessError:
            error_message = 'Was not able to store document ({file_name}) as attachment: {error_content}'.format(file_name=file_name, error_content=attachment['name'])
            raise error_message
        except:
            error_message = 'Unexpected error occurred when trying to attach document ({file_name}): {error_content}'.format(file_name=file_name, error_content=sys.exc_info()[1])
            raise error_message
    
    @api.multi
    def _get_raw_voucher_text(self, voucher_id):
        return self._get_scan_provider().get_voucher_text(voucher_id) if voucher_id else ''

    @api.multi
    def _attach_pdf(self):
        self.ensure_one()
        pdf = self._get_scan_provider().get_voucher_pdf(self.voucher_id)
        if pdf:
            file_name = 'invoicescan' + '-' + str(self.voucher_id) + '.pdf'
            self._set_attachment(file_name, pdf, 'application/pdf')
        else:
            error_message = 'Was not able to get the PDF file from invoice scan: voucher id ({voucher_id})'.format(voucher_id=self.voucher_id)
            raise error_message
        
    @api.multi
    def _update_line_items(self, voucher_id, line_items):
        # Clear lines and create new once
        voucher_lines = self.env['invoicescan.voucher.line'].search([('voucher_id', '=', voucher_id)])
        if voucher_lines:
            voucher_lines.unlink()
        self._create_line_items(voucher_id, line_items)
    
    @api.multi
    def _create_line_items(self, voucher_id, line_items):
        for item in line_items:
            vals = self._convert_voucher_values(item.get('fields', ''), self.env['invoicescan.voucher.line'])
            vals['line_id'] = item.get('feature_id')
            vals['voucher_id'] = voucher_id
            self.env['invoicescan.voucher.line'].create(vals)
    
    @api.multi
    def _convert_voucher_values(self, data, model):    
        values = {}
        for field in data:
            code = field.get('code', False)
            value = field.get('value', False) if field.get('value', False) else False
            if code and hasattr(model, code):
                # Convert currency values to positive
                if code in MONETARIES:
                    value = abs(float(value)) if value else 0.0
                
                # Avoid provider sending unsupported types
                if code == 'voucher_type':
                    value = VOUCHER2INVOICE.get(value, 'in_invoice')
                values[code] = value
        return values
    
    @api.multi
    def _ignore_manual_fields(self, vals):
        if self.voucher_type and vals.get('voucher_type', False):
            del vals['voucher_type']
        if self.catalog_debitor_id and vals.get('catalog_debitor_id', False):
            del vals['catalog_debitor_id']
        return vals

    @api.multi
    def _get_scan_provider(self):
        if not self.invoice_scan_provider:
            self.invoice_scan_provider = self.env['invoicescan.bilagscan']
        return self.invoice_scan_provider
    
    @api.multi
    def get_references(self):
        refs = []
        if self.voucher_number:
            refs.append(self.voucher_number)
        if self.reference:
            refs.append(self.reference)
        if self.purchase_order_number:
            refs.append(self.purchase_order_number)
        return ', '.join(refs)

    @api.multi
    def action_refresh_voucher(self):
        if self.state not in NO_REFRESH_STATES and self.voucher_id:
            voucher = self._get_scan_provider().get_voucher(self.voucher_id)
            if voucher:
                self.create_voucher(voucher)
    
    @api.multi
    def action_create_invoice(self):
        if self.state in ('deleted', 'failed'):
            self = self.sudo()
            self.env['account.invoice'].with_context(create_voucher_ids=self).generate_invoices()
            if self.error_message:
                raise UserError(_(self.error_message))

    @api.multi
    def action_open_invoice(self):
        if self.invoice_id:
            [action] = self.env.ref('niova_invoice_scan.action_voucher_vendor_bill').read()
            if self.voucher_type == 'in_refund':
                ctx = {'default_type': 'in_refund', 'type': 'in_refund', 'journal_type': 'purchase'}
            else:
                ctx = {'default_type': 'in_invoice', 'type': 'in_invoice', 'journal_type': 'purchase'}
            action['res_id'] = self.invoice_id.id
            action['context'] = ctx
            return action
    
    # ----------------------------------------
    # Mail Thread
    # ----------------------------------------
    @api.multi
    def _get_mail_attachments(self, msg_dict):
        attachments = []
        body = msg_dict.get('body', '')
        for attachment in msg_dict.get('attachments', []):
            result = body.find('data-filename="' + attachment.fname +'"')
            if result == -1:
                attachments.append(attachment)
        return attachments

    @api.multi
    def upload_attachment_2_voucher(self, file_name, attachment, vals):
        if self and not vals:
            voucher = self
        else:
            voucher = self.sudo().create(vals)
        
        if hasattr(attachment, '_name') and attachment._name == 'ir.attachment':
            voucher._move_attachment(attachment)
        else:
            voucher._set_attachment(file_name, attachment)
        return voucher

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        if custom_values is None:
            custom_values = {}
        note = msg_dict.get('subject', '')
        email = tools.email_split(msg_dict.get('email_from', False))[0]
        user = self.env['res.users'].search([('groups_id', 'in', [self.env.ref('base.group_user').id]), '|', ('login', 'ilike', email), ('email', 'ilike', email)], limit=1)

        # Create voucher for each attachment
        custom_values.update({
            'state': 'upload',
            'note': note,
            'upload_user_id': user.id if user else False,
            'upload_email': email
        })
        
        # Get attachments but not those that are in the body
        attachments = self._get_mail_attachments(msg_dict)
        
        # Remove body and attachment to avoid messages notes to have a message and attachments
        msg_dict.update({'attachments': [],
                         'body': ''})
        if not attachments:
            res = super(ScannedVoucher, self).message_new(msg_dict, custom_values)
        else:
            for attachment in attachments:
                vals = custom_values.copy()
                res = super(ScannedVoucher, self).message_new(msg_dict, custom_values)
                res.upload_attachment_2_voucher(attachment.fname, attachment.content, {})
        return res


class VoucherLines(models.Model):
    _name = 'invoicescan.voucher.line'
    _description = 'Invoice Scan Line'
    
    quantity = fields.Float(string="Quantities", default=0.0)
    unit_price = fields.Float(string="Price pr. Unit", default=0)
    amount = fields.Monetary(string="Amount Scanned", default=0, currency_field='currency_id')
    description = fields.Char(string="Product Description", default='')
    ex_vat_amount = fields.Monetary(string="Net Amount", default=0, currency_field='currency_id')
    incl_vat_amount = fields.Monetary(string="Gross Amount", default=0, currency_field='currency_id')
    account_id = fields.Integer(help="Account Id")
    vat_percentage = fields.Float(string="The Scanned Vat Percent", default=0.0)
    discount_percentage = fields.Float(string="Discount Percentage")
    discount_amount = fields.Float(string="Discount Amount")
    
    line_id = fields.Integer(string='Line ID')
    voucher_id = fields.Many2one('invoicescan.voucher', string="Voucher Ids", required=True, readonly=True, ondelete='cascade')
    currency_id = fields.Many2one('res.currency', related='voucher_id.currency_id', string="Voucher Currency", readonly=True)