{
    'name': 'Product Modifications',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 1,
    'author': "Allion Technologies PVT Ltd",
    'website': 'http://www.alliontechnologies.com/',
    'summary': 'Adding new custom fields to the product table',
    'description': """Adding new fields according to client's requirements""",
    'depends': ['base',
                'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_modifications_view.xml',
        'views/predifined_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}