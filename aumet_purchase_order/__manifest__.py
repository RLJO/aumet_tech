# -*- coding: utf-8 -*-
{
    'name': 'Purchase Excel Report',
    'version': '14.0',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'summary': 'Excel sheet for Purchase Order',
    'description': """ Purchase order excel report
When user need to print the excel report in purchase order select the purchase order list and
user need to click the "Purchase order Excel Report" button and message will appear.select the "Print Excel report"button
for generating the purchase order excel file""",
    'depends': [
        'purchase', 'sales_team', 'report_xlsx'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'report/report_action.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
