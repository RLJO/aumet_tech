{
    'name': 'Bonus Quantity',
    'category': 'Purchase',
    'summary': 'add Bonus Quantity field to PO',
    'description': """
    - Bonus Quantity field on PO
    - Create a Bill with Quantity
    - Update Inventory Valuation
    """,
    'category': 'Purchase',
    'depends': ['sale', 'purchase', 'stock', 'purchase_stock', 'account'],
    'data':
    [
        'views/sale_order_view.xml',
        'views/purchase_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
