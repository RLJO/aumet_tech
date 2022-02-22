# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import api, fields, models


class MultiBarcodes(models.Model):
    _name = "multi.barcodes"

    name = fields.Char('Name')
    product_id = fields.Many2one('product.template', string='Product')

    _sql_constraints = [
        ('name', 'unique (name)', 'The name of the Barcode must be unique!'),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
