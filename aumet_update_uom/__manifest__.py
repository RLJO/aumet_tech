# -*- coding: utf-8 -*-
{
    "name": "Aumet - POS Update UOM",
    "summary": """The module allows the customers to make partial payment for their orders and the user can validate the invoice for partial payment in POS session.""",
    "depends": ['stock'],

    "data": [
        "security/ir.model.access.csv",
        'wizard/update_uom.xml',
        'wizard/update_product_uom.xml',
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}
