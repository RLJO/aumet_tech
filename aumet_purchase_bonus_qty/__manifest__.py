{
    'name': 'Purchase Bonus Quantity',
    'category': 'Purchase',
    'summary': 'add Bonus Quantity field to PO',
    'description': """
    - Bonus Quantity field on PO
    - Create a Bill with Quantity
    - Update Inventory Valuation
    """,

    'category': 'Purchase',
    'depends': [
        'purchase', 'stock', 'purchase_stock', 'account'
    ],
    'data': [
        'views/purchase_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
