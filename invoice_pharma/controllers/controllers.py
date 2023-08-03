# -*- coding: utf-8 -*-
# from odoo import http


# class InvoicePharma(http.Controller):
#     @http.route('/invoice_pharma/invoice_pharma', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_pharma/invoice_pharma/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_pharma.listing', {
#             'root': '/invoice_pharma/invoice_pharma',
#             'objects': http.request.env['invoice_pharma.invoice_pharma'].search([]),
#         })

#     @http.route('/invoice_pharma/invoice_pharma/objects/<model("invoice_pharma.invoice_pharma"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_pharma.object', {
#             'object': obj
#         })
