from odoo import models, fields, api

class BikeAvailabilityWizard(models.TransientModel):
    _name = 'bike.availability.wizard'
    _description = 'Check Bike Availability'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    available_bike_ids = fields.Many2many(
        'bike.model',
        string="Available Bikes"
    )

    def _compute_available_bikes(self):
        for wiz in self:
            if not (wiz.start_date and wiz.end_date):
                wiz.available_bike_ids = self.env['bike.model'].search([])
                continue

            overlapping = self.env['bike.rental.contract'].search([
                ('start_date', '<=', wiz.end_date),
                ('end_date', '>=', wiz.start_date),
            ])

            bikes_unavailable_ids = overlapping.mapped('bike_id').ids

            wiz.available_bike_ids = self.env['bike.model'].search([
                ('id', 'not in', bikes_unavailable_ids)
            ])

    def action_check_availability(self):
        self._compute_available_bikes()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'bike.availability.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }