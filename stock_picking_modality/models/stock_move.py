# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    modality_id = fields.Many2one(
        comodel_name='stock.picking.modality',
        string='Modality',
    )
    destiny_id = fields.Many2one(
        comodel_name='stock.picking.destiny',
        string='Destiny',
    )
    price = fields.Float(
        string='Precio',
        compute='_on_change_price',
    )
    total_price = fields.Float(
        string='Precio total',
        compute='_compute_total_price',
    )

    @api.onchange('modality_id', 'destiny_id')
    def _on_change_price(self):
        self.price = 0
        for move in self:
            modality_price = self.env['stock.picking.modality.destiny.price'].search(
                [("modality_id", '=', move.modality_id.id), ("destiny_id", '=', move.destiny_id.id)], limit=1
            )
            if modality_price:
                move.price = modality_price.price

    @api.depends('product_uom_qty', 'price')
    def _compute_total_price(self):
        for move in self:
            move.total_price = move.product_uom_qty * move.price
