# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import UserError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_tax_adjustment = fields.Boolean(
        string='Cuenta de Ajuste de impuesto'
    )
    is_other_discount = fields.Boolean(
        string='Cuenta de Otros descuentos'
    )

    @api.constrains('is_tax_adjustment')
    def _check_tax_adjustment(self):
        if self.search_count([('is_tax_adjustment', '=', True), ('id', '!=', self.id)]) >= 1:
            raise UserError(
                u"Ya existe un registro de tipo 'Cuenta de Ajuste de impuesto'\n"
                u"Cuenta: {}".format(self.search(
                    [('is_tax_adjustment', '=', True), ('id', '!=', self.id)], limit=1).display_name)
            )

    @api.constrains('is_other_discount')
    def _check_other_discount(self):
        if self.search_count([('is_other_discount', '=', True), ('id', '!=', self.id)]) >= 1:
            raise UserError(
                u"Ya existe un registro de tipo 'Cuenta de Otros descuentos'\n"
                u"Cuenta: {}".format(self.search(
                    [('is_other_discount', '=', True), ('id', '!=', self.id)], limit=1).display_name)
            )
