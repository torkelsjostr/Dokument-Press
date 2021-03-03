from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime
import base64
import xlsxwriter


class CommissionsSettlementReport(models.TransientModel):
    _name = 'commissions.settlement.report'

    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date", required=True)
    author_id = fields.Many2one('commission.authors', string="Author")

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
            'name': 'Commission Settlement Report' + '.xlsx',
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
        report = 'Commission Settlement Report' + '.xlsx'
        workbook = xlsxwriter.Workbook(report)

        # Create worksheet 1
        worksheet = workbook.add_worksheet('Commission Settlement Report')
        worksheet.set_landscape()

        heading = workbook.add_format({'bold': True, 'align': 'center', 'font_size': '14'})
        heading_2 = workbook.add_format({'bold': True, 'align': 'left', 'font_size': '12'})
        font_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'font_size': 10, 'num_format': '#,##0.00'})
        font_right_bold = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'font_size': 10, 'num_format': '#,##0.00', 'bold': True})
        font_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        font_center_bold = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'font_size': 10, 'bold': True})

        worksheet.set_column('A:S', 16)
        worksheet.set_row(0, 20)

        row = 0
        col = 0

        # Write data on the worksheet
        worksheet.write(row, col, " ", heading)
        worksheet.merge_range(row, col, row, col + 9,  "Settlement Report ", heading)

        col = 0
        row = 3

        worksheet.write(row, col, "Name", font_center_bold)
        worksheet.write(row, col + 1, "Title", font_center_bold)
        worksheet.write(row, col + 2, "Beg. Inv.", font_center_bold)
        worksheet.write(row, col + 3, "End. Inv.", font_center_bold)
        worksheet.write(row, col + 4, "Receipts", font_center_bold)
        worksheet.write(row, col + 5, "Sold PCS", font_center_bold)
        worksheet.write(row, col + 6, "Free/Inv.adj/Scrap", font_center_bold)
        worksheet.write(row, col + 7, "Base", font_center_bold)
        worksheet.write(row, col + 8, "Amount", font_center_bold)
        worksheet.write(row, col + 9, "Currency", font_center_bold)

        row += 1

        commissions = self.env['commission'].search([('start_date', '>=', self.start_date), ('end_date', '<=', self.end_date)])
        if not commissions:
            raise UserError("There are no records for the given period.")
        for commission in commissions:
            worksheet.write(row, col, commission.name, font_center)
            worksheet.write(row, col + 1, commission.product_id.name, font_center)
            worksheet.write(row, col + 2, commission.product_id._compute_quantities_dict(lot_id=None, owner_id=None, package_id=None, to_date=self.start_date)[commission.product_id.id].get('qty_available'), font_right)
            worksheet.write(row, col + 3, commission.product_id._compute_quantities_dict(lot_id=None, owner_id=None, package_id=None, to_date=self.end_date)[commission.product_id.id].get('qty_available'), font_right)
            worksheet.write(row, col + 4, " ", font_right)
            worksheet.write(row, col + 5, commission.total_sales, font_right)
            worksheet.write(row, col + 6, " ", font_right)
            worksheet.write(row, col + 7, "Commission", font_center)
            worksheet.write(row, col + 8, commission.commission, font_right)
            worksheet.write(row, col + 9, commission.currency_id.name, font_right)
            row += 1
            for ded in commission.deduction_lines:
                worksheet.write(row, col, commission.name, font_center)
                worksheet.write(row, col + 1, commission.product_id.name, font_center)
                worksheet.write(row, col + 7, ded.name, font_center)
                worksheet.write(row, col + 8, ded.amount * -1, font_right)
                worksheet.write(row, col + 9, commission.currency_id.name, font_right)
                row += 1
            for all in commission.allowance_lines:
                worksheet.write(row, col, commission.name, font_center)
                worksheet.write(row, col + 1, commission.product_id.name, font_center)
                worksheet.write(row, col + 7, all.name, font_center)
                worksheet.write(row, col + 8, all.amount, font_right)
                worksheet.write(row, col + 9, commission.currency_id.name, font_right)
                row += 1
            worksheet.write(row, col, commission.name, font_center_bold)
            worksheet.write(row, col + 1, commission.product_id.name, font_center_bold)
            worksheet.write(row, col + 7, "Payable", font_center_bold)
            worksheet.write(row, col + 8, commission.total_commission, font_right_bold)
            worksheet.write(row, col + 9, commission.currency_id.name, font_right_bold)
            row += 1
        row += 2
        worksheet.write(row, col + 7, "Total Payable", font_center_bold)
        worksheet.write(row, col + 8, sum(commissions.mapped('total_commission')), font_right_bold)
        worksheet.write(row, col + 9, commissions[0].currency_id.name, font_right_bold)
        workbook.close()
        return report

