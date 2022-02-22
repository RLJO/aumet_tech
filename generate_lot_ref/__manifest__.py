{
    "name": "Aumet - Generate Barcode AEU",
    "summary": """generate lot/serial ref number from po and search in the form poo line with show in the product move 
    report """,
    "version": "14.0.0.1",
    "category": "Tools",
    "author": """Aumet Team""",
    "license": "AGPL-3",

    "depends": ["purchase", "stock", "purchase_extension", "aumet_inventory"],
    "data": ["data/lot_sequence.xml",
             "views/product_move_view.xml",
             "views/stock_production_lot_view.xml",
             "views/in_stock_inventory_view.xml",
             "views/opening_stock_inventory_view.xml",
             "views/stock_production_lot_view.xml",
             "views/stock_move_view.xml",
             "report/pharmacy_barcode_pdf.xml",
             "report/pharmacy_barcode_zpl.xml",
             "report/barcode_report.xml",

             ],
    'application': False,
    'installable': True,
    'auto_install': True,
}
