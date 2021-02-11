# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class AccountInvoiceChangeCompany(models.TransientModel):
    _name = 'account.invoice.change.company'
    _description = 'Account Invoice Change Company'
    
    new_company_id = fields.Many2one('res.company', string='New Company', required=True)
    
    @api.multi
    def _change_company(self, invoice, new_company):
        invoice = invoice.sudo()
        if invoice.state != 'draft' or new_company == invoice.company_id:
            return False
        
        # Change company
        invoice = invoice.with_context(force_company=new_company.id, company_id=new_company.id, type=invoice.type)
        invoice.company_id = new_company
        invoice.journal_id = invoice._default_journal().id
        if invoice.partner_id:
            invoice._onchange_partner_id()
        else:
            invoice.account_id = invoice._add_account({}, new_company.id).get('account_id')

        # Change invoice lines accounting
        for line in invoice.invoice_line_ids:
            line._onchange_product_id()
            line._onchange_account_id()
        
        # Apply the taxes
        invoice._onchange_invoice_line_ids()
        return True

    @api.multi        
    def action_change_company(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        
        for invoice in self.env['account.invoice'].browse(active_ids):
            status = self._change_company(invoice, self.new_company_id)
            if status:
                invoice._cr.commit()
                if len(active_ids) == 1:
                    # Return to list view, because we cannot look at an invoice in a different company
                    # when we stays in the old company
                    action = self.env.ref('account.action_invoice_tree2').read()[0]
                    return action
            elif len(active_ids) == 1:
                raise UserError(_("Not able to change company in state different from draft or has the same company."))
            else:
                invoice._cr.rollback()
        return {'type': 'ir.actions.act_window_close'}
    