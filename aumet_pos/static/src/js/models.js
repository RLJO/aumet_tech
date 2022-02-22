odoo.define('aumet_pos.pos', function (require) { "use strict";
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var _super_posmodel = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({
    initialize: function (session, attributes) {
        // New code
        var partner_model = _.find(this.models, function(model){
            return model.model === 'product.product';
        });
        partner_model.fields.push('is_available');
         partner_model.domain= function(self){
            var domain = ['&','&',['sale_ok','=',true],["available_in_pos","=",true],'|',['company_id','=',self.config.company_id[0]],['company_id','=',false]];
            if (self.config.limit_categories &&  self.config.iface_available_categ_ids.length) {
                domain.unshift('&');
                domain.push(['pos_categ_id', 'in', self.config.iface_available_categ_ids]);
            }
            if (self.config.iface_tipproduct){
              domain.unshift(['id', '=', self.config.tip_product_id[0]]);
              domain.unshift('|');
            }
            return domain;
        };
        // Inheritance
        return _super_posmodel.initialize.call(this, session, attributes);
    },
});


});
