# -*- coding: utf-8 -*-
{
    'name': "Aumet Purchase",

    'summary': """
        Customizations at purchase module for Aumet Pharmacy""",

    'description': """
        Customizations at purchase module for Aumet Pharmacy
    """,

    'author': "Aumet",
    'website': "http://www.aumet.com",

    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'stock', 'purchase_stock', 'account', 'sales_team', 'report_xlsx', 'purchase_stock',
                'product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_views.xml',
        'views/partner_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
