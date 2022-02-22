# -*- coding: utf-8 -*-
# Copyright 2016, 2019 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    sidebar_visible = fields.Boolean("Show App Sidebar", default=True)

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights on notification_email_send
            and alias fields. Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super(ResUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(['sidebar_visible'])
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(['sidebar_visible'])
        return init_res

    @api.model
    def systray_get_activities(self):
        user_activities = super(ResUsers, self).systray_get_activities()
        for activity in user_activities:
            if "stock" in activity["model"]:
                activity["icon"] = "/aumet_backend_theme/static/src/img/icons/Inventory.png"
            elif "pos" in activity["model"]:
                activity["icon"] = "/aumet_backend_theme/static/src/img/icons/Point of Sale.png"
            elif "account" in activity["model"]:
                activity["icon"] = "/aumet_backend_theme/static/src/img/icons/Invoicing.png"
            elif "hr" in activity["model"]:
                if activity["model"] == "hr_attendence":
                    activity["icon"] = "/aumet_backend_theme/static/src/img/icons/Attendances.png"
                else:
                    activity["icon"] = "/aumet_backend_theme/static/src/img/icons/Employees.png"
            elif "mail" in activity["model"]:
                activity["icon"] = "/aumet_backend_theme/static/src/img/icons/discuss.png"
            elif "utm" in activity["model"]:
                activity["icon"] = "/aumet_backend_theme/static/src/img/icons/Link Tracker.png"
            elif "purchase" in activity["model"]:
                activity["icon"] = "/aumet_backend_theme/static/src/img/icons/Purchase.png"
            elif "sale" in activity["model"]:
                activity["icon"] = "/aumet_backend_theme/static/src/img/icons/Sales.png"

        return user_activities
