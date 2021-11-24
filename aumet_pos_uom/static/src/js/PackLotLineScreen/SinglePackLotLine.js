odoo.define('aumet_pod_uom.SinglePackLotLine', function (require) {
    'use strict';

    const SinglePackLotLine = require('flexipharmacy.SinglePackLotLine');
    const Registries = require('point_of_sale.Registries');

    class SinglePackLotLineInh extends SinglePackLotLine {
        onUomChange(e) {
            const uom_id = e.target.value;
            var real_qty = this.props.serial.real_qty;
            this.props.serial.uom = uom_id;
            var uom_obj = this.env.pos.units_by_id[uom_id];
            var newQty = this.env.pos.db.get_qty_for_selected_uom(uom_obj, real_qty);
            this.props.serial.location_product_qty = Math.floor(newQty);
            this.render();
        }
    }

    Registries.Component.extend(SinglePackLotLine, SinglePackLotLineInh);

    return SinglePackLotLine;

});
