{
    'name': 'Aumet Pharmacy Debrand ',
    'description': 'Web & Favcion & Digist & Odoobot & Odoo.com &Email Template',
    'sequence': 1,
    'version': '14.0.0.0',
    'author': 'Aumet -walaa khaled ',

    'depends': ['web','digest','point_of_sale','account','auth_signup','mail','sale','hr','mail_bot','stock','base','sale_management','purchase','payment','mail_bot'],
    'data': [
        'data/auth_signup_data.xml',
        'data/digest_data.xml',
        'data/digest_tips_data.xml',
        'data/ir_cron_data.xml',
        'data/mail_channel_data.xml',
        'data/mail_data.xml',
        'data/portal_data.xml',
        'data/payment_data.xml',
        'views/templates.xml',
        'views/assets.xml',
        'views/pos_assets_index.xml',
        'views/partner_view.xml',
        'views/department_views.xml',
        'views/stock_orderpoint_views.xml',
        'views/res_company.xml',
        'views/stock_immediate_transfer_views.xml',
        'views/hr_employee_public_views.xml',



],
    'images': [
        'images/aumet-logo.png',
    ],
    "qweb": ["static/src/xml/base.xml",
             "static/src/xml/ErrorTracebackPopup.xml",
             "static/src/xml/ErrorPopup.xml ",
             "static/src/xml/ErrorBarcodePopup.xml",
             "static/src/xml/crash_manager.xml",

             ],
    'application': True,
    'installable': True,
}
