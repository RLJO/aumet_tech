# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'Product Multi Barcodes',
    'category': 'Base',
    'version': '1.0',
    'price': 30.00,
    'currency': 'EUR',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'description': """Product with multiple barcodes.""",
    'website': "http://www.acespritech.com",
    'summary': 'Product with multiple barcodes',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/multi_barcodes.xml',
        'views/product_view.xml',
        'views/multi_barcodes_assets.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
