odoo.define('aumet_pod_uom.PackLotLineScreen', function (require) {
    'use strict';

    const PackLotLineScreen = require('point_of_sale.PackLotLineScreen');
    const Registries = require('point_of_sale.Registries');
    // const { onMounted } = owl.hooks;

    const PackLotLineScreenInh = (PackLotLineScreen) =>
        class extends PackLotLineScreen {
            constructor() {
                super(...arguments);
                // onMounted(this.setFirstOneSelected.bind(this));
            }

            // setFirstOneSelected() {
            //     var self=this;
            //     if (this.props.serials.length == 1) {
            //         _.each(this.props.serials, function (serial) {
            //             var uoms = self.env.pos.db.get_uoms(serial);
            //             if (serial['location_product_qty'] < 1){
            //                 if (uoms.length > 1){
            //                     var foundUOM = false;
            //                     for(var ind in uoms){
            //                         var uom_id = uoms[ind].uom_id[0];
            //                         var uom_obj = self.env.pos.units_by_id[uom_id];
            //                         var qty = self.env.pos.db.get_qty_for_selected_uom(uom_obj, serial.real_qty);
            //                         if (qty >= 1){
            //                             if (!foundUOM){
            //                                 foundUOM = true;
            //                                 serial['uom'] = uom_id;
            //                                 serial['location_product_qty'] = Math.floor(qty);
            //                             }
            //                         }
            //                     }
            //                 }
            //             }
            //             serial.isSelected = true;
            //         });
            //         this.render();
            //         self.applyPackLotLines();
            //     }
            //     // this.render();
            // };
            _closePackLotScreen() {
                let serialApplied = [];
                let orderLine = this.env.pos.get_order().get_selected_orderline();
                if (this.props.orderline) {
                    orderLine = this.props.orderline;
                }
                var has_lot = false;
                _.each(orderLine.getPackLotLinesToEdit(), function (packLot) {
                    if (packLot.text != '') {
                        serialApplied.push(packLot.text)
                        has_lot = true;
                    }
                });
                _.each(this.props.serials, function (serial) {
                    if (!serialApplied.includes(serial.name)) {
                        serial.isSelected = false;
                    }
                });
                if (!has_lot) {
                    this.env.pos.get_order().remove_orderline(orderLine);
                }
                this.close();
            }

            applyPackLotLines() {
                let orderLine = this.env.pos.get_order().get_selected_orderline();
                var all_order_line = this.env.pos.get_order().orderlines.models
                var same_order_line
                // this.env.pos.get_order().orderlines.models[0].pack_lot_lines.models[0].attributes.lot_name
                if (this.props.orderline) {
                    orderLine = this.props.orderline;
                }
                let selectedLines = [];
                selectedLines = this.props.serials.filter(serial => serial.isSelected == true);
                if (selectedLines.length >= 1) {
                    let modifiedPackLotLines = {};
                    if (this.props.isSingleItem) {
                        if (selectedLines[0].inputQty > selectedLines[0].location_product_qty || selectedLines[0].inputQty <= 0) {
                            alert('Invalid Quantity!');
                            return;
                        } else {
                            _.each(all_order_line, function (item) {
                                if (item.product.id == orderLine.product.id) {
                                    _.each(item.pack_lot_lines.models, function (lot_id) {
                                        if (lot_id.attributes.lot_name === selectedLines[0].name) {
                                            same_order_line = item
                                        }
                                    });
                                }
                            });
                            if (same_order_line) {
                                orderLine.set_quantity('remove')
                                var total_qty = Number(same_order_line.quantity) + Number(selectedLines[0].inputQty)
                                if (Number(total_qty) > Number(selectedLines[0].location_product_qty)) {
                                    alert('Invalid Quantity!');
                                    return;
                                }
                                same_order_line.set_quantity(total_qty)
                                this._closePackLotScreen();
                                return;
                            } else {
                                let newPackLotLines = selectedLines.filter(item => item.id).map(item => ({lot_name: item.name}));
                                orderLine.setPackLotLines({modifiedPackLotLines, newPackLotLines});
                                orderLine.set_quantity(selectedLines[0].inputQty);
                                orderLine.set_custom_uom_id(parseInt(selectedLines[0].uom));
                                orderLine.apply_uom();
                                this._closePackLotScreen();
                                return;
                            }
                        }
                    }
                    let newPackLotLines = selectedLines.filter(item => item.id).map(item => ({lot_name: item.name}));
                    orderLine.setPackLotLines({modifiedPackLotLines, newPackLotLines});
                    this._closePackLotScreen();
                } else {
                    alert('Please assign Lot/Serial of product!')
                }
            }
        }

    Registries.Component.extend(PackLotLineScreen, PackLotLineScreenInh);

    return PackLotLineScreen;
});
