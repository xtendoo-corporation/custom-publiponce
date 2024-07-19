# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMovePlanning(models.Model):
    _name = 'stock.move.planning'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Stock Move Planning',
    )
    stock_move_id = fields.Many2one(
        comodel_name='stock.move',
        string='Stock Move',
        readonly=False,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product id',
    )
    product_name = fields.Char(
        string='Product',
    )
    modality_id = fields.Many2one(
        comodel_name='stock.picking.modality',
        string='Modality',
    )
    destiny_id = fields.Many2one(
        comodel_name='stock.picking.destiny',
        string='Destiny',
    )
    zone_id = fields.Many2one(
        comodel_name='stock.picking.zone',
        string='Zone',
    )
    res_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Resource',
        readonly=False,
        domain=[('is_resource', '=', True)],
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        readonly=False,
    )
    is_delivered = fields.Boolean(
        string='Delivered',
        default=False,
    )
    delivery_date = fields.Date(
        string='Delivery Date',
        readonly=False,
    )
    date_scheduled = fields.Date(
        string='Date Scheduled',
        required=True,
        readonly=False,
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
        readonly=False,
    )
    price = fields.Float(
        string='Price',
        compute='_on_change_price',
    )
    total_price = fields.Float(
        string='Total price',
        compute='_compute_total_price',
    )
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Order',
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

    @api.depends('quantity', 'price')
    def _compute_total_price(self):
        for move in self:
            move.total_price = move.quantity * move.price

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
