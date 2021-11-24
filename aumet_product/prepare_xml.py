import math

import pandas as pd

file = pd.read_csv('data/product.template.csv').drop_duplicates(subset=["barcode"])

fields = ['name', 'purchase_ok', 'sale_ok', 'type', 'available_in_pos', 'barcode', 'default_code', 'qr_code',
          'list_price', 'standard_price', 'tracking', 'use_expiration_date',
          'categ_id', 'pos_categ_id']
counter = 1
for i in range(int(file.shape[0] / 500)):
    f = open("data/data_{i}.xml".format(i=i), "w+")
    f.write("<odoo>")
    x = file.keys()
    for col in file[i * 500:(i + 1) * 500].values:
        f.write('<record id="product_product_{counter}" model="product.product">'.format(counter=counter))
        dict_value = dict(zip(x, col))
        for item in fields:
            if type(dict_value[item]) == float:
                if not math.isnan(dict_value[item]):
                    f.write('<field name="{field_name}">{field_value}</field>'.format(field_name=item,
                                                                                      field_value=dict_value[item]))
            elif type(dict_value[item]) == str:
                f.write('<field name="{field_name}">{field_value}</field>'.format(field_name=item,
                                                                                  field_value=dict_value[item].replace(
                                                                                      '&', '/')))
            else:
                f.write('<field name="{field_name}">{field_value}</field>'.format(field_name=item,
                                                                                  field_value=dict_value[item]))
        f.write('</record>')
        counter += 1
    f.write("</odoo>")
    f.close()
f = open("data/data_63.xml", "w+")
f.write("<odoo>")
x = file.keys()

for col in file[63 * 500:].values:
    f.write('<record id="product_product_{counter}" model="product.product">'.format(counter=counter))
    dict_value = dict(zip(x, col))
    for item in fields:
        if type(dict_value[item]) == float:
            if not math.isnan(dict_value[item]):
                f.write('<field name="{field_name}">{field_value}</field>'.format(field_name=item,
                                                                                  field_value=dict_value[item]))
        elif type(dict_value[item]) == str:
            f.write('<field name="{field_name}">{field_value}</field>'.format(field_name=item,
                                                                              field_value=dict_value[item].replace(
                                                                                  '&', '/')))
        else:
            f.write('<field name="{field_name}">{field_value}</field>'.format(field_name=item,
                                                                              field_value=dict_value[item]))
    f.write('</record>')
    counter += 1
f.write("</odoo>")
f.close()
