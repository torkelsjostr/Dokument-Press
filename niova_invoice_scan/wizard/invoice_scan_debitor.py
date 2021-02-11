# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova Group ApS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova Group ApS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class InvoiceScanDebitor(models.TransientModel):
    _name = 'invoicescan.debitor'
    _description = 'Invoice Scan Debitor'
    
    company_id = fields.Many2one('res.company', string='Default Debitor', required=True)
    company_ids = fields.Many2many('res.company', string='Debitors', required=True)
    
    @api.multi
    def action_upload_debitors(self):
        if not self.company_ids:
            raise UserError("No company has been selected.")
        
        if self.company_id not in self.company_ids:
            raise UserError("Default company must be one of the selected debitors.")
        
        debitors = []
        for company in self.company_ids:
            partner = company.partner_id
            
            def convert_values(value):
                return str(value) if value else ''
            
            debitor = {
                  "id": convert_values(company.id),
                  "group_id": 1,
                  "name": convert_values(company.name),
                  "alias": convert_values(partner.alias),
                  "address_1": convert_values(partner.street),
                  "address_2": convert_values(partner.street2),
                  "zip_code": convert_values(partner.zip),
                  "city": convert_values(partner.city),
                  "country": convert_values(partner.country_id.name),
                  "email": convert_values(company.email),
                  "keyWords": [
                    {
                      "type": "cvr",
                      "value": convert_values(company.company_registry)
                    }
                  ]
                }
            debitors.append(debitor)

        status, _, _ = self.env['invoicescan.bilagscan'].set_debitors(debitors)
        
        if not status:
            raise UserError(_("The debitors were not successful uploaded to Invoice Scan."))
        
        # Clear default debitor
        self.env['res.company'].search([]).write({'default_debitor': False})
        
        # Set new default debitor
        self.company_id.write({'default_debitor': True})
        
        return {'type': 'ir.actions.act_window_close'}