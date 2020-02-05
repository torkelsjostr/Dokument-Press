# -*- coding: utf-8 -*-
# Copyright 2019 Linescripts Softwares (<http://www.linescripts.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields,api 
import xml.etree.ElementTree as PARSER
from xml.etree.ElementTree import ParseError
from  xml.etree.ElementTree import Element
import re
from odoo.exceptions import ValidationError



class Wizard(models.TransientModel):
	_name = 'lsaddcolumn.wizard'
	_description = "Select Fields for adding Column"

	column_fields_id = fields.Many2one('ir.model.fields',
					domain = "[('model','=',context.get('modelName')),('name','not in',context.get('fields_name'))]", 
					string="Select a field to add ?")
 
	#ok button click method after selecting the field from dropdown
	def ok_button_clicked(self):
		view = self.env['ir.ui.view'].search([('id','=',self._context['view_id'])])
	
		if view.inherit_id:
			view1 = self.env['ir.ui.view'].search([('id','=',view.inherit_id.id)])
			print(view1)
			view_str = view1.arch_base
			new_view = view_str.replace('</tree>','<field name="'+str(self.column_fields_id.name)+'"/></tree>')
			view1.write({'arch_base':new_view})

			return {
				'type': 'ir.actions.client',
				'tag': 'reload',
			}

		else:
			view_str = view.arch_base
			new_view = view_str.replace('</tree>','<field name="'+str(self.column_fields_id.name)+'"/></tree>')
			view.write({'arch_base':new_view})

			return {
			   'type': 'ir.actions.client',
				'tag': 'reload',
			}
