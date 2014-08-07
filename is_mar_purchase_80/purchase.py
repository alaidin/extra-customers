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

class purchase_order(models.Model):
    _inherit = "purchase.order"
    
    is_direct_receipt = fields.Boolean(string = "Automatic picking", default = True)
    total_quantity = fields.Float('Total quantity', digits_compute=dp.get_precision('Product Unit of Measure'),
                                  compute="_get_total_quantity", store=True)
    
    @api.onchange('is_direct_receipt')
    def _onchange_direct_receipt(self):
        if not self.is_direct_receipt: 
            for line in self.order_line:
                line.partner_dest_id = False
    
    @api.one
    @api.depends(
                 'order_line.product_qty')
    def _get_total_quantity(self):
        self.total_quantity = sum((line.product_qty for line in self.order_line), 0.0)
    
    @api.model
    def _prepare_order_line_move(self, order, order_line, picking_id, group_id):
        res = super(purchase_order, self)._prepare_order_line_move(order, order_line, picking_id, group_id)
        
        obj_order_line = self.env['purchase.order.line']
        
        for vals in res:
            if vals.get('purchase_line_id'):
                line = obj_order_line.browse(vals['purchase_line_id'])
                if line.partner_dest_id:
                    vals.update({
                                  'partner_id': line.partner_dest_id.id,
                                  })

        return res
    
    @api.multi
    def action_picking_create(self):
        super(purchase_order,self).action_picking_create()
        
        for order in self:
            if order.is_direct_receipt:
                pickings = order.picking_ids.filtered(lambda p: p.state == 'assigned')
                
                if pickings:
                    pickings.do_transfer()

class purchase_order_line(models.Model):
    _inherit = "purchase.order.line"

    partner_dest_id = fields.Many2one("res.partner","Destination",readonly=True,states={'draft':[('readonly',False)]})
    
    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        if self.product_qty <0:
            raise exceptions.Warning(_('Quantity must be > 0'))
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
