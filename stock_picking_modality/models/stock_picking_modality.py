# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPickingModality(models.Model):
    _name = 'stock.picking.modality'

    name = fields.Char(
        string='Name',
    )
    price = fields.Float(
        string='Price',
    )
    stock_move_ids = fields.One2many(
        comodel_name='stock.move',
        inverse_name='modality_id',
        string='Stock Moves'
    )
    stock_move_count = fields.Integer(
        string='Stock Move Lines Count',
        compute='_compute_stock_move_count'
    )

    @api.depends('stock_move_ids')
    def _compute_stock_move_count(self):
        for modality in self:
            modality.stock_move_count = len(modality.stock_move_ids)

