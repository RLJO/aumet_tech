import pandas as pd

#
# file = pd.read_csv('data/product.template.csv').drop_duplicates(subset=["barcode"])
# print(file.columns)
# file.to_csv('data/product.template.csv', index=False)
# in_csv = 'data/product.template.csv'
# number_lines = sum(1 for row in (open(in_csv)))
# rowsize = 500
# for i in range(1, number_lines, rowsize):
#     df = pd.read_csv(in_csv,
#                      nrows=rowsize,  # number of rows to read at each loop
#                      skiprows=i)  # skip rows that have been read
#     out_csv = 'csv/data' + str(i) + '.csv'
#     df.to_csv(out_csv,
#               index=False,
#               header=['name', 'purchase_ok', 'sale_ok', 'type', 'available_in_pos', 'barcode',
#                        'default_code', 'qr_code', 'list_price', 'standard_price', 'tracking',
#                        'use_expiration_date', 'categ_id', 'pos_categ_id',
#                        'property_account_income_id', 'property_account_expense_id',
#                        'supplier_taxes_id', 'taxes_id'],
#             )  # size of data to append for each loop

data = pd.read_csv('csv/Aumet Pharmacy 4.11.csv')
data.dropna(subset=["GTIN (01)"], inplace=True)
lookups = pd.read_csv('csv/lookups.csv')

result = pd.merge(data,
                  lookups,
                  on='GTIN (01)')
new = data[~data['GTIN (01)'].isin(result['GTIN (01)'])]
result.to_csv('csv/result.csv', index=False, )
new.to_csv('csv/new.csv', index=False, )

