# -*- coding: utf-8 -*-

{
    'name': "Aumet - Barcode",
    'summary': "Use barcode scanners to process logistics operations",
    'description': """
This module enables the barcode scanning feature for the warehouse management system.
    """,
    'category': 'Operations/Inventory',
    'version': '1.0',
    'depends': ['barcodes', 'stock'],
    'data': [
        'views/stock_barcode_views.xml',
        'views/stock_inventory_views.xml',
        'views/stock_barcode_templates.xml',
        'data/data.xml',
    ],
    'qweb': [
        "static/src/xml/stock_barcode.xml",
        "static/src/xml/qweb_templates.xml",
    ],
    'installable': True,
    'application': True,
    'license': 'OEEL-1',
}
