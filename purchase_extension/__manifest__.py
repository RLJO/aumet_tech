# -*- coding: utf-8 -*-
{
    'name': 'Aumet - Purchase Extension',
    'category': 'Purchase',
    "description": "Purchase",
    'version': '1.3',
    'depends': ['purchase_stock', 'product', 'stock'],
    'data': [
        'views/purchase_order_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
