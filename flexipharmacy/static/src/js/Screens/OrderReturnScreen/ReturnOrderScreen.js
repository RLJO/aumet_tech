odoo.define('flexipharmacy.ReturnOrderScreen', function (require) {
    'use strict';

    const { useContext, useState } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const Registries = require('point_of_sale.Registries');
    const ReturnOrderFetcher = require('flexipharmacy.ReturnOrderFetcher');
    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    const contexts = require('point_of_sale.PosContext');
    const models = require('point_of_sale.models');

    class ReturnOrderScreen extends ControlButtonsMixin(IndependentToOrderScreen) {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
            useListener('set-numpad-mode', this._setNumpadMode);
            useListener('click-order', this._onClickOrder);
            useListener('next-page', this._onNextPage);
            useListener('prev-page', this._onPrevPage);
            useListener('search', this._onSearch);
            useListener('serialNumberPopup', this.OpenSerialNumberPopup);
            this.state = useState({orders:[], orderlines:[], ReturnAllProduct: false, SelectedLotSerialList: []})
            NumberBuffer.use({
                nonKeyboardInputEvent: 'numpad-click-input',
                useWithBarcode: true,
            });
            this.numpadMode = 'quantity';
            ReturnOrderFetcher.setComponent(this);
            ReturnOrderFetcher.setConfigId(this.env.pos.config_id);
            this.orderManagementContext = useContext(contexts.orderManagement);
        }
        mounted() {
            ReturnOrderFetcher.on('update', this, this.render);
//            this.env.pos.get('orders').on('add remove', this.render, this);

            // calculate how many can fit in the screen.
            // It is based on the height of the header element.
            // So the result is only accurate if each row is just single line.
            const flexContainer = this.el.querySelector('.flex-container');
            const cpEl = this.el.querySelector('.control-panel');
            const headerEl = this.el.querySelector('.order-row.header');
            const val = Math.trunc(
                (flexContainer.offsetHeight - cpEl.offsetHeight - headerEl.offsetHeight) /
                    headerEl.offsetHeight
            );
            ReturnOrderFetcher.setNPerPage(val);

            // Fetch the order after mounting so that order management screen
            // is shown while fetching.
//            console.log(ReturnOrderFetcher.fetch())
            setTimeout(() => ReturnOrderFetcher.fetch(), 0);
        }
        willUnmount() {
            ReturnOrderFetcher.off('update', this);
            this.env.pos.get('orders').off('add remove', null, this);
        }
        async OpenSerialNumberPopup(event) {
            var LineSerialNumber = []
            var SelectedLineSerialNumber = []
            _.each(event.detail.operation_lot_name, function(value,key) {
                var lot = {'id': key, 'name': value.lot_name}
                LineSerialNumber.push(lot)
            });
            const { confirmed, payload} = await this.showPopup(
                'SelectedSerialNumberPopup',
                {
                    title: this.env._t('Select Serial Number'),
                    numberlist: LineSerialNumber,
                    // selectedno: SelectedSerialList,
                }
            );

            if (confirmed) {
                _.each(payload, function(number) {
                    var lot = {lot_name: number.name}
                    SelectedLineSerialNumber.push(lot)
                });
                event.detail.line['select_operation_lot_name'] = SelectedLineSerialNumber
                event.detail.line['return_qty'] = SelectedLineSerialNumber.length
            }

        }
        get selectedClient() {
            const order = this.orderManagementContext.selectedOrder;
            return order ? order.get_client() : null;
        }
        get orders() {
            return ReturnOrderFetcher.get();
        }
        async _setNumpadMode(event) {
            const { mode } = event.detail;
            this.numpadMode = mode;
            NumberBuffer.reset();
        }
        _onNextPage() {
            ReturnOrderFetcher.nextPage();
        }
        _onPrevPage() {
            ReturnOrderFetcher.prevPage();
        }
        _onSearch({ detail: domain }) {
            ReturnOrderFetcher.setSearchDomain(domain);
            ReturnOrderFetcher.setPage(1);
            ReturnOrderFetcher.fetch();
        }
        _onClickOrder({ detail: clickedOrder }) {
//            if (!clickedOrder || clickedOrder.locked) {
                this.orderManagementContext.selectedOrder = clickedOrder;
//            } else {
//                this._setOrder(clickedOrder);
//            }
        }
        /**
         * @param {models.Order} order
         */
        _setOrder(order) {
            var posOrder = new models.Order({}, { pos: this.env.pos, json: order });
            this.env.pos.set_order(posOrder);
//            if (order === this.env.pos.get_order()) {
//                this.close();
//            }
        }
        ProcessReturnOrder() {
            var self = this
            this.state.orderlines = this.orderManagementContext.selectedOrder.orderlines.models
            this.state.orders = this.orderManagementContext.selectedOrder
            console.log("/////////*******--1111---*****//////////",this.state.orderlines)
            console.log("/////////*******--0000---*****//////////",this.state.orders)
            if (this.state.orderlines && this.state.orderlines.length > 0){
                var order = self.env.pos.get_order()
                var lines = order.get_orderlines();
                if(lines.length > 0){
                    self.orderIsEmpty(order);
                }
                var partner_id = this.state.orders.get_client()
                this.env.pos.get_order().set_client(partner_id);
                var line_datas = []
                _.each(this.state.orderlines, function (lines) {
                    if (lines.return_qty > 0){
                        var line_data = {}
                        var product_id = lines.product
                        var quantity = 0
                        if (lines.return_qty > lines.order_return_qty){
                            quantity = -lines.order_return_qty
                        }else{
                            quantity = -lines.return_qty
                        }
                        var price_unit = lines.price_unit
                        if (lines.pack_lot_ids.length > 0){
                            const isAllowOnlyOneLot = product_id.isAllowOnlyOneLot();
                            if (lines.pack_lot_ids.length > 0 && !isAllowOnlyOneLot){
                                self.state.SelectedLotSerialList = lines.select_operation_lot_name
                            }else{
                                self.state.SelectedLotSerialList = lines.operation_lot_name
                            }
                            let draftPackLotLines
                            const modifiedPackLotLines = {}
                            var newPackLotLines = self.state.SelectedLotSerialList 
                            draftPackLotLines = { modifiedPackLotLines, newPackLotLines };
                            draftPackLotLines
                            self.env.pos.get_order().add_product(product_id, {
                                draftPackLotLines,
                                quantity: quantity, 
                                price: price_unit,
                            });
                            let orderLine = self.env.pos.get_order().get_selected_orderline();
                            orderLine.set_quantity(quantity);
                        }else{
                            self.env.pos.get_order().add_product(product_id, {
                                quantity: quantity, 
                                price: price_unit,
                            });
                        }
                        line_data = {
                            'id': lines.id,
                            'return_qty': lines.return_qty,
                            'order_return_qty': lines.order_return_qty,
                            'select_operation_lot_name': lines.select_operation_lot_name,
                        }
                        line_datas.push(line_data)
                    }
                });
                // this.state.orders['lines'] = line_ids
                this.env.pos.get_order().set_refund_ref_order({'name': this.state.orders.name})
                // this.env.pos.get_order().set_refund_ref_order(this.state.orders)
                this.env.pos.get_order().set_refund_ref_orderline(line_datas)
                if (this.env.pos.get_order().get_orderlines() && this.env.pos.get_order().get_orderlines().length > 0){
                    this.env.pos.get_order().set_refund_order(true)
                }
                // this._onClearSearch()
                this.showScreen('ProductScreen', {'refund_order': true, 'refund_ref_order': this.state.orders});
            }
        }
    }
    ReturnOrderScreen.template = 'ReturnOrderScreen';
    ReturnOrderScreen.hideOrderSelector = true;

    Registries.Component.add(ReturnOrderScreen);

    return ReturnOrderScreen;
});
