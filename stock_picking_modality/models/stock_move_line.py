# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    modality_id = fields.Many2one(
        related='move_id.modality_id',
        store=True,
    )
    destiny_id = fields.Many2one(
        related='move_id.destiny_id',
        store=True,
    )
    zone_id = fields.Many2one(
        related='move_id.zone_id',
        store=True,
    )
    price = fields.Float(
        related='move_id.price',
    )
    total_price = fields.Float(
        related='move_id.total_price',
    )



