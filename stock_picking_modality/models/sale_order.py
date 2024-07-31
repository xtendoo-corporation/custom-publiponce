# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    modality_id = fields.Many2one(
        comodel_name='stock.picking.modality',
        string='Modality',
    )
    destiny_id = fields.Many2one(
        comodel_name='stock.picking.destiny',
        string='Destiny',
    )
    zone_id = fields.Many2one(
        comodel_name='stock.picking.zone',
        string='Zone',
    )

    # def action_confirm(self):
    #     res = super().action_confirm()
    #     for line in self.order_line:
    #         date_scheduled = self.date_order if self.date_order else False
    #         existing_plannings = self.env['stock.move.planning'].search([
    #             ('date_scheduled', '=', date_scheduled)
    #         ])
    #         planning_count = len(existing_plannings)
    #         scheduled_time = datetime.combine(date_scheduled, datetime.min.time()) + timedelta(hours=8 + planning_count)
    #         self.env['stock.move.planning'].create({
    #             'product_id': line.product_id.id,
    #             'product_name': line.product_id.name,
    #             'modality_id': line.modality_id.id if line.modality_id else False,
    #             'destiny_id': line.destiny_id.id if line.destiny_id else False,
    #             'zone_id': line.zone_id.id if line.zone_id else False,
    #             'res_partner_id': False,
    #             'order_id': self.id,
    #             'order_line_id': line.id,
    #             'partner_id': self.partner_id.id if self.partner_id else False,
    #             'date_scheduled': date_scheduled,
    #             'date_scheduled_time': scheduled_time,
    #             'quantity': line.product_uom_qty,
    #             'is_delivered': False,
    #             'delivery_date': False,
    #         })
    #         print("*"*80)
    #         print(line.id)
    #         print(line.product_id)
    #         print(line.product_uom_qty)
    #     return res

    @api.onchange('modality_id')
    def _onchange_modality_id(self):
        if self.modality_id:
            destiny_ids = self.env['stock.picking.modality.destiny.price'].search(
                [('modality_id', '=', self.modality_id.id)]).mapped('destiny_id.id')
            if self.destiny_id.id not in destiny_ids:
                self.destiny_id = False
            return {
                'domain': {
                    'destiny_id': [('id', 'in', destiny_ids)]
                }
            }
        else:
            self.destiny_id = False
            return {
                'domain': {
                    'destiny_id': []
                }
            }

    @api.onchange('destiny_id')
    def _onchange_destiny_id(self):
        if self.destiny_id and self.modality_id:
            zone_ids = self.env['stock.picking.modality.destiny.price'].search(
                [('modality_id', '=', self.modality_id.id), ('destiny_id', '=', self.destiny_id.id)]).mapped(
                'zone_id.id')
            if self.zone_id.id not in zone_ids:
                self.zone_id = False
            return {
                'domain': {
                    'zone_id': [('id', 'in', zone_ids)]
                }
            }
        else:
            self.zone_id = False
            return {
                'domain': {
                    'zone_id': []
                }
            }

    def action_view_plannings(self):
        self.ensure_one()
        action = self.env.ref('stock_picking_modality.action_sale_order_line_planning').read()[0]
        action['domain'] = [('order_id', '=', self.id)]
        # action['domain'] = [('product_id', 'in', self.order_line.mapped('product_id').ids)]
        return action
