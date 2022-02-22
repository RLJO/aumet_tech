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
    'depends': ['flexipharmacy', ],
    'data': [
        # 'data/alternate_product_ids_cron.xml',
        'views/active_ingredient.xml',
        'views/assets.xml',
    ],
    "auto_install": False,
    "installable": True,
}
