# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Order Line',
    )
    modality_id = fields.Many2one(
        comodel_name='stock.picking.modality',
        string='Modality',
        related='sale_line_id.modality_id',
        store=True,
    )
    destiny_id = fields.Many2one(
        comodel_name='stock.picking.destiny',
        string='Destiny',
        related='sale_line_id.destiny_id',
        store=True,
    )
    zone_id = fields.Many2one(
        comodel_name='stock.picking.zone',
        string='Zone',
        related='sale_line_id.zone_id',
        store=True,
    )
    # modality_id = fields.Many2one(
    #     comodel_name='stock.picking.modality',
    #     string='Modality',
    #     store=True,
    # )
    # destiny_id = fields.Many2one(
    #     comodel_name='stock.picking.destiny',
    #     string='Destiny',
    #     store=True,
    # )
    # zone_id = fields.Many2one(
    #     comodel_name='stock.picking.zone',
    #     string='Zone',
    #     store=True,
    # )
    price = fields.Float(
        string='Precio',
        compute='_on_change_price',
    )
    total_price = fields.Float(
        string='Precio total',
        compute='_compute_total_price',
    )

    @api.onchange('modality_id', 'destiny_id', 'zone_id')
    def _on_change_price(self):
        self.price = 0
        for move in self:
            modality_price = self.env['stock.picking.modality.destiny.price'].search(
                [("modality_id", '=', move.modality_id.id), ("destiny_id", '=', move.destiny_id.id),
                 ("zone_id", '=', move.zone_id.id)], limit=1
            )
            if modality_price:
                move.price = modality_price.price

    @api.depends('product_uom_qty', 'price')
    def _compute_total_price(self):
        for move in self:
            move.total_price = move.product_uom_qty * move.price

    @api.onchange('modality_id')
    def _onchange_modality_id(self):
        if self.modality_id:
            destiny_ids = self.env['stock.picking.modality.destiny.price'].search(
                [('modality_id', '=', self.modality_id.id)]).mapped('destiny_id.id')
            if self.destiny_id.id not in destiny_ids:
                self.destiny_id = False
            return {
                'domain': {
                    'destiny_id': [('id', 'in', destiny_ids)]
                }
            }
        else:
            self.destiny_id = False
            return {
                'domain': {
                    'destiny_id': []
                }
            }

    @api.onchange('destiny_id')
    def _onchange_destiny_id(self):
        if self.destiny_id and self.modality_id:
            zone_ids = self.env['stock.picking.modality.destiny.price'].search(
                [('modality_id', '=', self.modality_id.id), ('destiny_id', '=', self.destiny_id.id)]).mapped(
                'zone_id.id')
            if self.zone_id.id not in zone_ids:
                self.zone_id = False
            return {
                'domain': {
                    'zone_id': [('id', 'in', zone_ids)]
                }
            }
        else:
            self.zone_id = False
            return {
                'domain': {
                    'zone_id': []
                }
            }
