odoo.define('pos_multi_uom_price.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    var DB = require('point_of_sale.DB');
    DB.include({
        init: function (options) {
            this._super.apply(this, arguments);
            this.uom_by_product = {};
            this.product_by_tmpl_id = {};
        },

        get_qty_for_selected_uom: function(uom_obj, real_qty){
            var newQty = real_qty;
            if(uom_obj.uom_type == 'bigger'){
                newQty = (real_qty / uom_obj.factor_inv);
            }
            else if(uom_obj.uom_type == 'smaller'){
                newQty = (real_qty * uom_obj.factor);
            }
            else if(uom_obj.uom_type == 'reference'){
                newQty = real_qty;
            }
            return newQty;
        },

        get_product_by_tmpl_id: function (tmpl_id){
            return this.product_by_tmpl_id[tmpl_id];
        },

        add_product_by_tmpl_id: function(){
            var myProducts = this.product_by_id;
            for(var product_id in myProducts){
                var product = myProducts[product_id]
                this.product_by_tmpl_id[product.product_tmpl_id] = product;
            }
        },

        get_uom_by_product: function (id) {
            if (id in this.uom_by_product){
                return this.uom_by_product[id];
            }
            return []
        },

        add_uoms: function (uoms) {
            var self = this;
            _.each(uoms, function (unit) {
                var uom_product = self.get_product_by_tmpl_id(unit.product_id[0]);
                if (uom_product.id in self.uom_by_product){
                    console.log();
                }
                else{
                    var base_uom = {"id": uom_product.uom_id[0], "price": uom_product.lst_price,
                        "product_id": [uom_product.id, uom_product.display_name],
                        "uom_id": uom_product.uom_id}
                    self.uom_by_product[uom_product.id] = []
                    self.uom_by_product[uom_product.id].push(base_uom)
                }
                self.uom_by_product[uom_product.id].push(unit);

            });

            var myProducts = this.product_by_id;
            for(var product_id in myProducts) {
                var product = myProducts[product_id]
                if (product_id in self.uom_by_product){
                    console.log();
                }
                else{
                    var base_uom = {"id": product.uom_id[0], "price": product.lst_price,
                        "product_id": [product.id, product.display_name],
                        "uom_id": product.uom_id}
                    self.uom_by_product[product.id] = []
                    self.uom_by_product[product.id].push(base_uom);
                }
            }
        },

        get_uoms: function (serial) {
            return this.get_uom_by_product(serial.product_id[0])
        }
    });

    models.load_models({
        model: 'product.multi.uom.price',
        fields: ['uom_id', 'product_id', 'price'],
        loaded: function (self, uomPrice) {
            self.product_uom_price = {};
            if (uomPrice.length) {
                self.db.add_product_by_tmpl_id();
                self.db.add_uoms(uomPrice);
                _.each(uomPrice, function (unit) {
                    if (!self.product_uom_price[unit.product_id[0]]) {
                        self.product_uom_price[unit.product_id[0]] = {};
                        self.product_uom_price[unit.product_id[0]].uom_id = {};
                    }
                    self.product_uom_price[unit.product_id[0]].uom_id[unit.uom_id[0]] = {
                        id: unit.uom_id[0],
                        name: unit.uom_id[1],
                        price: unit.price,
                    };
                });
            }
        },
    });


    models.Orderline = models.Orderline.extend({
        apply_uom: function () {
            var self = this;
            var orderline = self.pos.get_order().get_selected_orderline();
            var uom_id = orderline.get_custom_uom_id();
            if (uom_id) {
                var selected_uom = this.pos.units_by_id[uom_id];
                orderline.uom_id = [uom_id, selected_uom.name];
                var latest_price = orderline.get_latest_price(selected_uom, orderline.product);
                let product = orderline.product.product_tmpl_id;
                let uomPrices = []
                if (orderline.pos.product_uom_price[product])
                    uomPrices = orderline.pos.product_uom_price[product].uom_id;
                let uom_price = {'price': 0, 'found': false}
                if (uomPrices) {
                    _.each(uomPrices, function (uomPrice) {
                        if (uomPrice.name == selected_uom.name) {
                            uom_price.price = uomPrice.price;
                            uom_price.found = true;
                        }
                    });
                }
                if (uom_price.found) {
                    orderline.set_unit_price(uom_price.price);
                } else {
                    orderline.set_unit_price(latest_price);
                }
                return true
            } else {
                return false
            }
        },
    });

});

