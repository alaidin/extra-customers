# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models, api, _, exceptions
import openerp.addons.decimal_precision as dp

class collection_create(models.TransientModel):
    _name = "collection.create"
    _description = "Transient collection creation"
    
    driver_id = fields.Many2one("hr.employee","Driver")
    date_expected = fields.Datetime("Date expected")
    name = fields.Char("Name", size=128)
    
    @api.model
    def _prepare_lines_move(self, wizard, quant, picking, group):
        ''' prepare the stock move data from the PO line. This function returns a list of dictionary ready to be used in stock.move's create()'''
#         product_uom = self.env['product.uom']
        
#         price_unit = order_line.price_unit
        price_unit = 1
#         if order_line.product_uom.id != order_line.product_id.uom_id.id:
#             price_unit *= order_line.product_uom.factor
#         if order.currency_id.id != order.company_id.currency_id.id:
#             #we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
#             price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id, order.company_id.currency_id.id, price_unit, round=False, context=context)
#         res = []
        
        
        move_template = {
            'name': quant.product_id.display_name,
            'product_id': quant.product_id.id,
            'product_uom': quant.product_id.uom_id.id,
            'product_uos': quant.product_id.uom_id.id,
            'product_uom_qty': quant.qty,
            'product_uos_qty': quant.qty,
            'date': fields.Datetime.now(),
            'date_expected': wizard.date_expected,
            'location_id': quant.location_id.id,
            'location_dest_id': picking.picking_type_id.default_location_dest_id.id,
            'picking_id': picking.id,
            'partner_id': quant.owner_id and quant.owner_id.id or False,
            'restrict_partner_id': quant.owner_id and quant.owner_id.id or False,
            'restrict_lot_id': quant.lot_id and quant.lot_id.id or False,
            'move_dest_id': False,
            'state': 'draft',
            'company_id': quant.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': picking.picking_type_id.id,
            'group_id': group.id,
            'procurement_id': False,
            'origin': wizard.name or '',
            'route_ids': picking.picking_type_id.warehouse_id and [(6, 0, [x.id for x in picking.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id':picking.picking_type_id.warehouse_id.id,
            'invoice_state': 'none'
        }

#         diff_quantity = order_line.product_qty
#         for procurement in order_line.procurement_ids:
#             procurement_qty = product_uom._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=order_line.product_uom.id)
#             tmp = move_template.copy()
#             tmp.update({
#                 'product_uom_qty': min(procurement_qty, diff_quantity),
#                 'product_uos_qty': min(procurement_qty, diff_quantity),
#                 'move_dest_id': procurement.move_dest_id.id,  #move destination is same as procurement destination
#                 'group_id': procurement.group_id.id or group_id,  #move group is same as group of procurements if it exists, otherwise take another group
#                 'procurement_id': procurement.id,
#                 'invoice_state': procurement.rule_id.invoice_state or (procurement.location_id and procurement.location_id.usage == 'customer' and procurement.invoice_state) or (order.invoice_method == 'picking' and '2binvoiced') or 'none', #dropship case takes from sale
#             })
#             diff_quantity -= min(procurement_qty, diff_quantity)
#             res.append(tmp)
#         #if the order line has a bigger quantity than the procurement it was for (manually changed or minimal quantity), then
#         #split the future stock move in two because the route followed may be different.
#         if diff_quantity > 0:
#             move_template['product_uom_qty'] = diff_quantity
#             move_template['product_uos_qty'] = diff_quantity
#             res.append(move_template)
        return move_template
    
    @api.model
    def _create_stock_moves(self, wizard, quants, picking=False):
        obj_stock_move = self.env['stock.move']
        todo_moves = self.env['stock.move']
        obj_group = self.env["procurement.group"]
        
        new_group = obj_group.create({'name': picking and picking.name or '/'})

        for quant in quants:
            vals = self._prepare_lines_move(wizard, quant, picking, new_group)
            move = obj_stock_move.create(vals)
            todo_moves += move

        todo_moves.action_confirm()
        todo_moves.action_assign()
        todo_moves.split_operation_serial()
    
    @api.one
    def collection_creation(self):
        driver_id = self.driver_id
        quant_ids = self._context.get("active_ids", [])
        
        if quant_ids:
            obj_stock_picking = self.env['stock.picking']
            picking_type = self.env.ref('is_mar_purchase_80.picking_type_collection', False)
            
            if not picking_type:
                raise exceptions.MissingError(_('Picking type collection has been deleted'))
            
            picking = obj_stock_picking.create({'picking_type_id':picking_type.id})
            
            obj_quant = self.env['stock.quant']
            quants = obj_quant.browse(quant_ids)
            
            self._create_stock_moves(self, quants, picking)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
