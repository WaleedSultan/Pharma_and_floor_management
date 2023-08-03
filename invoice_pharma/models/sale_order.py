from collections import defaultdict

from odoo import fields, models
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang



class Coupon(models.Model):
    _inherit = "coupon.program"

    sale_order_id = fields.Many2one(
        "sale.order"
    )
class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    coupon_ids = fields.One2many(
        "coupon.program", "sale_order_id", string="Coupons")


    def action_confirm(self):
        super().action_confirm()
        self.coupon_ids = self.no_code_promo_program_ids
        print("test")
        print("test")
        print("test")



class resPartnerInherit(models.Model):
    _inherit = "res.partner"

    license_no = fields.Char("License No")
    license_expiry = fields.Date("Expiry")
    license_category = fields.Selection(selection=[
        ('form_9', 'FORM 9'),
        ('form_10', 'FORM 10'),
        ('form_11', 'FORM 11'),
    ], string='License Category')

class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    reference_code = fields.Char('Reference Code')

    _sql_constraints = [
        ("name_ref", "unique (reference_code)", "Reference Code already exists!"),
    ]

