# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ApiForm(models.Model):
    _name = 'api.form'
    _rec_name = 'goods_owner_id'

    username = fields.Char("Username")
    password = fields.Char("Password")
    goods_owner_id = fields.Integer("Goods owner id")
    url = fields.Char("URL")
    name = fields.Selection([
        ('product', 'Product'),
        ('purchase_order', 'Purchase Order'),
        ('sale_order', 'Sale Order'),
        ('get_sale_order', 'Get Sale Order'),
        ('get_purchase_order', 'Get Purchase Order'),
    ], default="product", string="Type")

    @api.model
    def create(self, vals_list):
        """this function is to check already the 'name' is exists in the records"""
        records = self.env['api.form'].search([])  # search for records in model
        for record in records:  # loops the records
            if record.name == vals_list.get('name'):  # checks if new record name already in a record
                raise ValidationError("you cannot create a record with the same name.")  # if exists raise an
                # validation error

        return super(ApiForm, self).create(vals_list)  # returns the superclass create

    @api.multi
    def write(self, vals_list):
        """this function is to deny modification of the 'name' in the records"""
        records = self.env['api.form'].search([])  # search for records in the model
        for record in records:  # loops the records
            if record.name == vals_list.get('name'):  # checks if name already exists
                raise ValidationError("you cannot modify the name of the record.")  # if exists, raise an error

        return super(ApiForm, self).write(vals_list)  # returns the super class

