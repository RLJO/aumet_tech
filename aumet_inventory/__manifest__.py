# -*- coding: utf-8 -*-
{
    'name': "Aumet Inventory",
    'summary': """Lot Expiry Date In Inventory Line""",
    'description': """ Lot Expiry Date In Inventory Line
                    Lot Expiry Date In Inventory report
                    Lot Expiry Date in stock quant ,
                    Add Default value(Product Type,Avaliable POS , Tracking , Expiration date ),Rename Internal Ref to Code ,Add New feilds (strength,doesage_form,granular_unit,manufacturer)
    """,
    'author': "Ihab Shhadat",
    'category': 'Inventory/Inventory',
    'depends': ['product', 'product_expiry', 'point_of_sale', 'flexipharmacy',
                'purchase', 'sale',
                'product_expiry',
                'account', 'stock', 'stock_account', 'report_xlsx'],

    'data': [
        'security/groups.xml',
        # 'security/ir.model.access.csv',
        'views/adjustment_views.xml',
        'views/stock_inventory_views.xml',
        'views/stock_quant_views.xml',
        'views/in_adjustment_views.xml',
        'views/out_adjustment_views.xml',
        'views/opening_adjustment_views.xml',
        'views/product_views.xml',
        'report/report_stockinventory.xml',
        'data/data.xml',
        # 'report/shortfalls_report_template.xml',
        # 'wizard/shortfalls_wizard_view.xml',
        "views/stock_production_lot_view.xml"
    ],
    "auto_install": False,
    "installable": True,

}
