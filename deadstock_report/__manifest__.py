{
    'name': 'dead stock report',
    'version': '1.0',
    'category': 'inventory',
    'sequence': 60,
    'summary': 'shows the product having dead moves',
    'description': "It shows purchase history of product in purchase line",
    'author':'aswathy',
    'depends': ['base','account','stock'],
    'data': ['wizard/dead_stock_wizard.xml'
      ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
