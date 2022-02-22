odoo.define('aumet_pos.OrderManagementControlPanelAumet', function (require) {
    'use strict';

    const OrderManagementControlPanel = require('point_of_sale.OrderManagementControlPanel');
    const Registries = require('point_of_sale.Registries');
    var _super_orderManagementScreen = OrderManagementControlPanel.prototype;

    const OrderManagementControlPanelAumet = (OrderManagementControlPanel) =>
        class extends OrderManagementControlPanel {
            get searchFields() {
                const fields = _super_orderManagementScreen.searchFields;
                fields.push('lines.full_product_name')
                return fields;
            }
        }

    Registries.Component.extend(OrderManagementControlPanel, OrderManagementControlPanelAumet);

    return OrderManagementControlPanel;
});
