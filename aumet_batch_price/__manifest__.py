# -*- coding: utf-8 -*-
{
    'name': "aumet_batch_price",

    'summary': """
        allow multi price depend on Batch (Lot/Expiry Date) 
    """,

    'author': "Ihab Shhadat",
    'website': "https://pharmacy.aumet.com/",

    # Categories can be used to filter modules in modules listing
    'category': 'Point of Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['flexipharmacy', 'aumet_inventory'],

    'data': [
        'views/view_production_lot.xml',
    ],

}
