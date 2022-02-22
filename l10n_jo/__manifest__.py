# -*- encoding: utf-8 -*-

{
    'name': 'Aumet - Chart of Accounts ',
    'version': '14.0.0.0',
    'author': "aumet",
    'category': 'Localization',
    'description': """
     Arabic localization for most arabic countries.
    """,
    'depends': ['account', 'l10n_multilang'],
    'data': [
        'data/account_chart_template_data.xml',
        'data/account.account.template.csv',
        'data/l10n_ye_chart_data.xml',
        'data/account_chart_template_configure_data.xml',

    ],
    'demo': [
        'demo/demo_company.xml',
    ],
     'license': 'AGPL-3',
    'post_init_hook': 'load_translations',
}
