odoo.define('stock_barcode.HeaderWidget', function (require) {
    'use strict';

    var Widget = require('web.Widget');

    var HeaderWidget = Widget.extend({
        'template': 'stock_barcode_header_widget',
        events: {
            'click .o_exit': '_onClickExit',
            'click .o_show_information': '_onClickShowInformation',
            'click .o_close': '_onClickClose',
            'click .o_validate': '_onClickValidate',
            'click .o_cancel': '_onClickCancel',
            'click .o_print_inventory': '_onClickPrintInventory',
            'click .o_add_line': '_onClickAddLine',
            'click #js_id_sh_stock_move_barcode_mobile_start_btn': '_open_camera',
            'click #js_id_sh_stock_move_barcode_mobile_reset_btn': '_stop_camera',
        },

        init: function (parent, model, mode) {
            this._super.apply(this, arguments);
            this.title = parent.title;
            this.model = parent.actionParams.model;
            this.mode = parent.mode;
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------
        _open_camera: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            this.trigger_up('open_camera');
        },

        _stop_camera: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            this.trigger_up('stop_camera');
        },
        /**
         * Toggle the header between two display modes: `init` and `specialized`.
         * - in init mode: exit, informations and settings button are displayed;
         * - in settings mode: close button is displayed.
         *
         * @param {string} mode: "init" or "settings".
         */
        toggleDisplayContext: function (mode) {
            var $showInformation = this.$('.o_show_information');
            var $close = this.$('.o_close');
            var $exit = this.$('.o_exit');

            if (mode === 'init') {
                $showInformation.toggleClass('o_hidden', false);
                $close.toggleClass('o_hidden', true);
                $exit.toggleClass('o_invisible', false);
            } else if (mode === 'specialized') {
                $showInformation.toggleClass('o_hidden', true);
                $close.toggleClass('o_hidden', false);
                $exit.toggleClass('o_invisible', true);
            }
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
        /**
         * Handles the click on the `validate button`.
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onClickValidate: function (ev) {
            ev.stopPropagation();
            this.trigger_up('validate');
        },

        /**
         * Handles the click on the `cancel button`.
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onClickCancel: function (ev) {
            var r = confirm("Are You Sure you want to cancel the inventory?");
            if (r == true) {
                ev.stopPropagation();
                this.trigger_up('cancel');
            } else {
                return
            }

        },

        /**
         * Handles the click on the `print inventory` button. This is specific to the
         * `stock.inventory` model.
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onClickPrintInventory: function (ev) {
            ev.stopPropagation();
            this.trigger_up('picking_print_inventory');
        },
        /**
         * Handles the click on the `exit button`.
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onClickExit: function (ev) {
            ev.stopPropagation();
            this.trigger_up('exit');
        },

        /**
         * Handles the click on the `settings button`.
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onClickShowInformation: function (ev) {
            ev.stopPropagation();
            this.trigger_up('show_information');
        },
        /**
         * Handles the click on the `add a product button`.
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onClickAddLine: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            this.trigger_up('add_line');
        },

        /**
         * Handles the click on the `close button`.
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onClickClose: function (ev) {
            ev.stopPropagation();
            this.trigger_up('reload');
        },
    });

    return HeaderWidget;

});
