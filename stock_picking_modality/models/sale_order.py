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
        return action

    def update_stock_transfers_with_order_line(self):
        for line in self.order_line:
            transfers = self.env['stock.picking'].search([
                ('sale_id', '=', self.id)
            ])
            for transfer in transfers:
                for move in transfer.move_ids_without_package:
                    move.write({'sale_line_id': line.id})

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.update_stock_transfers_with_order_line()
        return res
