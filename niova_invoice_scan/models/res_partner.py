# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class Partner(models.Model):
    _inherit = 'res.partner'
    
    alias = fields.Char('Alias Name')
    
    # Automation
    property_invoice_automation = fields.Selection(
                                           [('none', 'No Automation'),
                                            ('lines', 'Apply Scanned Lines'),
                                            ('one_line', 'Generate One Invoice Line'),
                                            ('full', 'Apply Scanned Lines And Validate')],
                                           string='Degree of Automation',
                                           default='lines',
                                           company_dependent=True,
                                           help=" * The 'No Automation' disable all the automated features for handling vendor bills.\n"
                                                " * The 'Auto Apply Scanned Lines' applies scanned lines into the vendor bill.\n"
                                                " * The 'Auto Generate Invoice Line' generate a invoice line with the total amounts from the vendor bill.\n"
                                                " * The 'Apply Scanned Lines And Validate' applies scanned lines into the vendor bill and auto validate the vendor bill.\n")

    # Settings
    property_invoice_default_account_expense_id = fields.Many2one('account.account', string='Default Invoice Line Expense Account', company_dependent=True, help='This account will be used on the vendor bill lines as default')
    property_invoice_default_account_analytic_id = fields.Many2one('account.analytic.account', string='Default Invoice Line Analytic Account', company_dependent=True, help='This analytic account will be used on the vendor bill lines as default')
    property_invoice_default_line_description = fields.Char(string='Default Invoice Line Description', company_dependent=True, help='The default description on the invoice line')
    property_invoice_default_line_tax_id = fields.Many2one('account.tax',
                                                         company_dependent=True,
                                                         string='Default Invoice Line Tax',
                                                         domain=[('type_tax_use','!=','none'), '|', ('active', '=', False), ('active', '=', True)], 
                                                         help='Default taxes on invoice line.')
    
    # Validation criteria
    property_invoice_validation_deviation = fields.Float(string='Control Deviation (+/-)', currency_field='currency_id', default=0.0, company_dependent=True,
                                          help="This deviation value allows validation of vendor bills that have a differ from the control value with +/- the amount set.")
    property_invoice_validation_limit = fields.Float(string='Max Auto Validation Limit', currency_field='currency_id', default=0.0, company_dependent=True,
                                          help="This validation limit stops auto validation if the max amount is exceed. 0 is unlimited.")
    property_invoice_validation_vat = fields.Boolean(string='Auto Validate if VAT is matched', default=False,
                                          help="Auto validation of vendor bills will only succeed if the vendor is matched by the VAT number.")