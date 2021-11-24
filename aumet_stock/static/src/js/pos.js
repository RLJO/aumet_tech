odoo.define("pos_models_aumet.pos", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    models.load_fields('product.product', ['name', 'type', 'qty_available', 'allow_negative_stock']);

    var PosModelSuper = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        push_orders: function (order, opts) {
            var pushed = PosModelSuper.push_orders.apply(this, arguments);
            if (order && order.get_orderlines()) {
                this.update_product_qty_from_order_lines(order);
            }
            return pushed;
        },
        push_single_order: function (order, opts) {
            var pushed = PosModelSuper.push_single_order.apply(this, arguments);
            if (order && order.get_orderlines()) {
                this.update_product_qty_from_order_lines(order);
            }
            return pushed;
        },
        push_and_invoice_order: function (order) {
            var invoiced = PosModelSuper.push_and_invoice_order.apply(this, arguments);
            if (order && order.get_orderlines()) {
                this.update_product_qty_from_order_lines(order);
            }

            return invoiced;
        },
        update_product_qty_from_order_lines: function (order) {
            order.get_orderlines().forEach(function (line) {
                var product = line.get_product();
                product.qty_available = product.qty_available - line.get_quantity();
            });
            order.trigger('change', order)
        }
    });
});