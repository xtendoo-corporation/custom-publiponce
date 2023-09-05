# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _name = 'stock.move'

    modality_id = fields.Many2one(
        comodel_name='stock.picking.modality',
        string='Modality',
    )
    price = fields.Float(
        comoodel_name='stock.picking.modality',
        string='Price',
    )

    @api.onchange('picking_id.modality_id.price')
    def _onchange_price(self):
        for move in self:
            move.price = move.picking_id.modality_id.price
