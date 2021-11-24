odoo.define('aumet_pod_uom.SinglePackLotLine', function (require) {
    'use strict';

    const SinglePackLotLine = require('flexipharmacy.SinglePackLotLine');
    const Registries = require('point_of_sale.Registries');

    class SinglePackLotLineInh extends SinglePackLotLine {

    }

    Registries.Component.extend(SinglePackLotLine, SinglePackLotLineInh);

    return SinglePackLotLine;

});
