# -*- coding: utf-8 -*-
{
    'name': 'Aumet - Purchase Extension',
    'category': 'Purchase',
    "description": "Purchase",
    'version': '1.3',
    'depends': ['purchase_stock', 'product', 'stock','purchase'],
    'data': [
        'security/groups.xml',
        'views/purchase_order_view.xml',
        'security/groups.xml',


    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
