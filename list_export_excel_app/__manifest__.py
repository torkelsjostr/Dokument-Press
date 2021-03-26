# -*- coding: utf-8 -*-
{
	'name' : 'Export List View for All Application',
	'author':"Edge Technologies",
    'version': '12.0.1.0',
    'live_test_url': "https://youtu.be/xhLCyIR3YHI",
    "images":['static/description/main_screenshot.png'],
    'summary': 'Export List View with Details app is designed to export list view in xls report. This app helps user to print list view of all odoo applications with or without details in xls format.',
    'description' : """Export List View with Details app is designed to export list view in xls report. This app helps user to print list view of all odoo applications with or without details in xls format.


export records
export list view 
Web Export ListView XLS
Odoo export list view
Export views to PDF
Export the Pivot View
Export View XLSX
 list view export
 listview export
Export View PDF
Export current list view Odoo 11
Export records
export files
Export Product Stock in Excel
Export in Excel
Web Export Current View in Excel
Export Current View in Excel
Current View in Excel
Odoo Export Button View in Tree View
Export Templating
Add XLS export to accounting reports
xls list view export
xls export
XLS export to accounting reports





    """,
    "license" : "OPL-1",
    'depends' : ['base','base_setup'],
	'data' : [
		'security/ir.model.access.csv',
		'report/report.xml',
		'views/excel.xml',
		
	],
	'qweb' : ['static/src/xml/custom_button.xml'],
	'demo' : [],
	'installable' : 'True',
	'auto_install' : 'False',
	'price': 000,
    'currency': "EUR",
    'category': 'Extra Tools',
}	
