from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime
import base64
import xlsxwriter


class CommissionsSettlementReport(models.TransientModel):
    _name = 'commissions.settlement.report'

    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date", required=True)
    commission_plan_id = fields.Many2one('commission.plan', string="Commission Plan")
    author_id = fields.Many2one('commission.authors', string="Author", related='commission_plan_id.author_id')
    product_id = fields.Many2one('product.product', string="Product", domain=[('type', '=', 'product')], related='commission_plan_id.product_id')

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
        font_left_bold = workbook.add_format(
            {'align': 'left', 'valign': 'vcenter', 'font_size': 10, 'bold': True})

        worksheet.set_column('A:S', 16)
        worksheet.set_row(0, 20)

        row = 0
        col = 0

        # Write data on the worksheet
        worksheet.write(row, col, " ", heading)
        worksheet.merge_range(row, col, row, col + 10,  "Settlement Report ", heading)

        worksheet.write(3, col, "Author : ", font_left_bold)
        worksheet.write(4, col, "Period : ", font_left_bold)
        worksheet.write(3, col + 1, self.commission_plan_id.author_id.name)
        worksheet.write(4, col + 1, str(self.start_date) + " to " + str(self.end_date))

        col = 0
        row = 6

        worksheet.write(row, col, "Reference", font_center_bold)
        worksheet.write(row, col + 1, "Title", font_center_bold)
        worksheet.write(row, col + 2, "Beg. Inv.", font_center_bold)
        worksheet.write(row, col + 3, "End. Inv.", font_center_bold)
        worksheet.write(row, col + 4, "Receipts", font_center_bold)
        worksheet.write(row, col + 5, "Sold PCS", font_center_bold)
        worksheet.write(row, col + 6, "On Order/Free/Inv.adj.", font_center_bold)
        worksheet.write(row, col + 7, "Remark", font_center_bold)
        worksheet.write(row, col + 8, "Amount", font_center_bold)
        worksheet.write(row, col + 9, "Currency", font_center_bold)
        worksheet.write(row, col + 10, "Equivalent SEK value", font_center_bold)

        row += 1

        commissions = self.env['commission'].search([('start_date', '>=', self.start_date), ('end_date', '<=', self.end_date), ('state', 'in', ['confirm']), ('commission_plan_id', '=', self.commission_plan_id.id)])
        if not commissions:
            raise UserError("There are no records for the given period.")
        for commission in commissions:
            beginning_inventory = commission.product_id._compute_quantities_dict(lot_id=None, owner_id=None, package_id=None, to_date=self.start_date)[commission.product_id.id].get('qty_available')
            ending_inventory = commission.product_id._compute_quantities_dict(lot_id=None, owner_id=None, package_id=None, to_date=self.end_date)[commission.product_id.id].get('qty_available')
            receipts_total = self._get_receipts_total(commission.product_id.id, self.start_date, self.end_date)
            worksheet.write(row, col, commission.name, font_center)
            worksheet.write(row, col + 1, commission.product_id.name, font_center)
            worksheet.write(row, col + 2, beginning_inventory, font_right)
            worksheet.write(row, col + 3, ending_inventory, font_right)
            worksheet.write(row, col + 4, receipts_total, font_right)
            worksheet.write(row, col + 5, commission.total_qty, font_right)
            worksheet.write(row, col + 6, (beginning_inventory) - (ending_inventory) + (receipts_total) - commission.total_qty, font_right)
            worksheet.write(row, col + 7, "Royalty", font_center)
            worksheet.write(row, col + 8, commission.commission, font_right)
            worksheet.write(row, col + 9, commission.currency_id.name, font_right)
            worksheet.write(row, col + 10, commission.currency_id.with_context(date=commission.exchange_rate_date).compute(commission.commission, commission.company_currency_id) if commission.currency_id.id != commission.company_currency_id.id else commission.commission, font_right)
            row += 1
            for ded in commission.deduction_lines:
                worksheet.write(row, col, commission.name, font_center)
                worksheet.write(row, col + 1, commission.product_id.name, font_center)
                worksheet.write(row, col + 7, ded.name, font_center)
                worksheet.write(row, col + 8, ded.amount * -1, font_right)
                worksheet.write(row, col + 9, commission.currency_id.name, font_right)
                worksheet.write(row, col + 10, commission.currency_id.with_context(date=commission.exchange_rate_date).compute(ded.amount, commission.company_currency_id) if commission.currency_id.id != commission.company_currency_id.id else ded.amount * -1, font_right)
                row += 1
            for all in commission.allowance_lines:
                worksheet.write(row, col, commission.name, font_center)
                worksheet.write(row, col + 1, commission.product_id.name, font_center)
                worksheet.write(row, col + 7, all.name, font_center)
                worksheet.write(row, col + 8, all.amount, font_right)
                worksheet.write(row, col + 9, commission.currency_id.name, font_right)
                worksheet.write(row, col + 10, commission.currency_id.with_context(date=commission.exchange_rate_date).compute(all.amount, commission.company_currency_id) if commission.currency_id.id != commission.company_currency_id.id else all.amount, font_right)
                row += 1
            worksheet.write(row, col, commission.name, font_center_bold)
            worksheet.write(row, col + 1, commission.product_id.name, font_center_bold)
            worksheet.write(row, col + 7, "Total", font_center_bold)
            worksheet.write(row, col + 8, commission.total_commission, font_right_bold)
            worksheet.write(row, col + 9, commission.currency_id.name, font_right_bold)
            worksheet.write(row, col + 10, commission.currency_id.with_context(date=commission.exchange_rate_date).compute(commission.total_commission, commission.company_currency_id) if commission.currency_id.id != commission.company_currency_id.id else commission.total_commission, font_right_bold)
            row += 1
        row += 2
        total_commission = sum(commissions.mapped('total_commission')) if sum(commissions.mapped('total_commission')) >= 0 else 0
        worksheet.write(row, col + 7, "Total Payable", font_center_bold)
        worksheet.write(row, col + 8, total_commission, font_right_bold)
        worksheet.write(row, col + 9, commissions[0].currency_id.name, font_right_bold)
        worksheet.write(row, col + 10, commission[0].currency_id.with_context(date=commission[0].exchange_rate_date).compute(total_commission, commission[0].company_currency_id) if commission[0].currency_id.id != commission[0].company_currency_id.id else total_commission, font_right_bold)
        workbook.close()
        return report

    def _get_receipts_total(self, product_id, start_date, end_date):
        """get receipts total"""
        orders = self.env['stock.picking'].search([('state', '=', 'done'), ('picking_type_code', '=', 'incoming')])
        purchase_orders_lines = orders.filtered(lambda x: x.date_done.date() >= start_date and x.date_done.date() <= end_date).mapped('move_ids_without_package')
        return sum(purchase_orders_lines.filtered(lambda x: x.product_id.id == product_id).mapped('quantity_done'))
