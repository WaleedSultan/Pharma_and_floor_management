# -*- coding: utf-8 -*-
# from odoo import http


# class FlourInvoice(http.Controller):
#     @http.route('/flour_invoice/flour_invoice', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/flour_invoice/flour_invoice/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('flour_invoice.listing', {
#             'root': '/flour_invoice/flour_invoice',
#             'objects': http.request.env['flour_invoice.flour_invoice'].search([]),
#         })

#     @http.route('/flour_invoice/flour_invoice/objects/<model("flour_invoice.flour_invoice"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('flour_invoice.object', {
#             'object': obj
#         })
