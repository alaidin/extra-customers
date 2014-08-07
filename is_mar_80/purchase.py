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

from openerp import fields, models, api, _
import openerp.addons.decimal_precision as dp

class collection(models.Model):
    _name = "collection.collection"
    _description = "Collection object"
    _inherit = ['mail.thread']
    
    name = fields.Char("Name", size=128, required=True)
    quantity = fields.Float("Quantity", digits_compute=dp.get_precision("Product Unit of Measure"), required=True, default=1)
    date_receipt = fields.Datetime("Date")
    duration = fields.Integer("Duration")
    state = fields.Selection([
                              ('draft', 'New'),
                              ('full', 'Full'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')
                              ],'Status', required=True, copy=False, default='draft')
    
    #_group_by_full = {'state' : (['draft','full','cancel','done'],{})
    #                  }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: