# -*- coding: utf-8 -*-
{
	'name': "Invoice Details on Product",
	"author": "Edge Technologies",
	'version': "12.0.1.0",
	'category': "Product",
	'summary': "Apps for user to see invoice quantity and invoice amount on product. ",
	'description': """invoice quantity on product invoice amount on product invoice amount and invoice quantity on product invoice amount and quantity on product invoice detail on product product invoice link invoice product link
					""",
    "license" : "OPL-1",
	"live_test_url":'https://youtu.be/zKxHNKuaIUg',
	"images":['static/description/main_screenshot.png'],
    'depends': ['base', 'product','account','sale_management','purchase'],
	'data': [
				'views/product_invoice_link_view.xml',
			],
	'installable': True,
	'auto_install': False,
	'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
