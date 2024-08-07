from odoo import fields, models, api


class AssetSpecification(models.Model):
    _name = 'asset.specification'
    _description = 'Asset Specification'

    asset_id = fields.Many2one('asset.detail', string=" Asset")
    name = fields.Char(string="Item")
    specification = fields.Text(string="Specification")
    note = fields.Text(string="Note")
