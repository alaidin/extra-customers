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

class stock_move(models.Model):
    _inherit = "stock.move"
    
    @api.model
    def _create_operation_link(self, move, operation, operation_link):
        lot = move.restrict_lot_id
        partner = move.restrict_partner_id
        
        print move.product_qty, operation.product_qty
        
        if move.product_qty == operation.product_qty:
            operation.write({
                             'owner_id': partner.id,
                             'lot_id': lot.id,
                             })        
        elif move.product_qty < operation.product_qty:
            values = {
                     'product_qty': move.product_qty,
                     'lot_id': lot.id,
                     'owner_id': partner.id,
                     'processed': False,
                     'qty_done': 0,
                     }
            new_operation = operation.copy(values)
#             operation.product_qty -= move.product_qty #A TESTER
            operation.product_qty = operation.product_qty - move.product_qty
            
            operation_link.operation_id = new_operation.id
            
    
    @api.one
    def split_operation_serial(self):
        if self.restrict_lot_id or self.restrict_partner_id:
            for op_link in self.linked_move_operation_ids:
                operation = op_link.operation_id 
                
                print operation.lot_id , self.restrict_lot_id , opeartion.owner_id , self.restrict_partner_id
                
                if operation.lot_id != self.restrict_lot_id or opeartion.owner_id != self.restrict_partner_id:
                    self._create_operation_link(self, operation, op_link)
                    
            
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
