# -*- coding: utf-8 -*-
{
    'name': "Aumet Stock",

    'summary': """
        Inventory customizations for Aumet pharmacy
        """,

    'description': """
        Inventory customizations for Aumet pharmacy:
        1- Prevent negative stock
    """,

    'author': "Mahmoud Al Shaikh",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_product_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
