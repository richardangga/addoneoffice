from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
import time
import logging

_logger = logging.getLogger(__name__)
DOC_STATES = [('draft','Draft'),('open','Need Approval'),('unread','Unread'),('read','Read')]

class officedocument(models.Model):
    _name = 'office.officedocument'
    _description = 'Surat'

    name = fields.Char(string='Nomor', readonly=True)
    perihal_id = fields.Char(string='Perihal',required=True,readonly=True,states={'draft': [('readonly', False)]} )
    isisurat_id = fields.Text(string="Isi Surat",required=True,readonly=True,compute='_automate',states={'draft': [('readonly', False)]})
    
    @api.depends('isisurat_id','template_id')
    def _automate(self):
        for record in self:
            self.isisurat_id = record.template_id.isisurat_id
    
    @api.onchange('isisurat_id','template_id')
    def onchange_template_id(self):
        self.isisurat_id = self.template_id.isisurat_id
    
    dari_id = fields.Many2one(string='Dari',comodel_name='res.users',required=True,readonly=True,states={'draft': [('readonly',False)]}) 
    kepada_id = fields.Many2one(string='Kepada',comodel_name='office.to_user',ondelete='cascade',inverse_name='doc_id',required=True,readonly=True,states={'draft': [('readonly',False)]})
    tembusan_id = fields.Many2one(string='Tembusan',comodel_name='office.cc_user',inverse_name='doc_id',ondelete='cascade',required=True,readonly=True,states={'draft': [('readonly', False)]})
    tanggal_id = fields.Date(string='Tanggal',default= lambda self : time.strftime("%Y-%m-%d"),required=True,readonly=True,states={'draft': [('readonly',False)]})
    klasifikasi_id = fields.Many2one(string="Klasifikasi",comodel_name='office.doc_type',required=True,readonly=True, states={'draft': [('readonly', False)]})
    template_id = fields.Many2one(string="Template Surat",comodel_name='office.doc_template',required=True,readonly=True, states={'draft': [('readonly', False)]})
    status_id = fields.Boolean(string="Read",readonly=True)
    state = fields.Selection(string="State",selection=DOC_STATES,required=True,readonly=True,default=DOC_STATES[0][0])
    history_id = fields.One2many(string="History",comodel_name='office.doc_history',inverse_name='doc_id',ondelete='cascade',readonly=True)
    sumbersurat_id = fields.Many2one(string="Sumber Surat",comodel_name='office.officedocument')
    
    @api.model
    def create(self,vals):
        if not vals.get('name',False) or vals['name'] == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('office.officedocument') or 'Error Number'
        return super(officedocument,self).create(vals)
    
    @api.multi
    def action_draft(self):
        self.state = DOC_STATES[0][0]
    @api.multi
    def action_open(self):
        self.state = DOC_STATES[1][0]
    @api.multi
    def action_send(self):
        self.state = DOC_STATES[2][0]
    @api.multi
    def action_read(self):
        self.state = DOC_STATES[3][0]
    # @api.multi
    # def action_reply(self):
    #     '''
    #     redirect to office.officedocument form view with prefilled values
    #     from the old document
	# 	'''
    #     data = self.browse(cr, uid, ids, [])[0]
    #     context.update({
    #         'default_parent_id' : data.id,
    #         'default_user_id' : uid,
    #         'default_to_user_ids' : [(0,0,{'user_id':data.user_id.id})]
    #     })
    #     self.insert_history(cr, uid, ids[0], 'Replied')
    #     return {
    #         'name': _('Reply Surat'),
    #         'view_type': 'form',
    #         "view_mode": 'form',
    #         'res_model': 'office.officedocument',
    #         'type': 'ir.actions.act_window',
    #         'context': context,
    #     }
    # @api.multi
    # def action_forward(self):
    #     '''
    #     redirect to office.officedocument form view with prefilled values from the old doc
    #     '''
    #     data = self.browse(cr,uid,ids,[])[0]
	# 	context.update({
    #         'default_parent_id' : data.id,
    #         'default_user_id' : uid,
    #     })
	# 	self.insert_history(cr, uid, ids[0], 'Forwarded')
	# 	return {
	# 		'name': _('Reply Surat'),
	# 		'view_type': 'form',
	# 		"view_mode": 'form',
	# 		'res_model': 'office.officedocument',
	# 		'type': 'ir.actions.act_window',
	# 		'context': context,
	# 	}
	# 	return
class to_user(models.Model):
    _name = 'office.to_user'
    
    user_id = fields.Many2one(string="User",comodel_name='res.users')
    doc_id = fields.Many2one(string="Surat",comodel_name='office.officedocument')
    read_status = fields.Boolean(string="Read")
    
class cc_user(models.Model):
    _name = 'office.cc_user'

    user_id = fields.Many2one(string="User",comodel_name='res.users')
    doc_id = fields.Many2one(string="Surat",comodel_name='office.officedocument')
    read_status = fields.Boolean(string="Read")
    
class doc_template(models.Model):
    _name = 'office.doc_template'
    
    code = fields.Char(string="Code",required=True)
    name = fields.Char(string="Name",required=True)
    isisurat_id = fields.Text(string="Body",required=True)

class doc_type(models.Model):
    _name = 'office.doc_type'
    
    code = fields.Char(string="Code",required=True)
    name = fields.Char(string="Name",required=True)

class doc_history(models.Model):
    _name = 'office.doc_history'
    
    name = fields.Char(string="History")
    user_id = fields.Many2one(string="By",comodel_name='res.users')
    doc_id = fields.Many2one(string="Surat",comodel_name='office.officedocument')