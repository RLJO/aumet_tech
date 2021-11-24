# -*- coding: utf-8 -*-

from odoo import models, fields

class Users(models.Model):
    _inherit = 'res.users'

    odoobot_state = fields.Selection(default="disabled",string="Aumet Pharamcy State")
    notification_type = fields.Selection([
        ('email', 'Handle by Emails'),
        ('inbox', 'Handle in Aumet Pharmacy')],
        'Notification', required=True, default='email',
        help="Policy on how to handle Chatter notifications:\n"
             "- Handle by Emails: notifications are sent to your email address\n"
             "- Handle in Aumet Pharmacy: notifications appear in your Aumet Pharmacy Inbox")




