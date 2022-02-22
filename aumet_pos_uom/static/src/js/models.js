odoo.define('aumet_pos_uom.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var utils = require('web.utils');
    var field_utils = require('web.field_utils');
    var round_pr = utils.round_precision;
    var _ModelProto = models.Order.prototype;
    var rpc = require('web.rpc');

    models.Orderline = models.Orderline.extend({
        set_quantity: function (quantity, keep_price) {
            this.order.assert_editable();
            if (quantity === 'remove') {
                this.order.remove_orderline(this);
                return;
            } else {
                var quant = typeof (quantity) === 'number' ? quantity : (field_utils.parse.float('' + quantity) || 0);
                var unit = this.get_unit();
                if (unit) {
                    if (unit.rounding) {
                        var decimals = this.pos.dp['Product Unit of Measure'];
                        var rounding = Math.max(unit.rounding, Math.pow(10, -decimals));
                        this.quantity = round_pr(quant, rounding);
                        this.quantityStr = field_utils.format.float(this.quantity, {digits: [69, decimals]});
                    } else {
                        this.quantity = round_pr(quant, 1);
                        this.quantityStr = this.quantity.toFixed(0);
                    }
                } else {
                    this.quantity = quant;
                    this.quantityStr = '' + this.quantity;
                }
            }
            // just like in sale.order changing the quantity will recompute the unit price
            // if (!keep_price && !this.price_manually_set) {
            //     this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity(), this.get_price_extra()));
            //     this.order.fix_tax_included_price(this);
            // }
            this.trigger('change', this);
        },
    });

    models.Order = models.Order.extend({
        add_product: function (product, options) {
            _ModelProto.add_product.call(this, product, options);
//            this.setFirstOneSelected(product);
        },
        setFirstOneSelected: async function (product) {
            if (this.pos.config.enable_pos_serial && !this.refund_order) {
                var self = this;
                var picking_type = this.pos.config.picking_type_id[0]

                var params = {
                    model: 'stock.production.lot',
                    method: 'product_lot_and_serial',
                    args: [product, product.id, picking_type]
                }
                var pro_serials = [];
                await rpc.query(params).then(async function (serials) {
                    if (serials) {
                        for (var i = 0; i < serials.length; i++) {
                            if (serials[i].remaining_qty > 0) {
                                serials[i]['isSelected'] = false;
                                serials[i]['inputQty'] = 1;
                                serials[i]['uom'] = serials[i].product_uom_id[0];
                                if (serials[i].expiration_date) {
                                    let localTime = moment.utc(serials[i].expiration_date).toDate();
                                    serials[i]['expiration_date'] = moment(localTime).locale('en').format('YYYY-MM-DD hh:mm A');
                                }
                                if (self.pos.config.product_exp_days) {
                                    let product_exp_date = moment().add(self.pos.config.product_exp_days, 'd')
                                        .format('YYYY-MM-DD');
                                    let serial_life = moment(serials[i]['expiration_date']).locale('en').format('YYYY-MM-DD');
                                    if (product_exp_date >= serial_life) {
                                        serials[i]['NearToExpire'] = 'NearToExpire';
                                    }
                                }
                                pro_serials.push(serials[i])
                            }
                        }
                    }
                });


                var selectedLine = this.get_selected_orderline();
                var all_order_line = this.orderlines.models
                var same_order_line

                var serials = pro_serials;
                const isSingleItem = product.isAllowOnlyOneLot();
                if (serials.length == 1 && selectedLine) {
                    var serial = serials[0];
                    var prod_uom = 0;
                    var prod_qty = 1;
                    var foundUOM = false;
                    var uoms = this.pos.db.get_uoms(serial);
                    if (serial['location_product_qty'] <= 1) {
                        if (uoms.length > 1) {
                            for (var ind in uoms) {
                                var uom_id = uoms[ind].uom_id[0];
                                var uom_obj = this.pos.units_by_id[uom_id];
                                var qty = this.pos.db.get_qty_for_selected_uom(uom_obj, serial.real_qty);
                                if (qty >= 1) {
                                    if (!foundUOM) {
                                        foundUOM = true;
                                        prod_uom = uom_id;
                                        prod_qty = 1;
                                    }
                                }
                            }
                        }
                    }
                    selectedLine.set_quantity(prod_qty);

                    let modifiedPackLotLines = {};
                    if (isSingleItem && foundUOM) {
                        let newPackLotLines = serials.filter(item => item.id).map(item => ({lot_name: item.name}));
                        selectedLine.setPackLotLines({modifiedPackLotLines, newPackLotLines});
                        selectedLine.set_quantity(prod_qty);
                        selectedLine.set_custom_uom_id(parseInt(prod_uom));
                        selectedLine.apply_uom();
                        return true;
                    }
                    let selectedLines = [];
                    selectedLines = serials[0];
                    _.each(all_order_line, function (item) {
                        if (item.product.id == selectedLine.product.id) {
                            _.each(item.pack_lot_lines.models, function (lot_id) {
                                if (lot_id.attributes.lot_name === selectedLines.name) {
                                    same_order_line = item
                                }
                            });
                        }
                    });

                    if (same_order_line) {
                        selectedLine.set_quantity('remove')
                        var total_qty = Number(same_order_line.quantity) + Number(selectedLines.inputQty)
                        if (Number(total_qty) > Number(selectedLines.location_product_qty)) {
                            alert('Invalid Quantity!');
                            return;
                        }
                        same_order_line.set_quantity(total_qty)
                        return;
                    } else {
                        let newPackLotLines = serials.filter(item => item.id).map(item => ({lot_name: item.name}));
                        selectedLine.setPackLotLines({modifiedPackLotLines, newPackLotLines});
                        return;
                    }
                }
                return false;
            }
        },
    });

});
