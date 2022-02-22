odoo.define('aumet_flexi.DB', function (require) {
"use strict";

var POS_db = require('point_of_sale.DB');
var rpc = require('web.rpc');

var models = require('point_of_sale.models');

models.load_fields('product.product',['ingredient_ids_name']);

 POS_db.include({
 _product_search_string: function(product){
        var str = product.display_name;
        if (product.barcode) {
            str += '|' + product.barcode;
        }
        if (product.default_code) {
            str += '|' + product.default_code;
        }
        if (product.description) {
            str += '|' + product.description;
        }
        if (product.description_sale) {
            str += '|' + product.description_sale;
        }
        if (product.ingredient_ids_name) {
            str += '|' + product.ingredient_ids_name;
        }
        str  = product.id + ':' + str.replace(/:/g,'') + '\n';
        return str;
    },
 })

});