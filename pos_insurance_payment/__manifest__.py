# -*- coding: utf-8 -*-
{
    "name": "Aumet - POS Insurance Payment",
    "depends": ['wk_pos_partial_payment', 'point_of_sale', 'flexipharmacy'],
    "data": [
        'views/template.xml',
        'views/account_view.xml',
        'views/account_move_view.xml',
        'wizard/claim_report.xml',
        'security/ir.model.access.csv',
        'views/report.xml',
        'report/claim_report.xml',
        'views/account_move_report.xml',
        'views/res_config_setting.xml',
    ],
    "qweb": ['static/src/xml/pos.xml'],
    "application": True,
    "installable": True,
    "auto_install": False,
}
