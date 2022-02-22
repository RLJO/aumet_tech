odoo.define('flexipharmacy.mutlibarcode.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;
    var _ModelProto = models.Order.prototype;
    var utils = require('web.utils');
    var session = require('web.session');
    var exports = {};
    var round_pr = utils.round_precision;
    var round_di = utils.round_decimals;
    var field_utils = require('web.field_utils');
    var QWeb = core.qweb;

    models.load_fields("product.product", ['multi_barcode_ids']);
    var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        load_server_data: function(){
            var self = this;
            var loaded = _super_posmodel.prototype.load_server_data.call(this);
            loaded.then(function(){
                var barcode = {
                    model: 'multi.barcodes',
                    method: 'search_read',
                    domain: [],
                }
                rpc.query(barcode).then(function(result){
                }).catch(function(){
                    console.log("Connection lost");
                });
            })
            return loaded
        },
     });
    models.PosModel.prototype.models.push({
        model:  'multi.barcodes',
        fields: [],
        loaded: function(self,product_template_barcode){
            self.product_barcode_by_id = {};
            self.product_template_barcode = product_template_barcode;
            _.each(product_template_barcode, function(each_data){
                self.product_barcode_by_id[each_data.id] = each_data
            })
        },
    });

    return exports;

});
