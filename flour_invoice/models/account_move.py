import math
from collections import defaultdict

from odoo import fields, models, api, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang
import math


class AccountMove(models.Model):
    _inherit = "account.move"


    def action_print_report(self):
        if self.invoice_filter_type_domain == 'sale':
            data = {
                'model': 'account.move',
                'form': self.read()[0]
            }
            return self.env.ref('flour_invoice.account_flour_invoice').report_action(self, data=data)
        elif self.invoice_filter_type_domain == 'purchase':
            data = {
                'model': 'account.move',
                'form': self.read()[0]
            }
            return self.env.ref('flour_invoice.account_delivery_invoice').report_action(self, data=data)


class accountReportAb(models.AbstractModel):
    _name = 'report.flour_invoice.report_invoice'

    def _get_report_values(self, docids, data=None):
        if docids:
            docs = self.env['account.move'].search([('id', '=', docids[0])])
        else:
            docs = self.env['account.move'].search([('id', '=', data['form']['id'])])
        purchase_order = self.env['sale.order'].search([('name', '=', docs.invoice_origin)])
        picking_ids = purchase_order.picking_ids[0]
        total_weight = 0
        total_amount = 0
        total_qty = 0
        invoice_line = []
        for invoice in docs.invoice_line_ids:
            print(invoice.product_id.name)
            for product in picking_ids.move_line_nosuggest_ids:
                if product.product_id == invoice.product_id:
                    invoice_line.append({
                        'product': product.product_id.name,
                        'grn': picking_ids.carrier_tracking_ref,
                        'vehicle': picking_ids.name,
                        'net_weight': f'{invoice.quantity:,}',
                        'subtotal': f'{invoice.price_subtotal:,}',
                        'bags': [x for x in purchase_order.order_line if x.product_id == invoice.product_id][
                            0].product_packaging_qty,
                        'rate': invoice.price_unit

                    })
                    total_weight += invoice.quantity
                    total_amount += invoice.price_subtotal
                    total_qty += [x for x in purchase_order.order_line if x.product_id == invoice.product_id][
                        0].product_packaging_qty

        data = {
            'invoice_line': invoice_line,
            'weight': f'{total_weight:,}',
            'amount': f'{total_amount:,}',
            'qty': f'{total_qty:,}',
        }
        return {
            'data': data,
            'docs': docs,
        }


