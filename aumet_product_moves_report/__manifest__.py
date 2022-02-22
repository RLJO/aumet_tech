# -*- coding: utf-8 -*-
{
    'name': "Aumet - Product Moves Report",

    'summary': """Report for product stock moves""",

    'description': """""",

    'author': "Aumet",
    'website': "https://www.aumet.com",

    'category': 'Warehouse',
    'version': '14.0.1.0',

    'depends': ['base', 'stock', 'stock_account'],

    'data': [
        'wizard/product_move_wizard.xml',
        'views/report.xml',
        'views/product_moves_report.xml',
        'data/data.xml',
        'security/ir.model.access.csv'
    ],
}
