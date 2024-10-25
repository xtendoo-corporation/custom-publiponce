# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import api, fields, models


class PartialDeliveryWizard(models.TransientModel):
    _name = 'partial.delivery.wizard'
    _description = 'Partial Delivery Wizard'

    cantidad_entregada = fields.Float(
        string='Cantidad Entregada', required=True
    )
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        required=True
    )
    route_id = fields.Many2one(
        'stock.route',
        string='Route',
        required=True,
    )
    date_scheduled = fields.Date(
        string='Date Scheduled',
        readonly=False,
    )
    modality_id = fields.Many2one(
        'stock.picking.modality',
        string='Modality',
        required=True,
    )
    destiny_id = fields.Many2one(
        'stock.picking.destiny',
        string='Destiny',
        required=True,
    )
    zone_id = fields.Many2one(
        'stock.picking.zone',
        string='Zone',
        required=True,
    )

    def action_confirm_partial_delivery(self):
        self.ensure_one()
        sale_order_line = self.sale_order_line_id
        remaining_qty = sale_order_line.product_uom_qty - self.cantidad_entregada

        sale_order_line.product_uom_qty = self.cantidad_entregada
        sale_order_line.state_planning = 'delivered'

        picking = self.env['stock.picking'].search([
            ('origin', '=', sale_order_line.order_id.name),
            ('state', 'in', ['assigned']),
        ], limit=1)
        print(f"Picking found: {picking}")
        print(f"Picking name: {picking.name}")

        if picking:
            print(f"Picking move lines: {picking.move_line_ids}")
            print(f"Sale order line product ID: {sale_order_line.product_id.id}")
            move_line = picking.move_line_ids.filtered(lambda m: m.product_id == sale_order_line.product_id)
            print(f"Move line found: {move_line}")

            if move_line:
                print("Confirming picking...")
                picking.action_confirm()
                print(f"Setting quantity done to: {self.cantidad_entregada}")
                move_line.write({'qty_done': self.cantidad_entregada})  # Correct attribute name
                print("Validating picking...")
                picking.button_validate()
                print("Picking validated.")

                new_picking = self.env['stock.picking'].search([
                    ('origin', '=', sale_order_line.order_id.name),
                    ('state', '=', 'waiting'),
                ], limit=1)

                if new_picking:
                    print("Assigning new picking...")
                    new_picking.action_assign()

                    for move in new_picking.move_ids_without_package:
                        move.quantity_done = move.product_uom_qty
                        print(f"Move ID: {move.id}, Quantity Done: {move.quantity_done}")

                    print("Validating new picking...")
                    new_picking.button_validate()
                    print("New picking validated.")

            new_sale_order = self.env['sale.order'].create({
                'partner_id': sale_order_line.order_id.partner_id.id,
                'order_line': [(0, 0, {
                    'product_id': sale_order_line.product_id.id,
                    'product_uom_qty': remaining_qty,
                    'product_uom': sale_order_line.product_uom.id,
                    'price_unit': sale_order_line.price_unit,
                    'name': sale_order_line.name,
                    'state_planning': 'in_stock',
                    'date_scheduled': self.date_scheduled,
                    'route_id': self.route_id.id,
                    'modality_id': self.modality_id.id,
                    'destiny_id': self.destiny_id.id,
                    'zone_id': self.zone_id.id,
                })],
            })

            # new_sale_order.action_confirm()
            #
            # new_sale_order_line = new_sale_order.order_line[0]
            # print("*" * 20, new_sale_order_line.state_planning)
            # # Ensure the new sale order line has the correct state
            # new_sale_order_line.state_planning = 'in_stock'
            # print("*" * 20, new_sale_order_line.state_planning)

            sale_order_line.state = 'done'

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
