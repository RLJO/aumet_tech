odoo.define('point_of_sale.SinglePackLotLine', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class SinglePackLotLine extends PosComponent {
        constructor() {
            super(...arguments);
        }

        onKeyDown(e) {
            if (e.which == 96 || e.which == 110 || e.which == 190) {
                e.preventDefault();
            }
        }

        onUomChange(e) {
            const uom_id = e.target.value;
            var real_qty = this.props.serial.real_qty;
            this.props.serial.uom = uom_id;
            var uom_obj = this.env.pos.units_by_id[uom_id];
            var newQty = this.env.pos.db.get_qty_for_selected_uom(uom_obj, real_qty);
            this.props.serial.location_product_qty = Math.floor(newQty);
            this.render();
        }

        onClickPlus(serial) {
            if (this.props.isSingleItem) {
                if (this.props.serial.isSelected) {
                    this.trigger('toggle-Lot');
                    this.props.serial.isSelected = !this.props.serial.isSelected;
                    this.trigger('toggle-button-highlight');
                    return;
                }
                if (!this.props.isLotSelected) {
                    this.trigger('toggle-Lot');
                    this.props.serial.isSelected = !this.props.serial.isSelected;
                    this.trigger('toggle-button-highlight');
                }
                return;
            }
            this.props.serial.isSelected = !this.props.serial.isSelected;
            this.trigger('toggle-button-highlight');
            this.render();
        }
    }

    SinglePackLotLine.template = 'SinglePackLotLine';

    Registries.Component.add(SinglePackLotLine);

    return SinglePackLotLine;
});
