# -*- coding: utf-8 -*-
{
    'name': "Aumet Inventory",
    'summary': """Lot Expiry Date In Inventory Line""",
    'description': """ Lot Expiry Date In Inventory Line
                    Lot Expiry Date In Inventory report
                    Lot Expiry Date in stock quant 
    """,
    'author': "Ihab Shhadat",
    'website': "",
    'category': 'Inventory/Inventory',
    'depends': ['stock'],
    'data': [
        'views/stock_inventory_views.xml',
        'views/stock_quant_views.xml',

        'report/report_stockinventory.xml',

    ],
    "auto_install": False,
    "installable": True,
}
