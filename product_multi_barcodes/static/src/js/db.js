odoo.define('flexipharmacy.mutlibarcode.db', function (require) {
    "use strict";

    var DB = require('point_of_sale.DB');
    var core = require('web.core');
    var rpc = require('web.rpc');

    var _t = core._t;
    
    DB.include({
        init: function(options){
            this._super.apply(this, arguments);
            this.product_template_barcode_id = {};
            this.get_barcode_by_id()
        },
        get_barcode_by_id: function(){
            var self = this;
            var barcode = {
                model: 'multi.barcodes',
                method: 'search_read',
                domain: [],
            }
            rpc.query(barcode).then(function(result){
                _.each(result, function(each_data){
                    self.product_template_barcode_id[each_data.id] = each_data
                })
                return result
            }).catch(function(){
                console.log("Connection lost");
            });
        },
        add_products: function(products){
            this._super.apply(this, arguments);
            for(var i = 0, len = products.length; i < len; i++){
                var product = products[i];
                if(product.multi_barcode_ids && product.multi_barcode_ids.length > 0){
                    var self = this;
                    _.each(product.multi_barcode_ids, function(barcode_line_id){
                        var barcode = self.product_template_barcode_id[barcode_line_id]
                        self.product_by_barcode[barcode.name] = product;
                    })
                }
            }
        },
    });
});