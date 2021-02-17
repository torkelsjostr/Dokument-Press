# Copyright 2020 WeDo Technology
# Website: http://wedotech-s.com
# Email: apps@wedotech-s.com
# Phone:00249900034328 - 00249122005009

{
    'name': "Purchase Product Consumption Info",
    'version': '13.0.1.0',
    'license': 'OPL-1',
    'author': 'WeDo Technology',
    'support': 'odoo.support@wedotech-s.com',
    'category': 'purchase',
    'sequence': 1,
    'depends': ['purchase','stock'],
    'summary': """
       Show info in Purchase lines to know available quantities, Last Week Consumption and Last Month Consumption for each location.
       """,
    'description': """
        RFQ and Purchase Order
        Allow to show these information in Purchase Lines for each location:
            Quantity Available
            Last Week Consumption
            Last Month Consumption
        """,
    'images': ['images/main_screenshot.png'],
    'data': [
        'views/purchase_view.xml',
        'views/templates.xml',
    ],
    'qweb': ['static/src/xml/qty_at_date.xml'],
    'application': True,
}

