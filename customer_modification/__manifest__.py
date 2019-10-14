{
    'name': 'Customer Modifications',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 1,
    'author': "Allion Technologies PVT Ltd",
    'website': 'http://www.alliontechnologies.com/',
    'summary': 'Adding new custom fields to the customer table',
    'description': """Adding new fields & mapping some modification according to client's requirements""",
    'depends': ['base',
                'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/customer_groups_view.xml',
        'views/customer_vat_type_view.xml',
        'views/res_partners_modifications_view.xml',
     ],
    'installable': True,
    'application': True,
    'auto_install': False,
}