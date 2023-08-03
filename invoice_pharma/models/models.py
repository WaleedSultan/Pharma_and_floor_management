
from odoo import models, fields, api


class customerInherit(models.Model):
    _inherit = 'res.partner'
    pharma_type = fields.Selection(selection=[
        ('form9', 'Form-9'),
        ('form10', 'Form-10'),
        ('form11', 'Form-11')
    ], string='Pharma Type')
