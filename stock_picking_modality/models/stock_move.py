# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    modality_id = fields.Many2one(
        comodel_name='stock.picking.modality',
        string='Modality',
    )
    modality_price_ids = fields.One2many(
        comodel_name='rate.picking.modality.price',
        related='rate_id.modality_price_ids',
        string='Modalities and Prices',
    )
    price = fields.Float(
        string='Precio',
        compute='_on_change_price',
    )
    total_price = fields.Float(
        string='Precio total',
        compute='_compute_total_price',
        store=True,
    )
    lot_id = fields.Many2one(
        related='move_line_ids.lot_id',
    )
    rate_id = fields.Many2one(
        comodel_name='rate.picking.destiny',
        string='Destiny',
    )

    @api.depends('product_uom_qty', 'price')
    def _compute_total_price(self):
        for move in self:
            move.total_price = move.product_uom_qty * move.price

    @api.onchange('modality_id', 'rate_id')
    def _on_change_price(self):
        for move in self:
            modality_price = move.modality_price_ids.filtered(
                lambda x: x.modality_id == move.modality_id and x.rate_id == move.rate_id
            )
            move.price = modality_price.price if modality_price else 0.0
