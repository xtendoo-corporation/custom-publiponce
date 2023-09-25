# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions


class StockPickingModality(models.Model):
    _name = 'stock.picking.modality'

    name = fields.Char(
        string='Name',
        readonly=False,
        store=True,
    )
    price = fields.Float(
        string='Price',
        readonly=False,
        store=True,
    )
    stock_move_ids = fields.One2many(
        comodel_name='stock.move',
        inverse_name='modality_id',
        string='Stock Moves'
    )
    line_qty = fields.Integer(
        string='Cantidad de lineas',
        readonly=False,
        store=True,
    )

    def action_open_stock_move_filtered(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Moves',
            'res_model': 'stock.move',
            'view_mode': 'tree',
            'view_id': self.env.ref('stock.view_move_tree').id,
            'domain': [('modality_id', '=', self.id)],
            'target': 'current',
        }
