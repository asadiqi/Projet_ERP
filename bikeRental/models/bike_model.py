from odoo import models, fields, api


class BikeModel(models.Model):
    _name = 'bike.model'
    _description = 'Vélo'

    # Informations de base
    name = fields.Char(string="Nom", required=True)
    brand = fields.Char(string="Marque")

    bike_type = fields.Selection(
        [('vtt', 'VTT'), ('ville', 'Ville'), ('route', 'Route')],
        string="Type"
    )

    price = fields.Float(string="Prix par jour")
    description = fields.Text(string="Description")
    image = fields.Binary(string="Image")

    # Relations
    contract_ids = fields.One2many(
        'bike.rental.contract',
        'bike_id',
        string="Contrats"
    )

    # Calcul de disponibilité
    available = fields.Boolean(
        string="Disponible",
        compute='_compute_available',
        store=True
    )

    @api.depends('contract_ids.start_date', 'contract_ids.end_date')
    def _compute_available(self):
        """ Vélo disponible si aucun contrat actif aujourd'hui. """
        today = fields.Date.today()

        for bike in self:
            active = bike.contract_ids.filtered(
                lambda c: c.start_date <= today <= c.end_date
            )
            bike.available = not bool(active)
