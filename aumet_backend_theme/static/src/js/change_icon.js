odoo.define('custom_base.settings', function (require) {
"use strict";

var BaseSettingRenderer = require('base.settings').Renderer;

BaseSettingRenderer.include({

    _getAppIconUrl: function (module) {
        if (module == 'general_settings') {return "/aumet_backend_theme/static/src/img/icons/settings.png";}
        if (module == 'sale_management') {return "/aumet_backend_theme/static/src/img/icons/Sales.png";}
        if (module == 'purchase') {return "/aumet_backend_theme/static/src/img/icons/Purchase.png";}
        if (module == 'stock') {return "/aumet_backend_theme/static/src/img/icons/Inventory.png";}
        if (module == 'account') {return "/aumet_backend_theme/static/src/img/icons/Invoicing.png";}
        if (module == 'hr') {return "/aumet_backend_theme/static/src/img/icons/Employees.png";}
        if (module == 'hr_attendance') {return "/aumet_backend_theme/static/src/img/icons/Attendances.png";}
        if (module == 'point_of_sale') {return "/aumet_backend_theme/static/src/img/icons/Point of Sale.png";}
        else {return this._super.apply(this, arguments);}
    }
});
});