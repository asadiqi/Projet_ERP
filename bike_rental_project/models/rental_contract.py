from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class RentalContract(models.Model):
    _name = 'bike.rental.contract'
    _description = 'Rental Contract'

    name = fields.Char(string="Contract Name", required=True)
    customer_id = fields.Many2one('res.partner', string="Customer", required=True)
    bike_id = fields.Many2one('bike.model', string="Bike", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    notes = fields.Text(string="Notes")

    # =========================
    # WORKFLOW / STATUS
    # =========================
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('ongoing', 'Ongoing'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string="Status",
        default='draft',
        tracking=True
    )

    # =========================
    # COMPUTED FIELDS
    # =========================
    duration = fields.Integer(string="Duration (days)", compute='_compute_duration', store=True)
    price = fields.Float(string="Price", compute='_compute_price', store=True)
    
    # =========================
    # INVOICING (Rental Invoice)
    # =========================
    # This field links the rental contract to a customer invoice
    invoice_id = fields.Many2one(
        'account.move',
        string="Rental Invoice",
        readonly=True
    )

    is_late = fields.Boolean(string="Returned Late")
    is_damaged = fields.Boolean(string="Damaged")

    # =========================
    # COMPUTE METHODS
    # =========================
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

    # =========================
    # INVOICE CREATION
    # =========================
    def _create_rental_invoice(self):
        self.ensure_one()

        if not self.customer_id:
            raise UserError("Customer is missing.")

        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'is_rental_invoice': True,
            'rental_contract_id': self.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': f"Bike rental: {self.bike_id.name}",
                    'quantity': self.duration,
                    'price_unit': self.bike_id.price,
                })
            ]
        })

        return move
    # =========================
    # BUSINESS CONSTRAINTS
    # =========================
    @api.constrains('bike_id', 'start_date', 'end_date', 'state')
    def _check_bike_availability(self):
        """
        Prevent overlapping rentals for the same bike.
        Only contracts that are confirmed or ongoing
        block the availability.
        """
        for rec in self:
            if rec.state in ['confirmed', 'ongoing']:
                overlapping = self.env['bike.rental.contract'].search([
                    ('bike_id', '=', rec.bike_id.id),
                    ('id', '!=', rec.id),
                    ('state', 'in', ['confirmed', 'ongoing']),
                    ('start_date', '<=', rec.end_date),
                    ('end_date', '>=', rec.start_date),
                ])
                if overlapping:
                    raise ValidationError(
                        f"Bike {rec.bike_id.name} is already booked during this period."
                    )

    
    # =========================
    # WORKFLOW ACTIONS
    # =========================

    def action_confirm(self):
        """
        Confirm the rental reservation.
        """
        for rec in self:
            if rec.state != 'draft':
                raise UserError("Only draft contracts can be confirmed.")
            rec.state = 'confirmed'

    def action_start_rental(self):
        """
        Mark the bike as picked up by the customer.
        """
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError("Only confirmed contracts can be started.")
            rec.state = 'ongoing'

    def action_cancel(self):
        """
        Cancel the contract (if not finished).
        """
        for rec in self:
            if rec.state == 'done':
                raise UserError("You cannot cancel a finished contract.")
            rec.state = 'cancelled'
    
    def action_return_bike(self):
        for rec in self:
            if rec.state != 'ongoing':
                raise UserError("Only ongoing contracts can be returned.")

            # Create invoice
            invoice = rec._create_rental_invoice()

            rec.invoice_id = invoice.id
            rec.state = 'done'

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'Rental invoice created',
                    'type': 'success',
                    'sticky': False,
                }
            }