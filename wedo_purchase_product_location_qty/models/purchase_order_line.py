# Copyright 2020 WeDo Technology
# Website: http://wedotech-s.com
# Email: apps@wedotech-s.com
# Phone:00249900034328 - 00249122005009
from odoo import models, fields
from dateutil.relativedelta import relativedelta
from datetime import datetime

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_stock_quant_ids = fields.One2many('stock.quant', 'product_id', related='product_id.stock_quant_ids')

    def product_info(self, product_id, product_stock_quant_ids):
        locations= self.env['stock.location'].search_read([('usage','=','internal')],['id','name'])
        data=[]
        total={'qty':0, 'last_week_qty':0, 'last_month_qty': 0}
        for location in locations:
            domain = [('id', 'in', [quant_id for quant_id in product_stock_quant_ids]), ('location_id', '=', location['id']),]
            last_week_cons_domain = [("product_id", "=", product_id),
		    		     ("picking_id.picking_type_id.code","in",['outgoing','internal']),
		    		     ("state", "=", "done"),("location_id", "=",location['id']),
				     ("date", ">=", datetime.now() - relativedelta(days=7))]
            last_month_cons_domain = [("product_id", "=", product_id),
		    		     ("picking_id.picking_type_id.code","in",['outgoing','internal']),
		    		     ("state", "=", "done"),("location_id", "=",location['id']),
				     ("date", ">=", datetime.now() - relativedelta(days=30))]
            last_week_cons = self.env['stock.move.line'].search_read(last_week_cons_domain, ['qty_done'])
            last_month_cons = self.env['stock.move.line'].search_read(last_month_cons_domain, ['qty_done'])
            last_week_qty = last_week_cons and [line.get('qty_done') for line in last_week_cons][0] or 0
            last_month_qty = last_month_cons and [line.get('qty_done') for line in last_month_cons][0] or 0
            quant= self.env['stock.quant'].search_read(domain, ['quantity'])
            qty = quant and quant[0]['quantity'] or 0
            data.append({'name':location['name'], 'qty':qty, 'last_week_qty':last_week_qty , 'last_month_qty':last_month_qty})
            total['qty'] += qty
            total['last_week_qty'] += last_week_qty
            total['last_month_qty'] += last_month_qty
        data.append({'name':'Total', 'qty': total['qty'], 'last_week_qty':total['last_week_qty'], 'last_month_qty': total['last_month_qty']})
        return data

