from odoo import models, fields

class CreateInvoice(models.TransientModel):
    _name = "bikerental.create.invoice"
    _description = "bikerental.create.invoice"

    date = fields.Date()