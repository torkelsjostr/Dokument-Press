# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
import xlwt
from odoo.exceptions import Warning, ValidationError
import datetime
from odoo import tools
import math
from io import StringIO
import io
import base64

try:
	import xlwt
except ImportError:
	xlwt = None

class js_excel(models.TransientModel):

	_name = 'xls.excel'

	def create_excel(self,ids, model,fields_string,fields_row,selection_field):

		if len(ids) == 0:
			raise ValidationError("Please Select Records, Without Records Excel Cannot be Printed")
		else:

			models = self.env[model].browse(ids)
			workbook = xlwt.Workbook()
			worksheet = workbook.add_sheet('Sheet 1')
			filename = 'Detail Report.xls'
			values = self.env[model].search_read([('id','in', ids)],fields_row)

			selection_value = [];

			for key in selection_field:
				for value in key:
					selection_value.append(value)

			row = 0
			for lines in fields_string: 
				worksheet.write(0, row,lines,xlwt.easyxf('font:bold on'))
				row+=1

			row_2 = 2
			col_0 = 0
			
			for value in values:
				for lines in fields_row:
					sql = "SELECT ttype FROM ir_model_fields ir inner join ir_model mo on (ir.model_id = mo.id) WHERE ir.name='%s' and mo.model='%s';" %( str(lines),str(model));
					try:
							self.env.cr.execute(sql)
							[val] = self.env.cr.fetchone()
					except:
							val = None
					if lines:
						if val == 'datetime':
							if value[lines] == False:
								worksheet.write(row_2, col_0, 0, xlwt.easyxf("font: name Liberation Sans"))
							else:
									date_time = value[lines].strftime('%d-%m-%Y')
									worksheet.write(row_2, col_0, date_time, xlwt.easyxf("font: name Liberation Sans"))

						elif val == 'date':
							if value[lines] == False:
								worksheet.write(row_2, col_0, 0, xlwt.easyxf("font: name Liberation Sans"))
							else:
									date_time = value[lines].strftime('%d-%m-%Y')
									worksheet.write(row_2, col_0, date_time, xlwt.easyxf("font: name Liberation Sans"))
												
						elif val == 'selection':
								for values in selection_value:
									if value[lines] == values[0]:
										worksheet.write(row_2, col_0, values[1], xlwt.easyxf("font: name Liberation Sans"))
										break

						elif val == 'many2one' and isinstance(value[lines], tuple):
								worksheet.write(row_2, col_0, value[lines][1], xlwt.easyxf("font: name Liberation Sans"))

						else:
								worksheet.write(row_2, col_0, value[lines], xlwt.easyxf("font: name Liberation Sans"))
							
						col_0 +=1
				row_2 +=1
				col_0 = 0

		fp = io.BytesIO()
		workbook.save(fp)
		export_id = self.env['sale.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
		fp.close()
		return export_id.id
		
class sale_excel(models.TransientModel):

	_name= "sale.excel"

	excel_file = fields.Binary('Excel Report', readonly=True)
	file_name = fields.Char('Excel File', size=64)

