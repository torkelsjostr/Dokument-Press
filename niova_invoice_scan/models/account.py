# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
import sys
from odoo import models, api, fields, _
import logging
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)

ROUNDING_DECIMAL = 3


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    voucher_id = fields.Many2one('invoicescan.voucher', string='Voucher Id', ondelete='set null', readonly=True)
    partner_id = fields.Many2one('res.partner', 
                                 string='Partner', 
                                 change_default=True,
                                 required=False,
                                 readonly=True, 
                                 states={'draft': [('readonly', False)],
                                         'open': [('required', True)],
                                         'paid': [('required', True)],
                                         'cancel': [('required', True)]},
                                 track_visibility='always')
    
    auto_validated = fields.Boolean(string='Automatically Validated', default=False, readonly=True)
    control_value = fields.Monetary(string="Control Value", default=0, currency_field='currency_id', compute='_compute_control_value', readonly=True)       
    payment_date = fields.Date(related='voucher_id.payment_date', readonly=True)
    purchase_reference = fields.Char(related='voucher_id.reference', readonly=True)
    total_amount_incl_vat = fields.Monetary(related='voucher_id.total_amount_incl_vat', readonly=True)
    total_vat_amount_scanned = fields.Monetary(related='voucher_id.total_vat_amount_scanned', readonly=True)
    total_amount_excl_vat = fields.Monetary(related='voucher_id.total_amount_excl_vat', readonly=True)
    voucher_company_name = fields.Char(related='voucher_id.company_name', readonly=True)
    voucher_line_ids = fields.One2many(related='voucher_id.voucher_line_ids', readonly=True)
    voucher_line_count = fields.Integer(string='Scanned Lines Count', compute='_compute_voucher_line_count', readonly=True)
    duplicated_invoice_ids = fields.Many2many('account.invoice', 'invoice_related_invoice_rel', 'invoice_id','invoice_related_id', string='Duplicated Invoice IDs', readonly=True)
    default_currency_used = fields.Boolean(string='Default Currency is Used', default=False, readonly=True)
        
    # -------------------------------------------------------------------------
    # PROCESSING
    # -------------------------------------------------------------------------
    @api.multi
    def generate_invoices(self):
        InvoiceScan = self.env['invoicescan.voucher']
        
        # Get vouchers
        vouchers = InvoiceScan.get_ready_vouchers()
        if not vouchers:
            return 
        
        completed_vouchers = []
        for voucher in vouchers:
            # Create invoice
            invoice = self._create_invoice(voucher)
            
            # Continue if the invoice creation failed
            if not invoice:
                continue
            
            # Save voucher ID to report to voucher provider
            completed_vouchers.append(voucher.voucher_id)
            
            # Post process invoice
            company_id = invoice.company_id.id
            invoice.with_context(company_id=company_id, force_company=company_id)._post_process_generated_invoice()
            
        # Report to voucher provider
        InvoiceScan.report_as_done()
        _logger.info('Invoice scan: Successfully created {count} invoices: {voucher_ids}'.format(count=len(completed_vouchers), voucher_ids=", ".join(str(i) for i in completed_vouchers)))

    @api.multi
    def _create_invoice(self, voucher):
        invoice = False
        try:
            inv_type = voucher.voucher_type
            vals = {
                'type': inv_type,
                'state': 'draft',
                'voucher_id': voucher.id,
                'reference': voucher.get_references(),
                'date_invoice': voucher.invoice_date,
                'default_currency_used': voucher.default_currency
                }
            vals = self._check_duplicated_invoices(voucher, vals)
            vals = self._add_currency(vals, voucher)
            vals = self._add_fik(vals, voucher)
            vals = self._add_company(vals, voucher)
            # Add partner must be after a company has been selected
            vals = self._add_partner_values(vals, voucher)
            vals = self._add_journal(vals)
            
            # Create invoice
            invoice = self.with_context(default_type=inv_type, type=inv_type, company_id=vals.get('company_id'), force_company=vals.get('company_id')).create(vals)
            invoice._post_process_invoice()
            invoice._post_process_voucher(voucher)
        except:
            self.env.cr.rollback()
            error_message = 'Invoice (voucher id: {voucher_id}) was not created due to an unexpected error: {exception_log}'.format(exception_log=sys.exc_info()[1], voucher_id=voucher.id)
            voucher.write({'error_message': error_message,
                           'state': 'failed'})
        self.env.cr.commit()
        return invoice

    @api.multi
    def _post_process_voucher(self, voucher):
        # Attach PDF to invoice
        self._move_attachment(voucher, self)
        
        # Add notes
        self._add_note(voucher)
        
        # Clear error message and set invoice id and state
        voucher.write({'invoice_id': self.id,
                       'error_message': '',
                       'state': 'generated'})
    
    @api.multi
    def _post_process_invoice(self):
        self.ensure_one()
        self._onchange_payment_term_date_invoice()
        
    @api.multi
    def _post_process_generated_invoice(self):
        for invoice in self:
            #-------------------#
            # ---- Features ----#
            #-------------------#
            
            #Attach auto generated invoice line or voucher lines
            invoice._auto_attach_invoice_lines()
            
            # Auto validate invoice
            invoice._auto_validate()

    @api.multi
    def _add_note(self, voucher):
        note = ''
        if voucher.payment_method:
            note = '<strong>Recommended payment method</strong>: {payment_method}<br/>'.format(payment_method=voucher.payment_method.encode('utf-8'))
        if voucher.note:
            note = note + '<strong>Invoice note</strong>: {note}'.format(note=voucher.note.encode('utf-8'))
        if note:
            self.message_post(body=_(note))

    # -------------------------------------------------------------------------
    # ONCHANGE METHODS AND COMPUTES
    # -------------------------------------------------------------------------
    @api.depends('total_amount_incl_vat', 'amount_total')
    def _compute_control_value(self):
        for invoice in self:
            control_value = invoice.amount_total - invoice.voucher_id.total_amount_incl_vat
            invoice.control_value = control_value
            
    @api.onchange('currency_id')
    def _onchange_currency(self):
        self.default_currency_used = False
    
    @api.depends('voucher_line_ids')
    def _compute_voucher_line_count(self):
        for invoice in self:
            invoice.voucher_line_count = len(invoice.voucher_line_ids)
    
    @api.multi
    def _compute_quantity(self, quantity):
        if quantity:
            return quantity
        return 1
    
    @api.multi
    def _compute_unit_price(self, amount, qty, discount_percentage, discount_amount):
        if not amount:
            return 0.0, 0.0
        
        unit_price = round(amount/qty, ROUNDING_DECIMAL)
        return self._compute_discount(unit_price, discount_amount, discount_percentage)
    
    @api.multi
    def _compute_discount(self, unit_price, discount_amount, discount_percentage):
        if discount_percentage:
            discount_percentage = round(discount_percentage, ROUNDING_DECIMAL)
        elif discount_amount:
            discount_percentage = round(discount_amount/(unit_price + discount_amount)*100, ROUNDING_DECIMAL)
        else:
            return unit_price, 0.0
        
        percentage = 100-discount_percentage
        if float_compare(percentage, 0.0, 0.01) == 1:
            unit_price = unit_price/percentage*100
        discount_amount = round(discount_percentage/100 * unit_price, ROUNDING_DECIMAL)
        return unit_price, discount_percentage
    
    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------
    @api.multi
    def action_voucher_wizard(self):
        self.ensure_one()
        compose_form = self.env.ref('niova_invoice_scan.view_voucher_wizard_form', False)
        return {
            'name': _('Scanned Voucher'),
            'res_model': 'invoicescan.voucher',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'res_id': self.voucher_id.id
        }
         
    @api.multi
    def action_add_scanned_lines(self):
        self._add_invoice_lines('lines')
    
    @api.multi
    def action_add_single_line(self):
        self._add_invoice_lines('one_line')
    
    @api.multi
    def _add_invoice_lines(self, attach_type):
        if not self.partner_id:
            raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
        elif self.invoice_line_ids:
            raise UserError(_("You cannot add lines because there are already applied invoice lines."))
        company_id = self.company_id.id
        self.with_context(company_id=company_id, force_company=company_id)._attach_invoice_lines(attach_type)
    
    @api.multi
    def action_clear_invoice_lines(self):
        self.invoice_line_ids.unlink()
        # Remove the taxes
        self._onchange_invoice_line_ids()
    
    @api.multi
    def rematch_partner(self):
        domain = [('voucher_id.company_name', '!=', ''),
                  ('partner_id', '=', False)]
        invoices = self.search(domain)
        for invoice in invoices:
            vals = {}
            company_id = invoice.company_id
            vals = self._add_partner_values(vals, invoice.voucher_id, company_id)
            if vals.get('partner_id'):
                invoice.write(vals)
                # Post process invoice
                invoice.with_context(company_id=company_id.id, force_company=company_id.id)._post_process_generated_invoice()
                invoice._cr.commit()

    # -------------------------------------------------------------------------
    # INVOICE INITIALIZATIONS
    # -------------------------------------------------------------------------
    def _check_duplicated_invoices(self, voucher, vals):
        domain = ['|', ('voucher_id', '=', voucher.voucher_id),
                       ('reference', '=', voucher.get_references()),
                       ('voucher_id.joint_payment_id', '=', voucher.joint_payment_id),
                       ('voucher_company_name', '=', voucher.company_name)]
        
        # Check if there already is an voucher created
        duplicated_invoices = self.search(domain)
        if duplicated_invoices:
            invoice_ids = []
            for duplicated_invoice in duplicated_invoices:
                invoice_ids.append(duplicated_invoice.id)
            
            vals['duplicated_invoice_ids'] = [(6, 0, invoice_ids)]
        return vals
    
    @api.multi
    def _prepare_scanned_invoice_line(self, new_lines, quantity, description, voucher_line=False):
        context = {'journal_id': self.journal_id.id, 
                   'type': 'in_invoice',
                   'default_type': 'in_invoice',
                   'partner_id': self.partner_id.id,
                   'company_id': self.company_id.id,
                   'force_company': self.company_id.id}
        invoice_line = self.env['account.invoice.line'].with_context(context)
        account_id = invoice_line._default_account()
        account_analytic_id = invoice_line._default_analytic_account()
        quantity = self._compute_quantity(quantity)
        
        if voucher_line:                       
            unit_price, discount_percentage = self._compute_unit_price(voucher_line.amount, quantity, voucher_line.discount_percentage, voucher_line.discount_amount)
        else:
            unit_price = self.total_amount_excl_vat if self.total_amount_excl_vat else self.total_amount_incl_vat
            discount_percentage = 0.0
        
        line_values = {
            'invoice_id': self.id,
            'voucher_line_id': voucher_line.id if voucher_line else False,
            'name': description or 'No description found',
            'account_id': account_id,
            'account_analytic_id': account_analytic_id,
            'price_unit': unit_price,
            'quantity': quantity,
            'discount': discount_percentage
        }

        new_line = new_lines.new(line_values)
        new_line._set_additional_fields(self)
        new_line._onchange_account_id()
        return new_line
    
    @api.multi
    def _add_currency(self, vals, voucher):
        if voucher.currency_id.id:
            vals['currency_id'] = voucher.currency_id.id
        return vals
    
    @api.multi
    def _add_fik(self, vals, voucher):
        if voucher.payment_code_id and voucher.payment_id and voucher.joint_payment_id:
            if self._fields.get('fik_number', False):
                vals['fik_number'] = '+%s<%s+%s<' % (voucher.payment_code_id, voucher.payment_id, voucher.joint_payment_id)
            
            if self._fields.get('fik_payment_code', False) and voucher.payment_code_id in dict(self._fields.get('fik_payment_code').selection):
                vals['fik_payment_code'] = voucher.payment_code_id
            if self._fields.get('fik_payment_id', False):
                vals['fik_payment_id'] = voucher.payment_id
            if self._fields.get('fik_creditor_id', False):
                vals['fik_creditor_id'] = voucher.joint_payment_id
        return vals
    
    @api.multi
    def _add_account(self, vals, company_id, default_account_id=False):
        account_id = False
        if default_account_id:
            account_id = default_account_id
        else:
            account = self.env['ir.property'].with_context(force_company=company_id).get('property_account_payable_id', 'res.partner')
            if account:
                account_id = account.id
        vals['account_id'] = account_id
        return vals
    
    @api.multi
    def _add_company(self, vals, voucher):
        if voucher.company_id:
            company_id = voucher.company_id.id
        else:
            default_company = self.env['res.company'].search([('default_debitor', '=', True)], limit=1)
            if default_company:
                company_id = default_company.id
            else:
                company_id = 1
                    
        vals['company_id'] = company_id
        return vals

    @api.multi
    def _add_journal(self, vals):
        if vals['company_id']:
            journal_id = self.with_context(company_id=vals['company_id'], type=vals['type'])._default_journal().id
        else:
            journal_id = 1

        vals['journal_id'] = journal_id
        return vals

    @api.multi
    def _add_partner_values(self, vals, voucher, company=False):
        company_id = company.id if company else vals['company_id']
        search_criteria = ('supplier', '=', True)
        partner = self.env['res.partner'].with_context(force_company=company_id, company_id=company_id)
        
        # First find by VAT
        if voucher.company_vat_reg_no:
            domain = [search_criteria, ('vat', '=ilike', voucher.company_vat_reg_no)]
            partner = partner.search(domain, limit=1)
        
        # Else try with naming
        if not partner and voucher.company_name:
            domain = [search_criteria, '|', ('name', 'ilike', voucher.company_name), ('alias', 'ilike', voucher.company_name)]
            partner = partner.search(domain, limit=1)

        # Default values
        vals = self._add_account(vals, company_id)
        if partner:
            vals['partner_id'] = partner.id
            
            if not partner.property_account_payable_id:
                raise Exception('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
            vals = self._add_account(vals, company_id, partner.property_account_payable_id.id)
 
            if partner.property_supplier_payment_term_id:
                vals['payment_term_id'] = int(partner.property_supplier_payment_term_id.id)

        return vals

    def _convert_amount_currency(self, from_amount, to_currency):
        date = self.date_invoice or fields.Date.today()
        return self.currency_id._convert(from_amount, to_currency, self.company_id, date)
    
    # -------------------------------------------------------------------------
    # ATTACHMENTS
    # -------------------------------------------------------------------------
    @api.multi
    def _move_attachment(self, from_document, to_document):
        attachments = self.env['ir.attachment'].search([('res_model', '=', from_document._name),
                                                        ('res_id', '=', from_document.id)])
        if attachments:
            # move attachments
            attachments.write({'res_model': to_document._name, 'res_id': to_document.id})
            
    @api.multi
    def _auto_attach_invoice_lines(self):
        if self.partner_id and not self.invoice_line_ids:
            try:
                self._attach_invoice_lines(self.partner_id.property_invoice_automation)
                self.env.cr.commit()
            except:
                self.env.cr.rollback()
                _logger.exception('Invoice (invoice id: {invoice_id}) did not add invoice lines due to an unexpected error: {error_content}'.format(error_content=sys.exc_info()[1], invoice_id=self.id))
    
    @api.multi         
    def _attach_invoice_lines(self, attach_type):
        # If unselect is made, then unlink all voucher lines
        if not self.partner_id:
            raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
                
        new_lines = self.env['account.invoice.line']
        if attach_type == 'one_line':
            default_description = self.partner_id.property_invoice_default_line_description
            if not default_description:
                raise UserError(_("You have to set a Default Invoice Line Description on the Vendor."))
            new_line = self._prepare_scanned_invoice_line(new_lines, 1, default_description, False)
            new_lines += new_line
        
        elif attach_type in ('lines', False, '', 'full'):
            for line in self.voucher_id.voucher_line_ids - self.invoice_line_ids.mapped('voucher_line_id'):
                new_line = self._prepare_scanned_invoice_line(new_lines, line.quantity, line.description, line)
                new_lines += new_line
        
        if new_lines:
            self.invoice_line_ids += new_lines
            # Apply the taxes
            self._onchange_invoice_line_ids()
            return True
        return False
    
    # -------------------------------------------------------------------------
    # VALIDATIONS
    # -------------------------------------------------------------------------
    @api.multi
    def _auto_validate(self):
        if self._validate_invoice_criteria():
            try:
                # To be able to set another approver for automation
                if self._context.get('approval_user_id', False):
                    self.user_id = self._context.get('approval_user_id')
                
                # Do validation
                self.with_context(auto_validate=True).action_invoice_open()
                self.auto_validated = True
            except:
                self.env.cr.rollback()
                error_message = 'Auto validation failed due to: {error_content}'.format(error_content=sys.exc_info()[1])
                self.message_post(body=_(error_message))
            self.env.cr.commit()
    
    @api.multi
    def _validate_invoice_criteria(self):
        result = False
        for invoice in self:
            # Check voucher
            voucher = invoice.voucher_id
            if not voucher:
                break

            # Check partner
            partner = invoice.partner_id
            if not partner:
                break

            # Check automation
            if partner.property_invoice_automation != 'full':
                break
            
            # Check vat matches
            if partner.property_invoice_validation_vat and voucher.company_vat_reg_no != partner.vat:
                break
            
            # Check validation limit
            amount_untaxed = invoice.amount_untaxed
            if partner.currency_id != invoice.currency_id:
                amount_untaxed = invoice._convert_amount_currency(amount_untaxed, partner.currency_id)
            if partner.property_invoice_validation_limit and float_compare(amount_untaxed, partner.property_invoice_validation_limit, 0.01) == 1:
                break
            result = True
        return result
    
    @api.multi
    def _validate_control_value(self):
        if self._context.get('force_validate_invoice', False):
            return False
        
        for invoice in self.filtered(lambda inv: inv.type in ('in_invoice', 'in_refund')):
            # Check voucher
            voucher = invoice.voucher_id
            if not voucher:
                break
            
            # Check partner
            partner = invoice.partner_id
            if not partner:
                break
            
            # Check control value
            partner_currency = partner.currency_id
            deviation_max = partner.property_invoice_validation_deviation
            deviation_min = -deviation_max
            if partner_currency != invoice.currency_id:
                deviation_max = invoice._convert_amount_currency(deviation_max, partner_currency)
                deviation_min = invoice._convert_amount_currency(deviation_min, partner_currency)
            
            if not deviation_min <= self.control_value <= deviation_max:
                # If this is a auto validation, then throw exception, else open wizard
                if self._context.get('auto_validate', False):
                    raise UserError(_('The difference between Control Value and Total is to high.'))
                else:
                    action = self.env.ref('niova_invoice_scan.action_account_invoice_control').sudo()
                    wiz = self.env['account.invoice.control'].create({'invoice_id': invoice.id})
                    action.res_id = wiz.id
                    return action.read()[0]
            return False
        
    # -------------------------------------------------------------------------
    # ODOO ORIGINS
    # -------------------------------------------------------------------------
    @api.multi
    def unlink(self):
        vouchers = self.env['invoicescan.voucher']
        for invoice in self:
            if invoice.voucher_id:
                # Move attachment
                self._move_attachment(invoice, invoice.voucher_id)
                vouchers |= invoice.voucher_id
        if vouchers:
            vouchers.write({'state': 'deleted'})
        return super(AccountInvoice, self).unlink()

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        company_id = self.company_id.id
        partner = self.partner_id if not company_id else self.partner_id.with_context(force_company=company_id)
        if partner:
            self.fiscal_position_id = self.env['account.fiscal.position'].with_context(force_company=company_id).get_fiscal_position(partner.id)
        return res
    
    @api.multi
    def action_invoice_open(self):
        action = self._validate_control_value()
        if action:
            return action
        return super(AccountInvoice, self).action_invoice_open()
    
    @api.multi
    def name_get(self):
        """ Many2many display name"""
        vals = []
        for record in self:
            if record.number:
                val = record.number
            else: 
                val = 'BILL/ID/{id}'.format(id = record.id)
            vals.append((record.id, val))
        return vals
    
    @api.onchange('payment_term_id', 'date_invoice')
    def _onchange_payment_term_date_invoice(self):
        date_invoice = self.date_invoice
        if not date_invoice:
            date_invoice = fields.Date.context_today(self)
        if self.payment_term_id:
            pterm = self.payment_term_id
            pterm_list = pterm.with_context(currency_id=self.company_id.currency_id.id).compute(value=1, date_ref=date_invoice)[0]
            self.date_due = max(line[0] for line in pterm_list)
        elif self.voucher_id:
            if self.voucher_id.payment_date:
                self.date_due = self.voucher_id.payment_date

        if self.date_due and (date_invoice > self.date_due):
            self.date_due = date_invoice
            

class AccountInvoiceLine(models.Model):
    """ Override AccountInvoice_line to add the link to the scanned voucher line it is related to"""
    _inherit = 'account.invoice.line'

    @api.model
    def _default_analytic_account(self):
        if self._context.get('partner_id'):
            partner = self.env['res.partner'].with_context(self._context).browse(self._context.get('partner_id'))
            if partner.property_invoice_default_account_analytic_id:
                return partner.property_invoice_default_account_analytic_id.id
        return False
    
    price_unit = fields.Float(digits=dp.get_precision('Invoicescan Price Unit'))
    account_id = fields.Many2one(default=lambda self: self._default_account())
    account_analytic_id = fields.Many2one(default=_default_analytic_account)
    voucher_line_id = fields.Many2one('invoicescan.voucher.line', 'Scanned Order Line', ondelete='set null', readonly=True)
    voucher_id = fields.Many2one('invoicescan.voucher',related='voucher_line_id.voucher_id', string='Scanned Voucher', store=False, readonly=True, related_sudo=False,
        help='Associated Scanned Voucher.')
    
    # -------------------------------------------------------------------------
    # ODOO ORIGINS
    # -------------------------------------------------------------------------
    @api.model
    def _default_account(self):
        if self._context.get('partner_id'):
            partner = self.env['res.partner'].with_context(self._context).browse(self._context.get('partner_id'))
            if partner.property_invoice_default_account_expense_id:
                return partner.property_invoice_default_account_expense_id.id
        return super(AccountInvoiceLine, self)._default_account()
    
    @api.onchange('uom_id')
    def _onchange_uom_id(self):
        old_price_unit = False
        if self.voucher_id:
            old_price_unit = self.price_unit if self.price_unit else False
        res = super(AccountInvoiceLine, self)._onchange_uom_id()
        self.price_unit = old_price_unit if old_price_unit else self.price_unit
        return res
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        old_name = False
        if self.voucher_id:
            old_name = self.name if self.name else False
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        self.name = old_name if old_name else self.name
        return res
    
    @api.onchange('account_id')
    def _onchange_account_id(self):
        super(AccountInvoiceLine, self)._onchange_account_id()
        if not self.product_id and self.partner_id and self.partner_id.property_invoice_default_line_tax_id:
            self.invoice_line_tax_ids = [(6, 0, self.partner_id.property_invoice_default_line_tax_id._ids)]


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.multi
    def action_sync_invoice_scan(self):
        self.env['invoicescan.scheduler'].process_scanned_vouchers()