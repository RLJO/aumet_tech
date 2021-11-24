# -*- coding: utf-8 -*-
{
    'name': "Aumet flexiPharmacy",
    'summary': """Auto fill alternative product based on active ingredient""",
    'description': """
        Auto fill alternative product based on active ingredient
    """,
    'author': "Ihab Shhadat",
    'website': "",
    'category': 'Point of Sale',
    'depends': ['flexipharmacy', 'base', 'point_of_sale', 'sale_management', 'barcodes', 'stock', 'purchase', 'bus',
                'hr_attendance', 'account', 'pos_hr', 'product_expiry'],
    'data': [
        'views/active_ingredient.xml'
    ],
    "auto_install": False,
    "installable": True,
}
