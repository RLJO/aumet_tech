# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import SUPERUSER_ID, api

from .models.module import PARAM_INSTALLED_CHECKSUMS,ABOUT_TO_UPGRADE_MODULE
# from .models.module import ABOUT_TO_UPGRADE_MODULE


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.config_parameter"].set_param(PARAM_INSTALLED_CHECKSUMS, False)
    env["ir.config_parameter"].set_param(ABOUT_TO_UPGRADE_MODULE, False)

def test_post_init_hook(cr,registry):

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.module.module"]._save_installed_checksums()