class PurchaseOrderReport(models.AbstractModel):
    _name = 'report.flour_invoice.report_delivery_invoice'

    # def _get_report_values(self, docids, data=None):
    #     picking_ids = []
    #     if docids:_get_report_values
    #         docs = self.env['account.move'].search([('id', '=', docids[0])])
    #     else:
    #         docs = self.env['account.move'].search([('id', '=', data['form']['id'])])
    #     purchase_order = self.env['purchase.order'].search([('name', '=', docs.invoice_origin)])
    #     if purchase_order.picking_ids:
    #         for ids in purchase_order.picking_ids:
    #             picking_ids.append(ids)
    #     else:
    #         picking_ids = []
    #     total_gross_weight = 0
    #     total_tare = 0
    #     total_addition = 0
    #     total_net = 0
    #     total = 0
    #     invoice_line = {}
    #     for invoice in docs.invoice_line_ids:
    #         print(invoice.product_id.name)
    #         for multi_picking_ids in picking_ids:
    #             for product in multi_picking_ids.move_line_nosuggest_ids:
    #                 if product.product_id == invoice.product_id:
    #                     if not product.product_id.name in invoice_line.keys():
    #                         invoice_line[product.product_id.name] = {
    #                             'product': product.product_id.name,
    #                             'vehicle': (multi_picking_ids.carrier_tracking_ref or ""),
    #                             'grn': multi_picking_ids.name,
    #                             'unloading': product.location_dest_id.name,
    #                             'gross_weight': f'{product.tare_deduction + product.addition_deduction + invoice.quantity:,}',
    #                             'net_weight': f'{invoice.quantity:,}',
    #                             'tare': f'{product.tare_deduction:,}',
    #                             'addition': f'{product.addition_deduction:,}',
    #                             'rate40': invoice.price_unit * 40 if invoice.product_id and invoice.product_id.type == 'product' else 0,
    #                             'subtotal': f'{invoice.price_subtotal:,}',
    #                             'bags':
    #                                 [x for x in purchase_order.order_line if
    #                                  x.product_id == invoice.product_id][
    #                                     0].product_packaging_qty
    #                         }
    #                     else:
    #                         if multi_picking_ids.carrier_tracking_ref:
    #                             if multi_picking_ids.carrier_tracking_ref != invoice_line[product.product_id.name]['vehicle']:
    #                                 invoice_line[product.product_id.name] = {
    #                                     'product': product.product_id.name,
    #                                     'vehicle': (multi_picking_ids.carrier_tracking_ref or ""),
    #                                     'grn': multi_picking_ids.name,
    #                                     'unloading': product.location_dest_id.name,
    #                                     'gross_weight': f'{product.tare_deduction + product.addition_deduction + invoice.quantity:,}',
    #                                     'net_weight': f'{invoice.quantity:,}',
    #                                     'tare': f'{product.tare_deduction:,}',
    #                                     'addition': f'{product.addition_deduction:,}',
    #                                     'rate40': invoice.price_unit * 40 if invoice.product_id and invoice.product_id.type == 'product' else 0,
    #                                     'subtotal': f'{invoice.price_subtotal:,}',
    #                                     'bags':
    #                                         [x for x in purchase_order.order_line if
    #                                          x.product_id == invoice.product_id][
    #                                             0].product_packaging_qty
    #                                 }
    #                             else:
    #                                 veh = invoice_line[product.product_id.name]['vehicle']
    #                                 invoice_line[product.product_id.name]['vehicle'] = veh
    #
    #                                 invoice_line[product.product_id.name]['tare'] = float(
    #                                     invoice_line[product.product_id.name]['tare']) + (
    #                                                                                         product.tare_deduction or 0)
    #                                 invoice_line[product.product_id.name]['addition'] = float(
    #                                     invoice_line[product.product_id.name]['addition']) + (
    #                                                                                             product.addition_deduction or 0)
    #
    #                         if invoice.product_id.type == 'product':
    #                             total_tare += product.tare_deduction
    #                             total_addition += product.addition_deduction
    #                             total_net += invoice.quantity
    #                             total_gross_weight += product.tare_deduction + product.addition_deduction + invoice.quantity
    #                             total += invoice.price_subtotal
    #     return {
    #         'data': {'invoice_line': invoice_line,
    #                  'total': f'{total:,}',
    #                  'tare_total': f'{total_tare:,}',
    #                  'addi_total': f'{total_addition:,}',
    #                  'total_net': f'{total_net:,}',
    #                  'total_gross': f'{total_gross_weight:,}'
    #                  },
    #         'docs': docs,
    #     }
    # def _get_report_values(self, docids, data=None):
    #     picking_ids = []
    #     if docids:
    #         docs = self.env['account.move'].search([('id', '=', docids[0])])
    #     else:
    #         docs = self.env['account.move'].search([('id', '=', data['form']['id'])])
    #     purchase_order = self.env['purchase.order'].search([('name', '=', docs.invoice_origin)])
    #     if purchase_order.picking_ids:
    #         for ids in purchase_order.picking_ids:
    #             picking_ids.append(ids)
    #     else:
    #         picking_ids = []
    #     total_gross_weight = 0
    #     total_tare = 0
    #     total_addition = 0
    #     total_net = 0
    #     total = 0
    #     invoice_line = {}
    #     count = 0
    #     all_delvry_done = False
    #     for invoice in docs.invoice_line_ids:
    #         if not all_delvry_done:
    #             for multi_picking_ids in picking_ids:
    #                 for product in multi_picking_ids.move_line_nosuggest_ids:
    #                     if product.product_id == invoice.product_id:
    #                         if multi_picking_ids.name not in invoice_line.keys():
    #                             invoice_line[multi_picking_ids.name] = [[product.product_id.name, multi_picking_ids.carrier_tracking_ref,multi_picking_ids.name,product.location_dest_id.name,f'{product.tare_deduction + product.addition_deduction + invoice.quantity:,}',f'{invoice.quantity:,}',f'{product.tare_deduction:,}',f'{product.addition_deduction:,}',invoice.price_unit * 40 if invoice.product_id and invoice.product_id.type == 'product' else 0,f'{invoice.price_subtotal:,}',[x for x in purchase_order.order_line if
    #                                      x.product_id == invoice.product_id][
    #                                         0].product_packaging_qty]]
    #                         else:
    #                             invoice_line[multi_picking_ids.name].append(
    #                                 [product.product_id.name, multi_picking_ids.carrier_tracking_ref,
    #                                  multi_picking_ids.name, product.location_dest_id.name,
    #                                  f'{product.tare_deduction + product.addition_deduction + invoice.quantity:,}',
    #                                  f'{invoice.quantity:,}', f'{product.tare_deduction:,}',
    #                                  f'{product.addition_deduction:,}',
    #                                  invoice.price_unit * 40 if invoice.product_id and invoice.product_id.type == 'product' else 0,
    #                                  f'{invoice.price_subtotal:,}', [x for x in purchase_order.order_line if
    #                                                                  x.product_id == invoice.product_id][
    #                                      0].product_packaging_qty])
    #                             # if invoice.product_id.type == 'product':
    #                             #     total_tare += product.tare_deduction
    #                             #     total_addition += product.addition_deduction
    #                             #     total_net += invoice.quantity
    #                             #     total_gross_weight += product.tare_deduction + product.addition_deduction + invoice.quantity
    #                             #     total += invoice.price_subtotal
    #             all_delvry_done = True
    #     print(invoice_line)
    #     addi = 0
    #     tare = 0
    #     for dict_val in invoice_line:
    #         if len(invoice_line[dict_val]) > 1:
    #             for val in invoice_line[dict_val]:
    #                  tare = tare + float(val[6])
    #                  addi = addi + float(val[7])
    #
    #     for dict_val in invoice_line:
    #         if len(invoice_line[dict_val]) > 1:
    #             invoice_line[dict_val] = [invoice_line[dict_val][0]]
    #             invoice_line[dict_val][0][6] = tare
    #             invoice_line[dict_val][0][7] = addi
    #
    #     print("hello")
    #     return {
    #         'data': {'invoice_line': invoice_line,
    #                  'total': f'{total:,}',
    #                  'tare_total': f'{total_tare:,}',
    #                  'addi_total': f'{total_addition:,}',
    #                  'total_net': f'{total_net:,}',
    #                  'total_gross': f'{total_gross_weight:,}'
    #                  },
    #         'docs': docs,
    #     }

    def _get_report_values(self, docids, data=None):
        invoice_line = {}
        total_tare = 0
        total_addition = 0
        total_NW = 0
        total_GW = 0
        total_amount = 0
        total_lines = 0
        if docids:
            docs = self.env['account.move'].search([('id', '=', docids[0])])
        else:
            docs = self.env['account.move'].search([('id', '=', data['form']['id'])])

        for invoice in docs.invoice_line_ids:
            for stock in invoice.stock_move_line_ids:
                if invoice.id not in invoice_line.keys():
                    invoice_line[invoice.id] = {stock.picking_id.carrier_tracking_ref: [invoice.product_id.name,
                                                                                        stock.picking_id.carrier_tracking_ref,
                                                                                        stock.picking_id.name,
                                                                                        stock.location_dest_id.name,
                                                                                        stock.tare_deduction + stock.addition_deduction + stock.qty_done,
                                                                                        stock.qty_done,
                                                                                        stock.tare_deduction,
                                                                                        stock.addition_deduction,
                                                                                        invoice.price_unit * 40 if invoice.product_id and invoice.product_id.type == 'product' else 0,
                                                                                        invoice.price_unit * stock.qty_done,
                                                                                        stock.qty_done if stock.move_id.purchase_line_id.product_packaging_qty else 0.0]}
                    total_lines = total_lines + 1
                    total_tare = total_tare + stock.tare_deduction
                    total_addition = total_addition + stock.addition_deduction
                    total_GW = total_GW + stock.tare_deduction + stock.addition_deduction + stock.qty_done
                    total_NW = total_NW + stock.qty_done
                    total_amount = total_amount + (invoice.price_unit * stock.qty_done)
                else:
                    print("cccc")
                    if stock.picking_id.carrier_tracking_ref in invoice_line[invoice.id].keys():
                        invoice_line[invoice.id][stock.picking_id.carrier_tracking_ref][10] = float(
                            invoice_line[invoice.id][stock.picking_id.carrier_tracking_ref][
                                10]) + (stock.qty_done if stock.move_id.purchase_line_id.product_packaging_qty else 0.0)

                        invoice_line[invoice.id][stock.picking_id.carrier_tracking_ref][6] = float(
                            invoice_line[invoice.id][stock.picking_id.carrier_tracking_ref][
                                6]) + stock.tare_deduction

                        invoice_line[invoice.id][stock.picking_id.carrier_tracking_ref][7] = float(
                            invoice_line[invoice.id][stock.picking_id.carrier_tracking_ref][
                                7]) + stock.addition_deduction

                        invoice_line[invoice.id][stock.picking_id.carrier_tracking_ref][4] = float(
                            invoice_line[invoice.id][stock.picking_id.carrier_tracking_ref][
                                4]) + (stock.tare_deduction + stock.addition_deduction + stock.qty_done)

                        invoice_line[invoice.id][stock.picking_id.carrier_tracking_ref][5] = float(
                            invoice_line[invoice.id][stock.picking_id.carrier_tracking_ref][
                                5]) + (stock.qty_done)

                        invoice_line[invoice.id][stock.picking_id.carrier_tracking_ref][9] = float(
                            invoice_line[invoice.id][stock.picking_id.carrier_tracking_ref][
                                9]) + (invoice.price_unit * stock.qty_done)

                        total_tare = total_tare + stock.tare_deduction
                        total_addition = total_addition + stock.addition_deduction
                        total_GW = total_GW + stock.tare_deduction + stock.addition_deduction + stock.qty_done
                        total_NW = total_NW + stock.qty_done
                        total_amount = total_amount + (invoice.price_unit * stock.qty_done)
                    else:
                        invoice_line[invoice.id][stock.picking_id.carrier_tracking_ref] = [invoice.product_id.name,
                                                                                            stock.picking_id.carrier_tracking_ref,
                                                                                            stock.picking_id.name,
                                                                                            stock.location_dest_id.name,
                                                                                            stock.tare_deduction + stock.addition_deduction + stock.qty_done,
                                                                                            stock.qty_done,
                                                                                            stock.tare_deduction,
                                                                                            stock.addition_deduction,
                                                                                            invoice.price_unit * 40 if invoice.product_id and invoice.product_id.type == 'product' else 0,
                                                                                            invoice.price_unit * stock.qty_done,
                                                                                            stock.qty_done if stock.move_id.purchase_line_id.product_packaging_qty else 0.0]

                        total_lines = total_lines + 1
                        total_tare = total_tare + stock.tare_deduction
                        total_addition = total_addition + stock.addition_deduction
                        total_GW = total_GW + stock.tare_deduction + stock.addition_deduction + stock.qty_done
                        total_NW = total_NW + stock.qty_done
                        total_amount = total_amount + (invoice.price_unit * stock.qty_done)

        print(total_GW)
        print(total_NW)
        print(total_amount)
        print(total_tare)
        print(total_addition)
        # total_lines = len(invoice_line)
        return {
            'data': {'invoice_line': invoice_line,
                     'total_amount': total_amount,
                     'tare_total': total_tare,
                     'addi_total': total_addition,
                     'total_net': total_NW,
                     'total_gross': total_GW,
                     'total_lines': total_lines
                     },
            'docs': docs,
        }




