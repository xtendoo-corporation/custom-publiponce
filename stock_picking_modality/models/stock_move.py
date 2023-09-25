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
    total_price = fields.Float(
        string='Precio total',
        compute='_compute_total_price',
        store=True,
    )
    lot_id = fields.Many2one(
        comodel_name='stock.lot',
        string='Lote/Nº de serie',
    )

    @api.depends('product_uom_qty', 'price')
    def _compute_total_price(self):
        for move in self:
            move.total_price = move.product_uom_qty * move.price

    @api.onchange('modality_id')
    def _on_change_price(self):
        for move in self:
            move.price = move.modality_id.price


