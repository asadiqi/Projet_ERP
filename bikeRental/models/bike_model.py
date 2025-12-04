from odoo import models, fields, api


class BikeModel(models.Model):
    _name = 'bike.model'
    _description = 'Bike'

    # Basic information
    name = fields.Char(string="Name", required=True)
    brand = fields.Char(string="Brand")

    bike_type = fields.Selection(
        [('vtt', 'Mountain Bike'), ('ville', 'City Bike'), ('route', 'Road Bike')],
        string="Type"
    )

    price = fields.Float(string="Price per day")
    description = fields.Text(string="Description")
    image = fields.Binary(string="Image")

    # Relations
    contract_ids = fields.One2many(
        'bike.rental.contract',
        'bike_id',
        string="Contracts"
    )

    # Availability calculation
    available = fields.Boolean(
        string="Available",
        compute='_compute_available',
        store=True
    )

    @api.depends('contract_ids.start_date', 'contract_ids.end_date')
    def _compute_available(self):
        """ Bike available if no active contract today. """
        today = fields.Date.today()

        for bike in self:
            active = bike.contract_ids.filtered(
                lambda c: c.start_date <= today <= c.end_date
            )
            bike.available = not bool(active)