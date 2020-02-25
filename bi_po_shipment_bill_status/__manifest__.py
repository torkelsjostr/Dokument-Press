# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Shipment and Bill Status in Odoo',
    'version': '12.0.0.0',
    'category': 'Purchase',
    'summary': 'This module helps the user to get the status of shipment and vendor bill of purchase order also available filter for a purchase order with full or partial shipped, fully or partially paid.',
    'description': """This module helps the user to get the status of shipment and vendor bill of purchase order also available filter for a purchase order with full or partial shipped, fully or partially paid.
        
        purchase status
        purchase order status in Odoo
        shipment status in Odoo
        bill status in odoo
        purchase order status in odoo
        po status
        purchase shipment status
        purchase order status 
        status of purchase order status 
        status of Purchase Shipment
        status of Bill
        


        """,
    'price': 000,
    'currency': 'EUR',
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'depends': ['base','purchase','stock'],
    'data': [
            # 'security/ir.model.access.csv',
            'views/main_delivery_invoice.xml',
            
            ],
    'installable': True,
    'auto_install': False,
    "images":["static/description/Banner.png"],
    "live_test_url" : 'https://youtu.be/BzixceRLkUc'
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
