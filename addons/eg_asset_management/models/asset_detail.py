from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import UserError


class AssetDetail(models.Model):
    _name = "asset.detail"
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin', 'resource.mixin',
                'avatar.mixin']
    _mail_post_access = 'read'
    _description = "Asset Detail"

    name = fields.Char(string="Name")
    file_data = fields.Binary(string="Attachment")
    file_name = fields.Char(string="File Name")
    category_id = fields.Many2one(comodel_name="asset.category", string="Category", tracking=True)
    asset_code = fields.Char(string="Asset Code")
    asset_model = fields.Char(string="Asset Model", tracking=True)
    asset_brand = fields.Char(string="Asset Brand", tracking=True)
    serial_no = fields.Char(string="Serial No.", tracking=True)
    purchase_date = fields.Date(string="Purchase Date", tracking=True)
    purchase_value = fields.Float(string="Purchase Value", tracking=True)
    location_id = fields.Many2one(comodel_name="asset.location", string="Current Location", tracking=True)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", tracking=True)
    vendor_id = fields.Many2one(comodel_name="res.partner", string="Vendor")
    warranty_start = fields.Date(string="Warranty Start", tracking=True)
    warranty_end = fields.Date(string="Warranty End", tracking=True)
    note = fields.Html(string="Note")
    state = fields.Selection([('draft', 'New'), ('release', 'Release'), ('active', 'Assigned'), ('scrap', 'Scrap')],
                             string='State', default="draft")
    history_ids = fields.One2many('asset.history', 'asset_id', string="Asset History")
    spec_ids = fields.One2many('asset.specification', 'asset_id', string="Asset Configuration")
    date_from = fields.Datetime(string="From", tracking=True)
    date_till = fields.Datetime(string="To", tracking=True)
    reassigned = fields.Boolean(string="Reassigned", default="false")

    @api.model
    def create(self, vals):
        location_id = self.env["asset.location"].search([("is_default", "=", True)], limit=1)
        # vals["asset_code"] = self.env["ir.sequence"].next_by_code("asset.detail",
        #                                                           sequence_date=datetime.now().year) or "New"
        if location_id:
            vals["location_id"] = location_id.id
        res = super(AssetDetail, self).create(vals)
        code = self.env["ir.sequence"].next_by_code("asset.detail", sequence_date=datetime.now().year) or "New"
        loc_code = ''
        cat_code = ''
        if res:
            if res.location_id:
                loc_code = res.location_id.location_code
            if res.category_id:
                cat_code = res.category_id.short_code
        asset_code = 'TW/' + loc_code + '/' + cat_code + '/' + code
        print("asset_code", asset_code)
        res.write({
            'asset_code': asset_code
        })
        return res

    def scrap_asset(self):
        for asset_id in self:
            location_id = self.env["asset.location"].search([("is_scrap", "=", True)], limit=1)
            if location_id:
                asset_id.state = "scrap"
                if not asset_id.date_till:
                    raise UserError("Please add an end date to release this asset.")
                asset_id.state = "release"
                prev_emp = asset_id.employee_id
                prev_date_from = asset_id.date_from
                prev_date_till = asset_id.date_till
                asset_id.write({
                    'history_ids': [(0, 0, {
                        'employee_id': prev_emp.id,
                        'date_from': prev_date_from,
                        'date_till': prev_date_till,
                        'asset_id': asset_id.id,
                    })]
                })
                asset_id.employee_id = None
                asset_id.date_from = None
                asset_id.date_till = None

    def confirm_asset(self):
        for asset_id in self:
            if not asset_id.employee_id:
                raise UserError("Please add an employee before confirming the asset")
            if not asset_id.date_from:
                raise UserError("Please add From Date before confirming the asset")
            asset_id.state = "active"

    def release_asset(self):
        for asset_id in self:
            if not asset_id.date_till:
                raise UserError("Please add an end date to release this asset.")
            asset_id.state = "release"
            prev_emp = asset_id.employee_id
            prev_date_from = asset_id.date_from
            prev_date_till = asset_id.date_till
            asset_id.write({
                'history_ids': [(0, 0, {
                    'employee_id': prev_emp.id,
                    'date_from': prev_date_from,
                    'date_till': prev_date_till,
                    'asset_id': asset_id.id,
                })]
            })
            asset_id.employee_id = None
            asset_id.date_from = None
            asset_id.date_till = None
