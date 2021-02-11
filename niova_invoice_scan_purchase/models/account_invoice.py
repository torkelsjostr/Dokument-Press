# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova IT ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova IT ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
import sys
from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    # -------------------------------------------------------------------------
    # ONCHANGE METHODS AND COMPUTES
    # ------------------------------------------------------------------------- 
    @api.onchange('state', 'partner_id', 'invoice_line_ids')
    def _onchange_allowed_purchase_ids(self):
        result = super(AccountInvoice, self)._onchange_allowed_purchase_ids()
        '''
        Override of origin method
        '''
        # A PO can be selected only if at least one PO line is not already in the invoice
        purchase_line_ids = self.invoice_line_ids.mapped('purchase_line_id')
        purchase_ids = self.invoice_line_ids.mapped('purchase_id').filtered(lambda r: r.order_line <= purchase_line_ids)

        domain = [('invoice_status', 'in', ['to invoice', 'no']),
                  ('company_id', '=', self.company_id.id)]
        if self.partner_id:
            domain += [('partner_id', 'child_of', self.partner_id.id)]
        if purchase_ids:
            domain += [('id', 'not in', purchase_ids.ids)]
        result['domain'] = {'purchase_id': domain}
        return result
    
    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------        
    @api.multi
    def action_add_purchase_lines(self):
        self._add_invoice_lines('purchase')

    # -------------------------------------------------------------------------
    # ATTACHMENTS
    # -------------------------------------------------------------------------
    @api.multi
    def _auto_attach_invoice_lines(self):
        res = False
        if self.partner_id and not self.invoice_line_ids:
            # First do purchase order line attachment
            if self.partner_id.property_invoice_automation_purchase:
                try:
                    res = self._attach_invoice_lines('purchase')
                    self.env.cr.commit()
                except:
                    self.env.cr.rollback()
                    _logger.exception('Invoice (invoice id: {invoice_id}) did not add invoice lines due to an unexpected error: {error_content}'.format(error_content=sys.exc_info()[1], invoice_id=self.id))
            
            # If non was found then do normal flow
            if not res and not self.partner_id.property_invoice_automation_purchase:
                res = super(AccountInvoice, self)._auto_attach_invoice_lines()
        return res

    @api.multi         
    def _attach_invoice_lines(self, attach_type):
        res = False
        if attach_type == 'purchase':
            res = self._add_purchase_orders()
        return super(AccountInvoice, self)._attach_invoice_lines(attach_type) if not res else res

    @api.multi
    def _add_purchase_orders(self):
        self.ensure_one()
        if not self.voucher_id:
            return False
        try:
            new_lines = self.env['account.invoice.line']
            PurchaseOrder = self.env['purchase.order']
            for purchase_order in self.voucher_id.get_purchase_references():
                po = PurchaseOrder.search([('name', '=', purchase_order),
                                           ('company_id', '=', self.company_id.id)], limit=1)
                if po:
                    new_lines = self._add_purchase_order_line(po, new_lines)
            if new_lines:
                self.invoice_line_ids += new_lines
                self._onchange_origin()
                self.payment_term_id = self.purchase_id.payment_term_id

                # Apply the taxes
                self._onchange_invoice_line_ids()
                return True
        except:
            _logger.exception("Purchases was not added to vendor bill: %s", sys.exc_info()[1])
        return False
         
    @api.multi
    def _add_purchase_order_line(self, purchase, new_lines):
        # Add missing partner if it exist in the purchase
        if not self.partner_id:
            self.partner_id = purchase.partner_id.id

        for line in purchase.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
            data = self._prepare_invoice_line_from_po_line(line)
            
            # Cash the lines if it is an user action
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line
        return new_lines