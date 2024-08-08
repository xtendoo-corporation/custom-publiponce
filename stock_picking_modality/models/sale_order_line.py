# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    # _inherit = ['sale.order.line', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Stock Move Planning',
        compute='_compute_name'
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
    price_fee = fields.Float(
        comodel_name='stock.picking.modality.destiny.price',
        string='Precio Tarifa',
    )
    is_delivered = fields.Boolean(
        string='Delivered',
        default=False,
    )
    date_scheduled = fields.Date(
        string='Date Scheduled',
        required=True,
        readonly=False,
    )
    price = fields.Float(
        string='Price',
        compute='_on_change_price',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        related='order_id.partner_id',
    )
    tag_ids = fields.Many2many(
        comodel_name='res.partner',
        readonly=True,
        string='Cliente',
    )
    in_stock = fields.Boolean(
        string='In Stock',
        compute='_compute_in_stock',
        store=True,
    )
    color = fields.Integer(
        string='Color',
        help='1-Rojo, 2-Naranja, 3-Verde lima, 4-Azul, 5-Morado Oscuro, 6-Rojo anaranjado,'
             ' 7-Azul verdoso, 8-Azul oscuro, 9-Burdeos, 10-Verde, 11-Morado Odoo, '
    )
    partner_color = fields.Integer(
        string='Partner Color',
        compute='_compute_partner_color'
    )
    state_planning = fields.Selection([
        ('espera_recepcion', 'Espera recepción'),
        ('en_stock', 'En stock'),
        ('en_furgon', 'En furgón'),
        ('repartido', 'Repartido')
    ], string='State Planning',
        readonly=True,
        default='espera_recepcion',
        compute='_compute_state_planning')

    @api.depends('product_template_id', 'product_uom_qty')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.product_template_id.name} - {record.product_uom_qty}"

    @api.depends('partner_id')
    def _compute_partner_color(self):
        for record in self:
            record.partner_color = record.partner_id.color if record.partner_id else 0

    @api.depends('product_id', 'product_uom_qty')
    def _compute_in_stock(self):
        for record in self:
            if record.product_template_id:
                stock_quant = self.env['stock.quant'].search([
                    ('product_id', '=', record.product_template_id.id),
                    ('location_id.usage', '=', 'internal')
                ], limit=1)
                record.in_stock = stock_quant.quantity >= record.product_uom_qty
            else:
                record.in_stock = False

    @api.model
    def create(self, vals):
        record = super(SaleOrderLine, self).create(vals)
        if record.partner_id and record.partner_id not in record.tag_ids:
            record.tag_ids = [(4, record.partner_id.id)]
        return record

    @api.onchange('modality_id', 'destiny_id', 'zone_id')
    def _on_change_price(self):
        self.price = 0
        for line in self:
            modality_price = self.env['stock.picking.modality.destiny.price'].search(
                [("modality_id", '=', line.modality_id.id), ("destiny_id", '=', line.destiny_id.id),
                 ("zone_id", '=', line.zone_id.id)], limit=1
            )
            if modality_price:
                line.price = modality_price.price

    @api.onchange('zone_id')
    def _onchange_price_fee(self):
        if self.modality_id and self.destiny_id and self.zone_id:
            price_record = self.env['stock.picking.modality.destiny.price'].search([
                ('modality_id', '=', self.modality_id.id),
                ('destiny_id', '=', self.destiny_id.id),
                ('zone_id', '=', self.zone_id.id),
            ], limit=1)
            if price_record:
                self.price_fee = price_record.price
                self.purchase_price = self.price_fee
        else:
            self.price_fee = 0

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

    def action_deliver_products(self):
        for line in self:
            sale_order = line.order_id
            print(sale_order)
            if not sale_order:
                continue

            print("antes de buscar")
            last_transfer = self.env['stock.picking'].search([
                ('sale_id', '=', sale_order.id),
            ], order='date_done desc', limit=1)

            print(last_transfer)
            if last_transfer:
                print("realizar button validate")
                try:
                    for move in last_transfer.move_ids_without_package:
                        move.quantity_done = line.product_uom_qty
                        print(move.quantity_done)
                    last_transfer.button_validate()
                    print("realizado")
                    line.is_delivered = True
                    line.state_planning = 'repartido'
                except Exception as e:
                    print(f"Error during button_validate: {e}")

    def action_receive_products(self):
        for line in self:
            purchase_order = self.env['purchase.order'].search([
                ('origin', '=', line.order_id.name),
            ], limit=1)

            print(purchase_order)
            if not purchase_order:
                continue
            if purchase_order.state == 'draft':
                purchase_order.button_confirm()
                print("button_confirm")
            print("antes de buscar")
            last_receipt = self.env['stock.picking'].search([
                ('purchase_id', '=', purchase_order.id),
                ('state', 'in', ['assigned', 'waiting']),
            ], order='date_done desc', limit=1)

            print(last_receipt)

            if last_receipt:
                print("realizar button validate")
                for move in last_receipt.move_ids_without_package:
                    move.quantity_done = line.product_uom_qty
                last_receipt.button_validate()
                line.state_planning = 'en_stock'

    def action_move_to_truck(self):
        for line in self:
            transfer = self.env['stock.picking'].search([
                ('sale_id', '=', line.order_id.id),
                ('state', '=', 'assigned'),
            ], limit=1)
            print(f"Transfer ID: {transfer.id}")
            print(f"Transfer Name: {transfer.name}")
            print(f"Transfer State: {transfer.state}")
            print(f"Transfer Origin: {transfer.origin}")
            print(f"Transfer Partner: {transfer.partner_id.name}")
            if transfer:
                for move in transfer.move_ids_without_package:
                    move.quantity_done = line.product_uom_qty
                    print(f"Move ID: {move.id}, Quantity Done: {move.quantity_done}")

                transfer.button_validate()
                line.state_planning = 'en_furgon'

    def action_partial_delivery(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Partial Delivery',
            'res_model': 'partial.delivery.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_line_id': self.id,
            },
        }

    @api.depends('move_ids.move_line_ids.qty_done')
    def _compute_state_planning(self):
        for line in self:
            line.state_planning = 'espera_recepcion'
            print(
                f"Sale Order Line ID: {line.id}, Product: {line.product_id.name}, Quantity Ordered: {line.product_uom_qty}")

            purchase_picking = self.env['stock.picking'].search([
                ('sale_id', '=', line.order_id.id),
                ('picking_type_id.code', '=', 'incoming'),
                ('state', '=', 'done'),
                ('move_line_ids.location_dest_id.usage', '=', 'internal')
            ], limit=1)

            if purchase_picking:
                line.state_planning = 'en_stock'
                print(f" Salir del estado en stock")

            for move in line.move_ids:
                print(f"  Stock Move ID: {move.id}, Product: {move.product_id.name}, Quantity: {move.product_uom_qty},"
                      f"location_dest_id.usage: {move.location_dest_id.usage}")

                customer_moves = move.move_line_ids.filtered(
                    lambda x: x.qty_done == line.product_uom_qty and x.location_dest_id.usage == 'customer')
                if customer_moves:
                    line.state_planning = 'repartido'
                    line.is_delivered = True
                    break

                transit_moves = move.move_line_ids.filtered(
                    lambda x: x.qty_done == line.product_uom_qty and x.location_dest_id.usage == 'transit')
                if transit_moves:
                    line.state_planning = 'en_furgon'
                    print(f" Salir del estado en furgon")
                    break




                # internal_moves = move.move_line_ids.filtered(
                #     lambda x: x.qty_done == line.product_uom_qty and x.location_dest_id.usage == 'internal')
                # if internal_moves:
                #     line.state_planning = 'en_stock'
                #     break

    def show_related_stock_move_lines(self):
        for line in self:
            stock_moves = line.move_ids
            for move in stock_moves:
                for move_line in move.move_line_ids:
                    print(
                        f"Stock Move Line ID: {move_line.id}, Product: {move_line.product_id.name}, Quantity Done: {move_line.qty_done}, Location: {move_line.location_id.name}")
