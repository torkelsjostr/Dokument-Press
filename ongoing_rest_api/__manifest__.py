{
    'name': 'Ongoing WMS API Connector',
    'version': '1.0',
    'sequence': 1,
    'author': "Allion Technologies PVT Ltd",
    'website': 'http://www.alliontechnologies.com/',
    'summary': 'This Module connects Odoo with Ongoing WMS',
    'description': """This Module connects Odoo with Ongoing WMS""",
    'depends': ['stock', 'sale', 'purchase', 'customer_modification', 'product_modifications', 'account_intrastat'],
    'data': [
        'data/server_action.xml',
        'data/ongoing_api_config_data.xml',
        'security/ir.model.access.csv',
        'views/resource_views.xml',
        'views/api_form_view.xml',
        'views/inherit_sales_and_purchase_view.xml',
        'views/inherit_warehouse_view.xml',
     ],
    'installable': True,
    'application': True,
    'auto_install': False,
}