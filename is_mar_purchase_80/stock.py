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

class stock_picking(models.Model):
    _inherit = "stock.picking"
    
    driver_id = fields.Many2one('hr.employee', "Driver")

class stock_move(models.Model):
    _inherit = 'stock.move'
    
    supplier_id = fields.Many2one("res.partner", "Supplier from", read_only=True)
    
    @api.one
    def copy(default=None):
        default = default or {}
        if not default.get('split_from'):
            #we don't want to propagate the link to the purchase order line except in case of move split
            default['supplier_id'] = False
            
        return super(stock_move, self).copy(default)

class stock_quant(models.Model):
    _inherit = 'stock.quant'
    
    supplier_id = fields._Relational()
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
