odoo.define('aumet_pos.limitation', function (require) {
'use strict';
const Registries = require('point_of_sale.Registries');
var core = require('web.core');
var rpc = require('web.rpc');
var _t = core._t;
const PosComponent = require('point_of_sale.PosComponent');
const ProductScreen = require('point_of_sale.ProductScreen');

const DiscountButton = require('pos_discount.DiscountButton');

const DiscountLimit = DiscountButton =>
        class extends DiscountButton {
            async apply_discount(pc){
        var user = this.env.pos.get_cashier();
        var self = this;
        var order = this.env.pos.get_order();
        var lines = order.get_orderlines();
        rpc.query({
            model: 'pos.config',
            method: 'check_user_limit',
            args: [user, pc],
            })
            .then(async function (result) {
                var msg = _.str.sprintf(_t("You are not allowed to give discount more than %s!"), result['disc_limit']);
                if (result['disc_limit']){
                    await self.showPopup('ErrorPopup', {
                        title :  _t("Discount Limit Exceed"),
                        body  : msg,
                    });
                    return;
                }else{
                   var product  = self.env.pos.db.get_product_by_id(self.env.pos.config.discount_product_id[0]);
                  if (product === undefined) {
                        await self.showPopup('ErrorPopup', {
                            title : _t("No discount product found"),
                            body  : _t("The discount product seems misconfigured. Make sure it is flagged as 'Can be Sold' and 'Available in Point of Sale'."),
                        });
                        return;
                    }

                   // Remove existing discounts
            var i = 0;
            while ( i < lines.length ) {
                if (lines[i].get_product() === product) {
                    order.remove_orderline(lines[i]);
                } else {
                    i++;
                }
            }

            // Add discount
            // We add the price as manually set to avoid recomputation when changing customer.
            var base_to_discount = order.get_total_without_tax();
            if (product.taxes_id.length){
                var first_tax = self.env.pos.taxes_by_id[product.taxes_id[0]];
                if (first_tax.price_include) {
                    base_to_discount = order.get_total_with_tax();
                }
            }
            var discount = - pc / 100.0 * base_to_discount;
            rpc.query({
                model: 'pos.config',
                method: 'check_discount_per_amount',
                args: [user, discount],
            }).then(async function (result) {
                if(result["discount_amount"]){
                   await self.showPopup('ErrorPopup', {
                          title : _t("Discount Limit"),
                          body  : _t( _.str.sprintf(_t("The total discount must less than %s!"), result['discount_amount'])),
                        });
                        return;
                }
                else{
                 if( discount < 0 ){
                        order.add_product(product, {
                        price: discount,
                        lst_price: discount,
                        extras: {
                            price_manually_set: true,
                            },
                        });
                    }

                }
            })

                }
            });

            }
        };

Registries.Component.extend(DiscountButton, DiscountLimit);

return DiscountButton;
});