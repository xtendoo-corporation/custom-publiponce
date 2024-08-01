# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import api, fields, models

class PartialDeliveryWizard(models.TransientModel):
    _name = 'partial.delivery.wizard'
    _description = 'Partial Delivery Wizard'

    cantidad_entregada = fields.Float(string='Cantidad Entregada', required=True)
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', required=True)

    def action_confirm_partial_delivery(self):
        self.ensure_one()
        sale_order_line = self.sale_order_line_id
        remaining_qty = sale_order_line.product_uom_qty - self.cantidad_entregada

        # Update the current line with the delivered quantity
        sale_order_line.product_uom_qty = self.cantidad_entregada
        sale_order_line.is_delivered = True
        sale_order_line.state_planning = 'repartido'

        # Create a new sale order line with the remaining quantity
        if remaining_qty > 0:
            # Identify the main stock location
            main_stock_location = self.env.ref('stock.stock_location_stock')

            # Create an internal transfer
            internal_transfer = self.env['stock.picking'].create({
                'location_id': sale_order_line.order_id.warehouse_id.lot_stock_id.id,
                'location_dest_id': main_stock_location.id,
                'picking_type_id': self.env.ref('stock.picking_type_internal').id,
            })

            stock_move = self.env['stock.move'].create({
                'name': sale_order_line.name,
                'product_id': sale_order_line.product_id.id,
                'product_uom_qty': remaining_qty,
                'product_uom': sale_order_line.product_uom.id,
                'location_id': sale_order_line.order_id.warehouse_id.lot_stock_id.id,
                'location_dest_id': main_stock_location.id,
                'picking_id': internal_transfer.id,
            })

            # Validate the transfer
            internal_transfer.action_confirm()
            stock_move.quantity_done = remaining_qty
            internal_transfer.button_validate()

            new_sale_order = self.env['sale.order'].create({
                'partner_id': sale_order_line.order_id.partner_id.id,
                'order_line': [(0, 0, {
                    'product_id': sale_order_line.product_id.id,
                    'product_uom_qty': remaining_qty,
                    'product_uom': sale_order_line.product_uom.id,
                    'price_unit': sale_order_line.price_unit,
                    'name': sale_order_line.name,
                    'state_planning': 'en_stock',
                    'date_scheduled': fields.Datetime.now() + timedelta(days=1),
                })],
            })

            # Mark the original sale order line as completed
            sale_order_line.state = 'done'
