# -*- coding: utf-8 -*-

{

    'name': "Aumet - POS UOM Selection",

    'summary': """

       """,

    'description': """

    - Add ability to select UOM from lot/serial screen.

    """,

    'website': "",

    'category': 'Point of Sale',

    'version': '14.0.0.3',

    # any module necessary for this one to work correctly

    'depends': ['point_of_sale', 'aumet_pos_multi_uom_price', 'flexipharmacy'],


    # always loaded

    'data': [

        'views/assets.xml',

    ],


    'qweb': [

        'static/src/xml/Screens/PackLotLineScreen/PackLotLineScreen.xml',

        'static/src/xml/Screens/PackLotLineScreen/SinglePackLotLine.xml',

    ],

    "auto_install": False,

    "installable": True,

}