odoo.define('web_debrand.title', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var WebClient = require('web.AbstractWebClient');
    var utils = require('web.utils');
    var config = require('web.config');
    var _t = core._t;

    var ajax = require('web.ajax');
    var Dialog = require('web.Dialog');
    var ServiceProviderMixin = require('web.ServiceProviderMixin');
    var KeyboardNavigationMixin = require('web.KeyboardNavigationMixin');
    var CrashManager = require('web.CrashManager').CrashManager; // We can import crash_manager also
    var CrashManagerDialog = require('web.CrashManager').CrashManagerDialog; // We can import crash_manager also
    var ErrorDialog = require('web.CrashManager').ErrorDialog; // We can import crash_manager also
    var WarningDialog = require('web.CrashManager').WarningDialog; // We can import crash_manager also
//    var MailBotService = require('mail_bot.MailBotService').MailBotService; // We can import crash_manager also
    var concurrency = require('web.concurrency');
    var mixins = require('web.mixins');

    var QWeb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;

    let active = true;


    WebClient.include({
        init: function (parent) {
            this._super(parent);
            var self = this;
            this.set('title_part', {"zopenerp": "Aumet Pharmacy"});
        },
    });

        CrashManager.include({
        init: function (parent) {
            var self = this;
            active = true;
            this.isConnected = true;
            this._super.apply(this, arguments);

            window.onerror = function (message, file, line, col, error) {
                // Scripts injected in DOM (eg: google API's js files) won't return a clean error on window.onerror.
                // The browser will just give you a 'Script error.' as message and nothing else for security issue.
                // To enable onerror to work properly with CORS file, you should:
                //   1. add crossorigin="anonymous" to your <script> tag loading the file
                //   2. enabling 'Access-Control-Allow-Origin' on the server serving the file.
                // Since in some case it wont be possible to to this, this handle should have the possibility to be
                // handled by the script manipulating the injected file. For this, you will use window.onOriginError
                // If it is not handled, we should display something clearer than the common crash_manager error dialog
                // since it won't show anything except "Script error."
                // This link will probably explain it better: https://blog.sentry.io/2016/05/17/what-is-script-error.html
                if (!file && !line && !col) {
                    // Chrome and Opera set "Script error." on the `message` and hide the `error`
                    // Firefox handles the "Script error." directly. It sets the error thrown by the CORS file into `error`
                    if (window.onOriginError) {
                        window.onOriginError();
                        delete window.onOriginError;
                    } else {
                        self.show_error({
                            type: _t("Client Error"),
                            message: _t("Unknown CORS error"),
                            data: {debug: _t("An unknown CORS error occured. The error probably originates from a JavaScript file served from a different origin. (Opening your browser console might give you a hint on the error.)")},
                        });
                    }
                } else {
                    // ignore Chrome video internal error: https://crbug.com/809574
                    if (!error && message === 'ResizeObserver loop limit exceeded') {
                        return;
                    }
                    var traceback = error ? error.stack : '';
                    self.show_error({
                        type: _t("Client Error"),
                        message: message,
                        data: {debug: file + ':' + line + "\n" + _t('Traceback:') + "\n" + traceback},
                    });
                }
            };
//
            // listen to unhandled rejected promises, and throw an error when the
            // promise has been rejected due to a crash
            core.bus.on('crash_manager_unhandledrejection', this, function (ev) {
                if (ev.reason && ev.reason instanceof Error) {
                    var traceback = ev.reason.stack;
                    self.show_error({
                        type: _t("Client Error"),
                        message: '',
                        data: {debug: _t('Traceback:') + "\n" + traceback},
                    });
                } else {
                    // the rejection is not due to an Error, so prevent the browser
                    // from displaying an 'unhandledrejection' error in the console
                    ev.stopPropagation();
                    ev.stopImmediatePropagation();
                    ev.preventDefault();
                }
            });
        },

    show_warning: function (error, options) {
        if (!active) {
            return;
        }
        var message = error.data ? error.data.message : error.message;
        var title = _t("Something went wrong !");
        if (error.type) {
            title = _.str.capitalize(error.type);
        } else if (error.data && error.data.title) {
            title = _.str.capitalize(error.data.title);
        }
        return this._displayWarning(message, title, options);
    },
    show_error: function (error) {
        let ttype = "type" in error;
        let mmessage = "message" in error;
        if (ttype) {
            if ( error.type.includes('Odoo')){
            error.type = error.type.replace('Odoo', '')
            }
        }
        else {
            error.type = _t("Error")
        }
        if (mmessage){
            if ( error.message.includes('Odoo')){
            error.message = error.message.replace('Odoo', '')
            }
        }
        this._super(error)
    },
    show_message: function(exception) {
        return this.show_error({
            type: _t("Client Error"),
            message: exception,
            data: {debug: ""}
        });
    },
});
    Dialog.include({
    init: function (parent, options) {
            var self = this;
            this._super(parent);
            this._opened = new Promise(function (resolve) {
                self._openedResolver = resolve;
            });
            options = _.defaults(options || {}, {
                title: _t(' '), subtitle: '',
                size: 'large',
                fullscreen: false,
                dialogClass: '',
                $content: false,
                buttons: [{text: _t("Ok"), close: true}],
                technical: true,
                $parentNode: false,
                backdrop: 'static',
                renderHeader: true,
                renderFooter: true,
                onForceClose: false,
            });

            this.$content = options.$content;
            this.title = options.title;
            this.subtitle = options.subtitle;
            this.fullscreen = options.fullscreen;
            this.dialogClass = options.dialogClass;
            this.size = options.size;
            this.buttons = options.buttons;
            this.technical = options.technical;
            this.$parentNode = options.$parentNode;
            this.backdrop = options.backdrop;
            this.renderHeader = options.renderHeader;
            this.renderFooter = options.renderFooter;
            this.onForceClose = options.onForceClose;

            core.bus.on('close_dialogs', this, this.destroy.bind(this));
        },
    });

});