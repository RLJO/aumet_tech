# -*- coding: utf-8 -*-
# from odoo import http


# class AumetStock(http.Controller):
#     @http.route('/aumet_stock/aumet_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aumet_stock/aumet_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aumet_stock.listing', {
#             'root': '/aumet_stock/aumet_stock',
#             'objects': http.request.env['aumet_stock.aumet_stock'].search([]),
#         })

#     @http.route('/aumet_stock/aumet_stock/objects/<model("aumet_stock.aumet_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aumet_stock.object', {
#             'object': obj
#         })
