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
        related='move_line_ids.lot_id',
    )
    destiny = fields.Selection(
        selection=[('ciudad', 'Ciudad'), ('provincia_cercana', 'Provincia cercana'),
                   ('provincia_lejana', 'Provincia lejana')],
        string='Destino',
    )

    @api.depends('product_uom_qty', 'price')
    def _compute_total_price(self):
        for move in self:
            move.total_price = move.product_uom_qty * move.price

    @api.onchange('modality_id')
    def _on_change_price(self):
        for move in self:
            move.price = move.modality_id.price

    @api.onchange('modality_id', 'destiny')
    def _on_change_price(self):
        for move in self:
            if move.modality_id and move.destiny == 'ciudad':
                if move.modality_id.name == 'Simple':
                    move.price = 14.0
                else:
                    move.price = 14.0 / 2
            if move.modality_id and move.destiny == 'provincia_cercana':
                if move.modality_id.name == 'Simple':
                    move.price = 9.0
                else:
                    move.price = 9.0 / 2
            if move.modality_id and move.destiny == 'provincia_lejana':
                if move.modality_id.name == 'Simple':
                    move.price = 11.0
                else:
                    move.price = 11.0 / 2
