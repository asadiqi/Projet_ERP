from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RentalContract(models.Model):
    _name = 'bike.rental.contract'  # Identifiant unique du modèle
    _description = 'Contrat de location'  # Description lisible

    # Nom du contrat (ex: "Contrat #001") obligatoire
    name = fields.Char(string="Nom du contrat", required=True)

    # Client qui loue le vélo (Many2one vers res.partner)
    customer_id = fields.Many2one('res.partner', string="Client", required=True)

    # Vélo loué (Many2one vers bike.model)
    bike_id = fields.Many2one('bike.model', string="Vélo", required=True)

    # Date de début et de fin du contrat
    start_date = fields.Date(string="Date début", required=True)
    end_date = fields.Date(string="Date fin", required=True)

    # Durée en jours (calcul automatique)
    duration = fields.Integer(string="Durée (jours)", compute='_compute_duration', store=True)

    # Prix total du contrat (calcul automatique: durée x prix vélo)
    price = fields.Float(string="Prix", compute='_compute_price', store=True)

    # Notes supplémentaires du contrat
    notes = fields.Text(string="Notes")

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        """
        Calcule automatiquement la durée du contrat en jours
        """
        for rec in self:
            if rec.start_date and rec.end_date:
                rec.duration = (rec.end_date - rec.start_date).days
            else:
                rec.duration = 0

    @api.depends('duration', 'bike_id')
    def _compute_price(self):
        """
        Méthode automatique pour calculer le prix total du contrat.
        
        Elle est exécutée à chaque fois que :
        - la durée (duration) change
        - le vélo choisi (bike_id) change
        
        self peut contenir un ou plusieurs contrats, c’est pourquoi
        on boucle dessus.
        """
        for rec in self:
            if rec.bike_id and rec.duration:
                rec.price = rec.bike_id.price * rec.duration
            else:
                rec.price = 0.0

    @api.constrains('bike_id', 'start_date', 'end_date')
    def _check_bike_availability(self):
        """
        Empêche de créer un contrat pour un vélo déjà loué
        pendant une période qui chevauche un contrat existant.
        """
        for rec in self:
            overlapping = self.env['bike.rental.contract'].search([
                ('bike_id', '=', rec.bike_id.id),
                ('id', '!=', rec.id),  # Ignore le contrat courant
                ('start_date', '<=', rec.end_date),
                ('end_date', '>=', rec.start_date),
            ])
            if overlapping:
                raise ValidationError(
                    f"Le vélo {rec.bike_id.name} est déjà réservé pendant cette période."
                )
