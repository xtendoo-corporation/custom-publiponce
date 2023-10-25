# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    modality_id = fields.Many2one(
        related='move_id.modality_id',
    )
    destiny_id = fields.Many2one(
        related='move_id.destiny_id',
    )
    price = fields.Float(
        related='move_id.price',
    )
    total_price = fields.Float(
        related='move_id.total_price',
    )

