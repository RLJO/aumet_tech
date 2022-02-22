# -*- coding: utf-8 -*-
{
    'name': "Aumet Barcode",

    'summary': """
        Add GS1 Barcode Support into various modules
        """,

    'description': """
        Adding barcode functionality into a various modules in Odoo
        - Parse barcodes according to the GS1-128 specifications
        - Point Of Sale
        - Product Template (Soon)
        - Purchase Order (Soon)
        - Inventory Adjustment (Soon)
    """,

    'author': "Mahmoud Al Shaikh",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['barcodes', 'uom', 'point_of_sale', 'purchase', 'product','aumet_inventory'],

    # always loaded
    'data': [
        'data/barcodes_gs1_rules.xml',
        'views/barcodes_templates.xml',
        'views/barcodes_view.xml',
        'views/purchase.xml',
        'views/product_template.xml',
        'views/stock.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
