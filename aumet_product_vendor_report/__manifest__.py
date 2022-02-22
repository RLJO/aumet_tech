# -*- coding: utf-8 -*-
{
    'name': "Aumet - Product By Vendor Report",

    'summary': """Report for product by vendor""",

    'description': """""",

    'author': "Aumet",
    'website': "https://www.aumet.com",

    'category': 'Warehouse',
    'version': '14.0.1.0',

    'depends': ['base', 'stock', 'stock_account'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/shortfall_wizard.xml',
        'wizard/purchase_vendor_wizard.xml',
        'wizard/vendor_product_wizard.xml',
        'report/product_report.xml',
        'views/purchase_vendor_report.xml',
        'views/shortfall_report.xml',
        'views/vendor_product_report.xml'],
}