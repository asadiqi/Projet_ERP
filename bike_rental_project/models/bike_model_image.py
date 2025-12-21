from odoo import models, fields

class BikeModelImage(models.Model):
    _name = 'bike.model.image'
    _description = 'Bike Gallery Images'
    _order = 'sequence asc'

    name = fields.Char(string="Description")
    image = fields.Binary(string="Photo", required=False)
    sequence = fields.Integer(string="Order", default=10)

    bike_id = fields.Many2one(
        'bike.model',
        string="Bike",
        ondelete='cascade'
    )
