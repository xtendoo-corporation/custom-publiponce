# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import api, fields, models


class StockMovePlanning(models.Model):
    _name = 'stock.move.planning'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Stock Move Planning',
        compute='_compute_name'
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
    date_scheduled_time = fields.Datetime(
        string='Date Scheduled time',
        required=True,
        readonly=False,
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
        readonly=False,
        compute='_compute_qty',
        inverse='_inverse_qty',
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
    order_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Order Line',
    )
    color = fields.Integer(
        string='Color',
        help='1-Rojo, 2-Naranja, 3-Verde lima, 4-Azul, 5-Morado Oscuro, 6-Rojo anaranjado,'
                    ' 7-Azul verdoso, 8-Azul oscuro, 9-Burdeos, 10-Verde, 11-Morado Odoo, '
    )
    tag_ids = fields.Many2many(
        comodel_name='res.partner',
        readonly=True,
        string='Cliente',
    )
    partner_color = fields.Integer(
        string='Partner Color',
        compute='_compute_partner_color'
    )
    in_stock = fields.Boolean(
        string='In Stock',
        compute='_compute_in_stock',
        store=True,
    )

    @api.depends('order_line_id')
    def _compute_qty(self):
        for record in self:
            record.quantity = record.order_line_id.product_uom_qty if record.order_line_id else 0

    def _inverse_qty(self):
        for record in self:
            if record.order_line_id:
                record.order_line_id.product_uom_qty = record.quantity

    @api.depends('product_id', 'quantity')
    def _compute_in_stock(self):
        for record in self:
            if record.product_id:
                stock_quant = self.env['stock.quant'].search([
                    ('product_id', '=', record.product_id.id),
                    ('location_id.usage', '=', 'internal')
                ], limit=1)
                record.in_stock = stock_quant.quantity >= record.quantity
            else:
                record.in_stock = False

    @api.depends('product_name', 'quantity')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.product_name} - {record.quantity}"

    @api.depends('partner_id')
    def _compute_partner_color(self):
        for record in self:
            record.partner_color = record.partner_id.color if record.partner_id else 0

    @api.model
    def create(self, vals):
        if 'partner_id' in vals:
            partner_id = vals['partner_id']
            vals['tag_ids'] = [(6, 0, [partner_id])]
        return super(StockMovePlanning, self).create(vals)

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

    @api.model
    def mark_as_delivered(self):
        yesterday = fields.Date.today() - timedelta(days=1)
        plannings = self.search([
            ('date_scheduled', '=', yesterday),
            ('is_delivered', '=', False),
        ])
        plannings.write({'is_delivered': True})
