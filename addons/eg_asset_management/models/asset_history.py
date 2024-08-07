from odoo import fields, models, api
from odoo.exceptions import UserError

class AssetHistory(models.Model):
    _name = 'asset.history'

    asset_id = fields.Many2one('asset.detail', string=" Asset")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    date_from = fields.Datetime(string="From")
    date_till = fields.Datetime(string="To")
    note = fields.Text(string="Note")

    @api.model
    def unlink(self):
        # Raise an exception if a delete attempt is made
        raise UserError("You are not allowed to delete records in the Asset History model.")