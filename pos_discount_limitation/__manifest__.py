# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Aumet - POS Discount Limit",
    "summary": """set limit for each user in the pos""",
    "version": "14.0.0.1",
    "category": "Sale",
    "author": """Aumet Team""",
    "license": "AGPL-3",
    "installable": True,
    'depends': ['pos_discount', 'point_of_sale', "pos_fixed_discounts"],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_discount_view.xml',
        'views/assets.xml',
    ],
}
