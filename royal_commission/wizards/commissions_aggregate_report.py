from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime
import base64
import xlsxwriter


class CommissionsAggregateReport(models.TransientModel):
    _name = 'commissions.aggregate.report'

    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date", required=True)
    state = fields.Selection([('confirm', 'Confirmed'), ('vendor_bill', 'Vendor Bill'), ('paid', 'Paid'), ('calculated', 'Calculated')], required=True)

    report_file = fields.Binary('File', readonly=True)
    report_name = fields.Text(string='File Name')
    is_printed = fields.Boolean('Printed', default=False)

    def export_commission_xlsx(self, fl=None):
        """commission report"""
        if fl == None:
            fl = ''

        fl = self.print_commission()

        my_report_data = open(fl, 'rb+')
        f = my_report_data.read()
        values = {
            'name': 'Commission Aggregate Report' + '.xlsx',
            'res_model': 'ir.ui.view',
            'res_id': False,
            'type': 'binary',
            'public': True,
            'datas': base64.encodestring(f),
        }
        attachment_id = self.env['ir.attachment'].sudo().create(values)
        download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }

    def print_commission(self):
        """Printing commission report"""
        # "Setting name for the report"
        report = 'Commission Aggregate Report' + '.xlsx'
        workbook = xlsxwriter.Workbook(report)

        # Create worksheet 1
        worksheet = workbook.add_worksheet('Commission Aggregate Report')
        worksheet.set_landscape()

        heading = workbook.add_format({'bold': True, 'align': 'center', 'font_size': '14'})
        heading_2 = workbook.add_format({'bold': True, 'align': 'left', 'font_size': '12'})
        font_right = workbook.add_format(
            {'align': 'right', 'valign': 'vcenter', 'font_size': 10, 'num_format': '#,##0.00', 'border': 1})
        font_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'font_size': 10, 'border': 1})
        font_center_bold = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'font_size': 10, 'bold': True, 'border': 1})
        font_right_bold = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'font_size': 10, 'num_format': '#,##0.00', 'bold': True})
        font_left_bold = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'font_size': 10, 'num_format': '#,##0.00', 'bold': True})

        worksheet.set_column('A:S', 16)
        worksheet.set_row(0, 20)

        row = 0
        col = 0

        # Write data on the worksheet
        worksheet.write(row, col, " ", heading)
        worksheet.merge_range(row, col, row, col + 3,  "Aggregation Report ", heading)

        col = 0
        row = 3

        worksheet.write(row, col, "Name", font_center_bold)
        worksheet.write(row, col + 1, "Product", font_center_bold)
        worksheet.write(row, col + 2, "Author", font_center_bold)
        worksheet.write(row, col + 3, "Sum(SEK)", font_center_bold)

        row += 1

        commissions = self.env['commission'].search([('start_date', '>=', self.start_date), ('end_date', '<=', self.end_date), ('state', '=', self.state)])
        if not commissions:
            raise UserError("There are no records for the given period.")

        for commission in commissions:
            worksheet.write(row, col, commission.name, font_center)
            worksheet.write(row, col + 1, commission.product_id.name, font_right)
            worksheet.write(row, col + 2, commission.author_id.name, font_right)
            worksheet.write(row, col + 3, commission.total_commission, font_right)
            row += 1
        row += 2
        worksheet.write(row, col + 2, "Total", font_left_bold)
        worksheet.write(row, col + 3, sum(commissions.mapped('total_commission')), font_right_bold)
        workbook.close()
        return report

