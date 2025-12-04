from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RentalContract(models.Model):
    _name = 'bike.rental.contract'
    _description = 'Rental Contract'

    name = fields.Char(string="Contract Name", required=True)
    customer_id = fields.Many2one('res.partner', string="Customer", required=True)
    bike_id = fields.Many2one('bike.model', string="Bike", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    duration = fields.Integer(string="Duration (days)", compute='_compute_duration', store=True)
    price = fields.Float(string="Price", compute='_compute_price', store=True)
    notes = fields.Text(string="Notes")

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                rec.duration = (rec.end_date - rec.start_date).days
            else:
                rec.duration = 0

    @api.depends('duration', 'bike_id')
    def _compute_price(self):
        for rec in self:
            if rec.bike_id and rec.duration:
                rec.price = rec.bike_id.price * rec.duration
            else:
                rec.price = 0.0

    @api.constrains('bike_id', 'start_date', 'end_date')
    def _check_bike_availability(self):
        for rec in self:
            overlapping = self.env['bike.rental.contract'].search([
                ('bike_id', '=', rec.bike_id.id),
                ('id', '!=', rec.id),
                ('start_date', '<=', rec.end_date),
                ('end_date', '>=', rec.start_date),
            ])
            if overlapping:
                raise ValidationError(
                    f"Bike {rec.bike_id.name} is already booked during this period."
                )