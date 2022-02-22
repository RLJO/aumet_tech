# -*- coding: utf-8 -*-
# from odoo import http


# class AumetBarcode(http.Controller):
#     @http.route('/aumet_barcode/aumet_barcode/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aumet_barcode/aumet_barcode/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aumet_barcode.listing', {
#             'root': '/aumet_barcode/aumet_barcode',
#             'objects': http.request.env['aumet_barcode.aumet_barcode'].search([]),
#         })

#     @http.route('/aumet_barcode/aumet_barcode/objects/<model("aumet_barcode.aumet_barcode"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aumet_barcode.object', {
#             'object': obj
#         })
