import math
from collections import defaultdict

from odoo import fields, models, api, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang
import math

class AccountMove(models.Model):
    _inherit = "stock.move"

    in_invoice = fields.Boolean('In Invoice')

# class accountReportAb(models.AbstractModel):
#     _name = 'report.flour_invoice.report_delivery_invoice'
#
#     def _get_report_values(self, docids, data=None):
#         docs = self.env['stock.picking'].search([('id', '=', data['form']['id'])])
#         total_gross_weight = 0
#         total_amount = 0
#         total_qty = 0
#         for totaL_weight_amount in docs.move_line_ids_without_package:
#             total_gross_weight +=totaL_weight_amount.tare_deduction+totaL_weight_amount.addition_deduction
#
#         data = {
#             'weight':total_gross_weight,
#             'amount':total_amount,
#             'qty':total_qty
#         }
#         return {
#             'data': data,
#             'docs': docs,
#         }
