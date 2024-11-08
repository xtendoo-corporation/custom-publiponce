# Copyright 2023 Salvador, Abraham (https://xtsendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta, datetime

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleOrderLine(models.Model):
    # _inherit = 'sale.order.line'
    _name = 'sale.order.line'
    _inherit = ['sale.order.line', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Stock Move Planning',
        compute='_compute_name'
    )
    modality_id = fields.Many2one(
        comodel_name='stock.picking.modality',
        string='Modality',
        required=True,
    )
    destiny_id = fields.Many2one(
        comodel_name='stock.picking.destiny',
        string='Destiny',
        required=True,
    )
    zone_id = fields.Many2one(
        comodel_name='stock.picking.zone',
        string='Zone',
        required=True,
    )
    price_fee = fields.Float(
        comodel_name='stock.picking.modality.destiny.price',
        string='Precio Tarifa',
    )
    date_scheduled = fields.Date(
        string='Date Scheduled',
        readonly=False,
        required=True,
    )
    date_scheduled_time = fields.Datetime(
        string='Date Scheduled Time',
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
        ('waiting_reception', 'Waiting for reception'),
        ('in_stock_partially', 'Partially in stock'),
        ('in_stock', 'In stock'),
        ('in_van', 'In van'),
        ('delivered', 'Delivered')
    ], string='State Planning',
        readonly=True,
        default='waiting_reception',
        store=True,
        compute='_compute_state_planning'
    )
    route_id = fields.Many2one(
        'stock.route',
        string='Route',
    )


    @api.depends('partner_id', 'zone_id', 'product_uom_qty')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.partner_id.name} - {record.zone_id.name} - {record.product_uom_qty}"

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

    @api.onchange('state')
    def _onchange_state(self):
        """Limpia el campo route_id si el estado vuelve a borrador."""
        if self.state == 'draft':
            self.route_id = False

    @api.model
    def create(self, vals):
        # Validación: si el estado es 'sale', `route_id` es obligatorio
        if vals.get('state') == 'draft' and not vals.get('route_id'):
            raise UserError("El campo Ruta es obligatorio cuando se crea un pedido de venta.")
        # Set default date_scheduled_time to date_scheduled at 08:00:00
        if 'date_scheduled' in vals and vals['date_scheduled']:
            date_scheduled = fields.Date.from_string(vals['date_scheduled'])
            date_scheduled_time = datetime.combine(date_scheduled, datetime.min.time()) + timedelta(hours=8)
            while self.search([('date_scheduled_time', '=', date_scheduled_time)]):
                date_scheduled_time += timedelta(hours=1)
            vals['date_scheduled_time'] = date_scheduled_time
        # Check for duplicate product lines on the same scheduled date
        if 'product_id' in vals and 'date_scheduled' in vals:
            existing_line = self.search([
                ('product_id', '=', vals['product_id']),
                ('date_scheduled', '=', vals['date_scheduled']),
                ('state_planning', '!=', 'delivered')
            ])
            if existing_line:
                raise ValidationError("No pueden haber dos líneas con el mismo producto en la misma fecha planificada.")

        # Create the record
        record = super(SaleOrderLine, self).create(vals)

        # Update tag_ids field
        if record.partner_id and record.partner_id not in record.tag_ids:
            record.tag_ids = [(4, record.partner_id.id)]

        return record


    def write(self, vals):
        for line in self:
            if (vals.get('state') == 'draft' or line.state == 'draft') and not vals.get('route_id', line.route_id):
                raise UserError("El campo Ruta es obligatorio para confirmar el pedido de venta.")
        if 'product_id' in vals or 'date_scheduled' in vals and vals['date_scheduled']:
            for line in self:
                product_id = vals.get('product_id', line.product_id.id)
                date_scheduled = vals.get('date_scheduled', line.date_scheduled)
                if isinstance(date_scheduled, str):
                    date_scheduled = fields.Date.from_string(date_scheduled)
                date_scheduled_time = datetime.combine(date_scheduled, datetime.min.time()) + timedelta(hours=8)
                while self.search([('date_scheduled_time', '=', date_scheduled_time)]):
                    date_scheduled_time += timedelta(hours=1)
                vals['date_scheduled_time'] = date_scheduled_time
                existing_line = self.search([
                    ('product_id', '=', product_id),
                    ('date_scheduled', '=', date_scheduled),
                    ('id', '!=', line.id),
                    ('state_planning', '!=', 'delivered')
                ])
                if existing_line:
                    raise ValidationError(
                        "No pueden haber dos líneas con el mismo producto en la misma fecha planificada.")
        res = super(SaleOrderLine, self).write(vals)
        return res

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


    @api.onchange('modality_id', 'date_scheduled', 'route_id')
    def _onchange_modality_id(self):
        if not self.date_scheduled or not self.route_id:
            return

        allowed_modality_ids = []
        simple_lines = self.search([
            ('date_scheduled', '=', self.date_scheduled),
            ('route_id', '=', self.route_id.id),
            ('modality_id.name', '=', 'Simple')
        ])
        double_lines = self.search([
            ('date_scheduled', '=', self.date_scheduled),
            ('route_id', '=', self.route_id.id),
            ('modality_id.name', '=', 'Doble')
        ])
        triple_lines = self.search([
            ('date_scheduled', '=', self.date_scheduled),
            ('route_id', '=', self.route_id.id),
            ('modality_id.name', '=', 'Triple')
        ])

        if not simple_lines:
            allowed_modality_ids = self.env['stock.picking.modality'].search([('name', '=', 'Simple')]).ids
        elif not double_lines:
            allowed_modality_ids = self.env['stock.picking.modality'].search([('name', 'in', ['Simple', 'Doble'])]).ids
        elif not triple_lines:
            allowed_modality_ids = self.env['stock.picking.modality'].search(
                [('name', 'in', ['Simple', 'Doble', 'Triple'])]).ids
        else:
            allowed_modality_ids = self.env['stock.picking.modality'].search([]).ids

        if self.modality_id:
            destiny_ids = self.env['stock.picking.modality.destiny.price'].search(
                [('modality_id', '=', self.modality_id.id)]).mapped('destiny_id.id')
            if self.destiny_id.id not in destiny_ids:
                self.destiny_id = False
            return {
                'domain': {
                    'modality_id': [('id', 'in', allowed_modality_ids)],
                    'destiny_id': [('id', 'in', destiny_ids)]
                }
            }
        else:
            self.destiny_id = False
            return {
                'domain': {
                    'modality_id': [('id', 'in', allowed_modality_ids)],
                    'destiny_id': []
                }
            }

    @api.onchange('date_scheduled')
    def _onchange_date_scheduled(self):
        if self.date_scheduled:
            self.modality_id = False
            self.zone_id = False
            self.destiny_id = False
            date_scheduled = fields.Date.from_string(self.date_scheduled)
            date_scheduled_time = datetime.combine(date_scheduled, datetime.min.time()) + timedelta(hours=8)
            while self.search([('date_scheduled_time', '=', date_scheduled_time)]):
                date_scheduled_time += timedelta(hours=1)
            self.date_scheduled_time = date_scheduled_time


    @api.onchange('route_id')
    def _onchange_route_id(self):
        if self.route_id:
            self.modality_id = False
            self.zone_id = False
            self.destiny_id = False


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
            ('state_planning', '!=', 'delivered'),
        ])
        plannings.write({'state_planning': 'delivered'})


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
                    line.state_planning = 'delivered'
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
                line.state_planning = 'in_stock'


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
                line.state_planning = 'in_van'


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

    def action_view_sale_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.order_id.id,
            'target': 'current',
        }

    @api.depends('move_ids.move_line_ids.qty_done', 'move_ids.quantity_done')
    def _compute_state_planning(self):
        for line in self:
            print("*" * 100, "Entramos en la linea")
            line.state_planning = 'waiting_reception'
            print(
                f"Sale Order Line ID: {line.id}, Product: {line.product_id.name}, Quantity Ordered: {line.product_uom_qty}")

            purchase_picking = self.env['stock.picking'].search([
                ('sale_id', '=', line.order_id.id),
                ('picking_type_id.code', '=', 'incoming'),
                ('state', '=', 'done'),
                ('move_line_ids.location_dest_id.usage', '=', 'internal')
            ], limit=1)

            if purchase_picking:
                stock_location_id = self.env.ref('stock.stock_location_stock').id
                stock_quant = self.env['stock.quant'].search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', stock_location_id)
                ], limit=1)
                if stock_quant:
                    reserved_quantity = stock_quant.reserved_quantity
                    print(f"Reserved Stock Quantity: {reserved_quantity}")
                    if reserved_quantity >= line.product_uom_qty:
                        line.state_planning = 'in_stock'
                        print(f" Salir del estado en stock")
                    elif 0 < reserved_quantity < line.product_uom_qty:
                        line.state_planning = 'in_stock_partially'
                        print(f" Salir del estado en stock parcialmente")

            for move in line.move_ids:
                print(f"  Stock Move ID: {move.id}, Product: {move.product_id.name}, Quantity: {move.product_uom_qty},"
                      f"location_dest_id.usage: {move.location_dest_id.usage}")

                customer_moves = move.move_line_ids.filtered(
                    lambda x: x.qty_done == line.product_uom_qty and x.location_dest_id.usage == 'customer')
                if customer_moves:
                    line.state_planning = 'delivered'
                    print(f" Salir del estado delivered")
                    break

                transit_moves = move.move_line_ids.filtered(
                    lambda x: x.location_dest_id.usage == 'transit')
                if transit_moves:
                    if any(x.qty_done == line.product_uom_qty for x in transit_moves):
                        line.state_planning = 'in_van'
                        print(f" Salir del estado en furgon")
                        break
                    elif purchase_picking:
                        stock_location_id = self.env.ref('stock.stock_location_stock').id
                        stock_quant = self.env['stock.quant'].search([
                            ('product_id', '=', line.product_id.id),
                            ('location_id', '=', stock_location_id)
                        ], limit=1)
                        if stock_quant:
                            reserved_quantity = stock_quant.reserved_quantity
                            print(f"Reserved Stock Quantity: {reserved_quantity}")
                            if reserved_quantity >= line.product_uom_qty:
                                line.state_planning = 'in_stock'
                                print(f" Salir del estado en stock")
                            elif 0 < reserved_quantity < line.product_uom_qty:
                                line.state_planning = 'in_stock_partially'
                                print(f" Salir del estado en stock parcialmente")
                    if not purchase_picking:
                        line.state_planning = 'in_stock'
                        print(f" Salir del estado en stock")
                    break


    def show_related_stock_move_lines(self):
        for line in self:
            stock_moves = line.move_ids
            for move in stock_moves:
                for move_line in move.move_line_ids:
                    print(
                        f"Stock Move Line ID: {move_line.id}, Product: {move_line.product_id.name}, Quantity Done: {move_line.qty_done}, Location: {move_line.location_id.name}")
