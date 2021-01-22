# -*- coding: utf-8 -*-
from odoo import http

# class OvSaleStatus(http.Controller):
#     @http.route('/ov_sale_status/ov_sale_status/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ov_sale_status/ov_sale_status/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ov_sale_status.listing', {
#             'root': '/ov_sale_status/ov_sale_status',
#             'objects': http.request.env['ov_sale_status.ov_sale_status'].search([]),
#         })

#     @http.route('/ov_sale_status/ov_sale_status/objects/<model("ov_sale_status.ov_sale_status"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ov_sale_status.object', {
#             'object': obj
#         })