# noinspection PyStatementEffect
{
    'name': "Sale Line Stock",

    'sequence': 200,

    'summary': """Adds product's available stock to sale order line.""",

    'author': "Arxi",
    'website': "http://www.arxi.pt",

    'category': 'Sales',
    'version': '12.0.1.0.1',
    'license': 'OPL-1',
    'price': 0.00,
    'currency': 'EUR',

    'depends': ['stock', 'sale_management'],

    'data': [
        'views/sale_views.xml',
    ],

    'images': [
        'static/demo.gif',
        'static/description/banner.png',
    ],
}
