# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.tests import Form

class TestPlanning(TransactionCase):

    # some helpers
    def _create_customer(self):
        return self.env["res.partner"].create(
            {"name": "Test customer", "is_company": True}
        )

    def _create_warehouse(self):
        return self.env["stock.warehouse"].create(
            {"name": "Test warehouse", "code": "TWH"}
        )

    def _create_transit_location(self, warehouse):
        return self.env["stock.location"].create(
            {"name": "Transit location", "usage": "transit", "location_id": warehouse.view_location_id.id}
        )

    def _create_route(self, transit_location, stock_picking_transit_type,
                      stock_picking_customers_type):
        if not self.env['ir.model'].search([('model', '=', 'stock.route')]):
            raise ValueError(
                "Model 'stock.route' is not available. Ensure the required module is installed and loaded.")

        route = self.env["stock.route"].create(
            {"name": "Test route", "warehouse_selectable": True, "product_selectable": True, "sale_selectable": True}
        )

        self.env["stock.rule"].create({
            "name": "Buy",
            "location_src_id": self.env.ref('stock.stock_location_suppliers').id,
            "location_dest_id": self.env.ref('stock.stock_location_stock').id,
            "picking_type_id": self.env.ref('stock.picking_type_in').id,
            "route_id": route.id,
            "action": "buy",
            "procure_method": "make_to_order",
        })

        self.env["stock.rule"].create({
            "name": "Internal to Transit",
            "location_src_id": self.env.ref('stock.stock_location_stock').id,
            "location_dest_id": transit_location.id,
            "picking_type_id": stock_picking_transit_type.id,
            "route_id": route.id,
            "action": "pull_push",
            "procure_method": "mts_else_mto",
        })

        self.env["stock.rule"].create({
            "name": "Transit to Customers",
            "location_src_id": transit_location.id,
            "location_dest_id": self.env.ref('stock.stock_location_customers').id,
            "picking_type_id": stock_picking_customers_type.id,
            "route_id": route.id,
            "action": "pull_push",
            "procure_method": "mts_else_mto",
        })

        return route

    def _create_route_with_last_two_rules(self, transit_location, stock_picking_transit_type,
                                          stock_picking_customers_type):
        if not self.env['ir.model'].search([('model', '=', 'stock.route')]):
            raise ValueError(
                "Model 'stock.route' is not available. Ensure the required module is installed and loaded.")

        route = self.env["stock.route"].create(
            {"name": "Test route 2", "warehouse_selectable": True, "product_selectable": True, "sale_selectable": True}
        )

        self.env["stock.rule"].create({
            "name": "Internal to Transit",
            "location_src_id": self.env.ref('stock.stock_location_stock').id,
            "location_dest_id": transit_location.id,
            "picking_type_id": stock_picking_transit_type.id,
            "route_id": route.id,
            "action": "pull_push",
            "procure_method": "mts_else_mto",
        })

        self.env["stock.rule"].create({
            "name": "Transit to Customers",
            "location_src_id": transit_location.id,
            "location_dest_id": self.env.ref('stock.stock_location_customers').id,
            "picking_type_id": stock_picking_customers_type.id,
            "route_id": route.id,
            "action": "pull_push",
            "procure_method": "mts_else_mto",
        })

        return route

    def _create_route_with_inverse(self, transit_location, stock_picking_transit_type,
                                   stock_picking_customers_type):
        if not self.env['ir.model'].search([('model', '=', 'stock.route')]):
            raise ValueError(
                "Model 'stock.route' is not available. Ensure the required module is installed and loaded.")

        route = self.env["stock.route"].create(
            {"name": "Test route with inverse", "warehouse_selectable": True, "product_selectable": True,
             "sale_selectable": True}
        )

        self.env["stock.rule"].create({
            "name": "Buy",
            "location_src_id": self.env.ref('stock.stock_location_suppliers').id,
            "location_dest_id": self.env.ref('stock.stock_location_stock').id,
            "picking_type_id": self.env.ref('stock.picking_type_in').id,
            "route_id": route.id,
            "action": "buy",
            "procure_method": "make_to_order",
        })

        self.env["stock.rule"].create({
            "name": "Internal to Transit",
            "location_src_id": self.env.ref('stock.stock_location_stock').id,
            "location_dest_id": transit_location.id,
            "picking_type_id": stock_picking_transit_type.id,
            "route_id": route.id,
            "action": "pull_push",
            "procure_method": "mts_else_mto",
        })

        self.env["stock.rule"].create({
            "name": "Transit to Customers",
            "location_src_id": transit_location.id,
            "location_dest_id": self.env.ref('stock.stock_location_customers').id,
            "picking_type_id": stock_picking_customers_type.id,
            "route_id": route.id,
            "action": "pull_push",
            "procure_method": "mts_else_mto",
        })

        self.env["stock.rule"].create({
            "name": "Transit to Internal",
            "location_src_id": transit_location.id,
            "location_dest_id": self.env.ref('stock.stock_location_stock').id,
            "picking_type_id": stock_picking_transit_type.id,
            "route_id": route.id,
            "action": "pull_push",
            "procure_method": "mts_else_mto",
        })

        return route

    def _create_stock_picking_transit_type(self, transit_location):
        return self.env["stock.picking.type"].create(
            {"name": "Test picking type transit", "default_location_src_id": self.env.ref('stock.stock_location_stock').id,
             "default_location_dest_id": transit_location.id, "sequence_code": "TST",
             "reservation_method": "at_confirm", "company_id": self.env.company.id,
             "code": "internal", "create_backorder": "always", "show_operations": False}
        )

    def _create_stock_picking_customers_type(self, transit_location):
        customers_location = self.env.ref('stock.stock_location_customers')
        return self.env["stock.picking.type"].create(
            {"name": "Test picking type customers", "default_location_src_id": transit_location.id,
             "default_location_dest_id": customers_location.id, "sequence_code": "TSC",
             "reservation_method": "at_confirm", "company_id": self.env.company.id,
             "code": "internal", "create_backorder": "always", "show_operations": False
             }
        )

    def _create_order(self, customer, product):
        return self.env["sale.order"].create(
            {"partner_id": customer.id, "order_line": [(0, 0, {"product_id": product.id})]}
        )

    def _create_product(self, customer, route):
        product = self.env["product.product"].create(
            {"name": "Test product", "type": "product", "seller_ids": [(0, 0, {"partner_id": customer.id})],
             "detailed_type": "product", "purchase_ok": True}
        )
        product.write({'route_ids': [(4, route.id)]})
        print(f"Product created: {product.name} (ID: {product.id}) with route: {route.name} (ID: {route.id})")
        return product

    def _create_stock_picking_modality(self, name, line_qty):
        return self.env['stock.picking.modality'].create({
            'name': name,
            'line_qty': line_qty,
        })

    def _create_stock_picking_destiny(self, name):
        return self.env['stock.picking.destiny'].create({
            'name': name,
        })

    def _create_stock_picking_zone(self, name, destiny_id):
        return self.env['stock.picking.zone'].create({
            'name': name,
            'destiny_id': destiny_id.id,
        })

    def _create_stock_picking_modality_destiny_price(self, modality_id, destiny_id, zone_id, price):
        return self.env['stock.picking.modality.destiny.price'].create({
            'modality_id': modality_id.id,
            'destiny_id': destiny_id.id,
            'zone_id': zone_id.id,
            'price': price,
        })

    def _create_order_with_line(self, customer, product, route, modality, destiny, zone, quantity, fee):

        # product.write({'route_ids': [(4, route.id)]})

        return self.env['sale.order'].create({
            'partner_id': customer.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'route_id': route.id,
                'modality_id': modality.id,
                'destiny_id': destiny.id,
                'zone_id': zone.id,
                'product_uom_qty': quantity,
                'price_unit': fee.price,
            })]
        })

    def _confirm_purchase_order(self, order):
        purchase_order = self.env['purchase.order'].search([
            ('origin', '=', order.name),
        ], limit=1)
        print(f"Purchase order created: {purchase_order.name} (ID: {purchase_order.id})")

        purchase_order.button_confirm()
        print(f"Purchase order confirmed: {purchase_order.name} (ID: {purchase_order.id})")

        picking = purchase_order.picking_ids
        print(f"Picking created: {picking.name} (ID: {picking.id})")

        # Link the picking to the sale order
        picking.write({'sale_id': order.id})

        picking.action_confirm()
        print(f"Picking confirmed: {picking.name} (ID: {picking.id})")
        picking.action_assign()
        print(f"Picking assigned: {picking.name} (ID: {picking.id})")

        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
            print(f"Move {move.id} quantity done set to {move.quantity_done}")

        picking.button_validate()
        print(f"Picking validated: {picking.name} (ID: {picking.id})")

    def _confirm_partial_purchase_order(self, order, partial_quantity, remaining_quantity):
        purchase_order = self.env['purchase.order'].search([
            ('origin', '=', order.name),
        ], limit=1)
        print(f"Purchase order created: {purchase_order.name} (ID: {purchase_order.id})")

        purchase_order.button_confirm()
        print(f"Purchase order confirmed: {purchase_order.name} (ID: {purchase_order.id})")

        picking = purchase_order.picking_ids
        print(f"Picking created: {picking.name} (ID: {picking.id})")

        picking.write({'sale_id': order.id})


        picking.action_confirm()
        print(f"Picking confirmed: {picking.name} (ID: {picking.id})")
        picking.action_assign()
        print(f"Picking assigned: {picking.name} (ID: {picking.id})")

        # Validate partial quantity
        for move in picking.move_ids_without_package:
            move._set_quantity_done(partial_quantity)
            # move.quantity_done = partial_quantity
            print(f"Move {move.id} partial quantity done set to {move.quantity_done}")

        # picking.button_validate()

        backorder_wizard_dict = picking.button_validate()
        backorder_wiz = Form(
            self.env[backorder_wizard_dict["res_model"]].with_context(
                **backorder_wizard_dict["context"]
            )
        ).save()
        backorder_wiz.process()

        print(f"Picking validated: {picking.name} (ID: {picking.id})")
        # partial_picking_wizard = self.env['stock.backorder.confirmation'].create({
        #     'pick_ids': [(4, picking.id)]
        # })
        # partial_picking_wizard.process()
        # print(f"Partial picking processed: {picking.name} (ID: {picking.id})")

        print(f"Picking Details: ID: {picking.id}, Name: {picking.name}, State: {picking.state}")
        for move in picking.move_ids_without_package:
            print(
                f"Move ID: {move.id}, Product: {move.product_id.name}, Quantity Done: {move.quantity_done}, State: {move.state}")

        for line in order.order_line:
            line._compute_state_planning()
            self.assertEqual(line.state_planning, "en_stock_parcial")
            print(f"Sale Order Line ID: {line.id} is in 'en_stock_parcial' state as expected.")

        new_picking = self.env['stock.picking'].search([
            ('origin', '=', purchase_order.name),
            ('state', '=', 'assigned')
        ], limit=1)

        if new_picking:
            new_picking.action_confirm()
            new_picking.action_assign()
            print(f"New picking created: {new_picking.name} (ID: {new_picking.id})")

            for move in new_picking.move_ids_without_package:
                move._set_quantity_done(remaining_quantity)
                print(f"Move {move.id} remaining quantity done set to {move.quantity_done}")

            new_picking.button_validate()

            # immediate_wizard = new_picking.button_validate()
            # print("*"*80, immediate_wizard)
            # immediate_wizard_form = Form(
            #     self.env[immediate_wizard["res_model"]].with_context(
            #         **immediate_wizard["context"]
            #     )
            # ).save()
            # immediate_wizard_form.process()

            print(f"Picking validated: {new_picking.name} (ID: {new_picking.id})")

            for line in order.order_line:
                line._compute_state_planning()
                self.assertEqual(line.state_planning, "en_stock")
                print(f"Sale Order Line ID: {line.id} is in 'en_stock' state as expected.")
        else:
            raise ValueError("No new picking found for the remaining quantity.")

    def _confirm_assigned_picking(self, order):
        pickings = self.env['stock.picking'].search([('origin', '=', order.name)])
        print(f"All pickings related to order {order.name}: {[picking.id for picking in pickings]}")
        for picking in pickings:
            print(f"Picking ID: {picking.id}")
            print(f"Picking Name: {picking.name}")
            print(f"Picking State: {picking.state}")
            print(f"Picking Origin: {picking.origin}")
            print(f"Picking Partner: {picking.partner_id.name}")
        picking = order.picking_ids.filtered(lambda p: p.state == 'assigned')
        if not picking:
            raise ValueError("No assigned picking found for the order.")

        picking.action_confirm()

        # Ensure there are move lines to assign
        if not picking.move_ids_without_package:
            raise ValueError("Nothing to check the availability for.")

        picking.action_assign()
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()

    def test_planning_state(self):
        customer = self._create_customer()
        print(f"Customer created: {customer.name} (ID: {customer.id})")

        warehouse = self._create_warehouse()
        print(f"Warehouse created: {warehouse.name} (ID: {warehouse.id})")

        transit_location = self._create_transit_location(warehouse)
        print(f"Transit location created: {transit_location.name} (ID: {transit_location.id})")

        stock_picking_transit_type = self._create_stock_picking_transit_type(transit_location)
        print(
            f"Stock picking transit type created: {stock_picking_transit_type.name} (ID: {stock_picking_transit_type.id})")

        stock_picking_customers_type = self._create_stock_picking_customers_type(transit_location)
        print(
            f"Stock picking customers type created: {stock_picking_customers_type.name} (ID: {stock_picking_customers_type.id})")

        route = self._create_route(transit_location, stock_picking_transit_type,
                                   stock_picking_customers_type)
        print(f"Route created: {route.name} (ID: {route.id})")

        product = self._create_product(customer, route)
        print(f"Product created: {product.name} (ID: {product.id})")

        modality = self._create_stock_picking_modality('Test modality', 1)
        print(f"Modality created: {modality.name} (ID: {modality.id})")

        destiny = self._create_stock_picking_destiny('Test destiny')
        print(f"Destiny created: {destiny.name} (ID: {destiny.id})")

        zone = self._create_stock_picking_zone('Test zone', destiny)
        print(f"Zone created: {zone.name} (ID: {zone.id})")

        fee = self._create_stock_picking_modality_destiny_price(modality, destiny, zone, 10)
        print(f"Fee created: {fee.name} (ID: {fee.id}) - Price: {fee.price}")

        order = self._create_order_with_line(customer, product, route, modality, destiny, zone, 33, fee)
        print(f"Order created: {order.name} (ID: {order.id})")

        order.action_confirm()
        print(f"Order confirmed: {order.name} (ID: {order.id})")

        for line in order.order_line:
            self.assertEqual(line.state_planning, "espera_recepcion")
            print(f"Sale Order Line ID: {line.id} is in 'espera_recepcion' state as expected.")

        self._confirm_purchase_order(order)
        print(f"Purchase order created and confirmed for order: {order.name} (ID: {order.id})")

        for line in order.order_line:
            self.assertEqual(line.state_planning, "en_stock")
            print(f"Sale Order Line ID: {line.id} is in 'en_stock' state as expected.")

        self._confirm_assigned_picking(order)
        print(f"First assigned picking confirmed for order: {order.name} (ID: {order.id})")

        for line in order.order_line:
            self.assertEqual(line.state_planning, "en_furgon")
            print(f"Sale Order Line ID: {line.id} is in 'en_furgon' state as expected.")

        self._confirm_assigned_picking(order)
        print(f"Second assigned picking confirmed for order: {order.name} (ID: {order.id})")

        for line in order.order_line:
            self.assertEqual(line.state_planning, "repartido")
            print(f"Sale Order Line ID: {line.id} is in 'repartido' state as expected.")

        pickings = self.env['stock.picking'].search([('origin', '=', order.name)])
        print(f"All pickings related to order {order.name}: {[picking.id for picking in pickings]}")
        for picking in pickings:
            print(f"Picking ID: {picking.id}")
            print(f"Picking Name: {picking.name}")
            print(f"Picking State: {picking.state}")
            print(f"Picking Origin: {picking.origin}")
            print(f"Picking Partner: {picking.partner_id.name}")

    def test_partial_delivery_to_customer(self):
        customer = self._create_customer()
        print(f"Customer created: {customer.name} (ID: {customer.id})")

        warehouse = self._create_warehouse()
        print(f"Warehouse created: {warehouse.name} (ID: {warehouse.id})")

        transit_location = self._create_transit_location(warehouse)
        print(f"Transit location created: {transit_location.name} (ID: {transit_location.id})")

        stock_picking_transit_type = self._create_stock_picking_transit_type(transit_location)
        print(
            f"Stock picking transit type created: {stock_picking_transit_type.name} (ID: {stock_picking_transit_type.id})")

        stock_picking_customers_type = self._create_stock_picking_customers_type(transit_location)
        print(
            f"Stock picking customers type created: {stock_picking_customers_type.name} (ID: {stock_picking_customers_type.id})")

        route = self._create_route(transit_location, stock_picking_transit_type, stock_picking_customers_type)
        print(f"Route created: {route.name} (ID: {route.id})")

        product = self._create_product(customer, route)
        print(f"Product created: {product.name} (ID: {product.id})")

        modality = self._create_stock_picking_modality('Test modality', 1)
        print(f"Modality created: {modality.name} (ID: {modality.id})")

        destiny = self._create_stock_picking_destiny('Test destiny')
        print(f"Destiny created: {destiny.name} (ID: {destiny.id})")

        zone = self._create_stock_picking_zone('Test zone', destiny)
        print(f"Zone created: {zone.name} (ID: {zone.id})")

        fee = self._create_stock_picking_modality_destiny_price(modality, destiny, zone, 10)
        print(f"Fee created: {fee.name} (ID: {fee.id}) - Price: {fee.price}")

        order = self._create_order_with_line(customer, product, route, modality, destiny, zone, 33, fee)
        print(f"Order created: {order.name} (ID: {order.id})")

        order.action_confirm()
        print(f"Order confirmed: {order.name} (ID: {order.id})")

        for line in order.order_line:
            assert line.state_planning == 'espera_recepcion', f"Expected 'espera_recepcion', got {line.state_planning}"
            print(f"Sale Order Line ID: {line.id} is in 'espera_recepcion' state as expected.")

        self._confirm_purchase_order(order)
        print(f"Purchase order created and confirmed for order: {order.name} (ID: {order.id})")

        for line in order.order_line:
            assert line.state_planning == 'en_stock', f"Expected 'en_stock', got {line.state_planning}"
            print(f"Sale Order Line ID: {line.id} is in 'en_stock' state as expected.")

        self._confirm_assigned_picking(order)
        print(f"First assigned picking confirmed for order: {order.name} (ID: {order.id})")

        for line in order.order_line:
            assert line.state_planning == 'en_furgon', f"Expected 'en_furgon', got {line.state_planning}"
            print(f"Sale Order Line ID: {line.id} is in 'en_furgon' state as expected.")

        print("*"*80,"Wizard a continuación")
        new_route = self._create_route_with_last_two_rules(transit_location, stock_picking_transit_type,
                                                           stock_picking_customers_type)

        wizard = self.env['partial.delivery.wizard'].create({
            'cantidad_entregada': 16.5,
            'sale_order_line_id': order.order_line.id,
            'route_id': new_route.id,
            'modality_id': modality.id,
            'destiny_id': destiny.id,
            'zone_id': zone.id,
        })
        wizard.action_confirm_partial_delivery()

        for line in order.order_line:
            assert line.state_planning == 'repartido', f"Expected 'repartido', got {line.state_planning}"
            print("*"*20, "Order anterior")
            print(f"Sale Order Line ID: {line.id} is in 'repartido' state as expected.")

        new_order = self.env['sale.order'].search([
            ('order_line.product_uom_qty', '=', 16.5),
            ('order_line.route_id', '=', new_route.id),
            ('order_line.modality_id', '=', modality.id),
            ('order_line.destiny_id', '=', destiny.id),
            ('order_line.zone_id', '=', zone.id),
        ], limit=1)

        if new_order:
            print(f"New Order: {new_order.name} (ID: {new_order.id})")
            print(f"Customer: {new_order.partner_id.name} (ID: {new_order.partner_id.id})")
            print(f"Order Date: {new_order.date_order}")
            print(f"Order State: {new_order.state}")
            for line in new_order.order_line:
                print(f"Order Line ID: {line.id}")
                print(f"Product: {line.product_id.name} (ID: {line.product_id.id})")
                print(f"Quantity: {line.product_uom_qty}")
                print(f"Price Unit: {line.price_unit}")
                print(f"State Planning: {line.state_planning}")
                print(f"Route: {line.route_id.name} (ID: {line.route_id.id})")
                print(f"Modality: {line.modality_id.name} (ID: {line.modality_id.id})")
                print(f"Destiny: {line.destiny_id.name} (ID: {line.destiny_id.id})")
                print(f"Zone: {line.zone_id.name} (ID: {line.zone_id.id})")
            for line in new_order.order_line:
                assert line.state_planning == 'en_stock', f"Expected 'en_stock', got {line.state_planning}"
                print(f"Sale Order Line ID: {line.id} is in 'en_stock' state as expected.")

            self._confirm_assigned_picking(new_order)
            print(f"Assigned picking confirmed for order created with wizard: {new_order.name} (ID: {new_order.id})")

            for line in new_order.order_line:
                assert line.state_planning == 'en_furgon', f"Expected 'en_furgon', got {line.state_planning}"
                print(f"Sale Order Line ID: {line.id} is in 'en_furgon' state as expected.")

            self._confirm_assigned_picking(new_order)
            print(f"Assigned picking confirmed for order created with wizard: {new_order.name} (ID: {new_order.id})")

            for line in new_order.order_line:
                assert line.state_planning == 'repartido', f"Expected 'repartido', got {line.state_planning}"
                print(f"Sale Order Line ID: {line.id} is in 'repartido' state as expected.")
        else:
            print("No new order found.")

    def test_partial_receipt(self):
        customer = self._create_customer()
        print(f"Customer created: {customer.name} (ID: {customer.id})")

        warehouse = self._create_warehouse()
        print(f"Warehouse created: {warehouse.name} (ID: {warehouse.id})")

        transit_location = self._create_transit_location(warehouse)
        print(f"Transit location created: {transit_location.name} (ID: {transit_location.id})")

        stock_picking_transit_type = self._create_stock_picking_transit_type(transit_location)
        print(
            f"Stock picking transit type created: {stock_picking_transit_type.name} (ID: {stock_picking_transit_type.id})")

        stock_picking_customers_type = self._create_stock_picking_customers_type(transit_location)
        print(
            f"Stock picking customers type created: {stock_picking_customers_type.name} (ID: {stock_picking_customers_type.id})")

        route = self._create_route_with_inverse(transit_location, stock_picking_transit_type, stock_picking_customers_type)
        print(f"Route created: {route.name} (ID: {route.id})")

        product = self._create_product(customer, route)
        print(f"Product created: {product.name} (ID: {product.id})")

        modality = self._create_stock_picking_modality('Test modality', 1)
        print(f"Modality created: {modality.name} (ID: {modality.id})")

        destiny = self._create_stock_picking_destiny('Test destiny')
        print(f"Destiny created: {destiny.name} (ID: {destiny.id})")

        zone = self._create_stock_picking_zone('Test zone', destiny)
        print(f"Zone created: {zone.name} (ID: {zone.id})")

        fee = self._create_stock_picking_modality_destiny_price(modality, destiny, zone, 10)
        print(f"Fee created: {fee.name} (ID: {fee.id}) - Price: {fee.price}")

        order = self._create_order_with_line(customer, product, route, modality, destiny, zone, 33, fee)
        print(f"Order created: {order.name} (ID: {order.id})")

        order.action_confirm()
        print(f"Order confirmed: {order.name} (ID: {order.id})")

        for line in order.order_line:
            self.assertEqual(line.state_planning, "espera_recepcion")
            print(f"Sale Order Line ID: {line.id} is in 'espera_recepcion' state as expected.")

            # Confirm purchase order and receive partial quantity
        self._confirm_partial_purchase_order(order, partial_quantity=16, remaining_quantity=17)
        print(f"Purchase order created and confirmed for order: {order.name} (ID: {order.id})")

