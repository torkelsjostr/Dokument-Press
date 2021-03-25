import base64
import os
from datetime import datetime
from datetime import *
from io import BytesIO

import xlsxwriter
from PIL import Image as Image
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import xlsxwriter.utility


class deadstockwiz(models.TransientModel):
    _name = 'dead.stock.wiz'
    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    warehouse = fields.Many2many('stock.location', string="Location", required=True)




    #check stock moves of all product in given daterange,from givenlocation
    @api.multi
    def get_data(self):

        list = []
        domain = []
        date_from = self.date_from
        date_to = self.date_to
        location_ids = [l.id for l in self.warehouse]
        domain.append(('location_id', 'in', location_ids))
        location_dest_ids = []
        dest = self.env['stock.location'].search([('usage', '=', 'customer')])
        for i in dest:
            location_dest_ids.append(i.id)

        domain.append(('location_dest_id', 'in', location_dest_ids))
        products = self.env['product.product'].search([])
        for product in products:
            stock_moves = self.env['stock.move'].search(
                domain + [('state', '=', 'done'), ('product_id', '=', product.id),
                          ('date', '<=', date_to), ('date', '>', date_from)])



            if not stock_moves:

                vals = {'name': product.name,

                        'barcode': product.barcode,
                        'sale_price': product.lst_price,
                        'cost_price': product.standard_price
                        }

                qty = 0
                for x in location_ids:

                    for temp in product.stock_quant_ids:

                        if temp.location_id.id == x:
                            qty = qty + temp.quantity
                vals['Quantity'] = qty
                if qty > 0:
                    list.append(vals)

        return list

    #passing product details and adding in report/worksheet
    @api.multi
    def get_item_data(self):
        file_name = _('Deadstock report.xlsx')
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)


        start_date = self.date_from
        end_date = self.date_to


        names = ""
        for loc in self.warehouse:
            name1=loc.name
            name2=loc.location_id.name
            name=name2+"/"+name1
            names = names + name
            names = names + ","
        names = names.rstrip(',')
        res = self.get_data()
        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 16})

        sub_heading_format = workbook.add_format({'align': 'left',
                                                  'valign': 'vleft',
                                                  'bold': True,
                                                  'size': 12})

        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        worksheet = workbook.add_worksheet('deadstock report.xlsx')
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)


        worksheet.merge_range('A1:E2', "Dead Stock Item Details",
                              heading_format)

        worksheet.merge_range('B3:E3', '%s' % (names))
        worksheet.write(2, 0, "Locations:", sub_heading_format)

        worksheet.write(3, 1, start_date, date_format)

        worksheet.write(3, 0, "Date From:", sub_heading_format)

        worksheet.write(4, 0, "Date To:", sub_heading_format)
        worksheet.write(4, 1, end_date, date_format)
        worksheet.write(6, 0, "Products", sub_heading_format)
        worksheet.write(6, 1, "Barcode", sub_heading_format)
        worksheet.write(6, 2, "Sale Price", sub_heading_format)

        worksheet.write(6, 3, "Cost Price", sub_heading_format)

        worksheet.write(6, 4, "Quantity", sub_heading_format)

        row = 8

        for i in res:
            worksheet.write(row, 0, i['name'])
            worksheet.write(row, 1, i['barcode'])
            worksheet.write(row, 2, i['sale_price'])

            worksheet.write(row, 3, i['cost_price'])
            worksheet.write(row, 4, i['Quantity'])

            row = row + 1

        workbook.close()
        file_download = base64.b64encode(fp.getvalue())
        fp.close()
        self = self.with_context(default_name=file_name, default_file_download=file_download)

        return {
            'name': 'Deadstock report Download',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'dead.stock.excel',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self._context,
        }


class deadstock_report_excel(models.TransientModel):
    _name = 'dead.stock.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('Download Report', readonly=True)