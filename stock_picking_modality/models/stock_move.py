# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    modality_id = fields.Many2one(
        comodel_name='stock.picking.modality',
        string='Modality',
    )
    price = fields.Float(
        string='Price',
    )

    @api.onchange('modality_id')
    def _on_change_price(self):
        for move in self:
            move.price = move.modality_id.price
