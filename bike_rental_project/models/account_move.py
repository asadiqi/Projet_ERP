from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_rental_invoice = fields.Boolean(string="Rental Invoice")
    rental_contract_id = fields.Many2one(
        'bike.rental.contract',
        string="Rental Contract",
        readonly=True
    )

    def add_late_fee(self):
        product = self.env['product.product'].search([('default_code', '=', 'LATE_FEE')], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': 'Late Fee',
                'default_code': 'LATE_FEE',
                'lst_price': 0,   # prix par défaut, tu peux le modifier plus tard
                'type': 'service', # important pour que ce soit un service
            })
        for invoice in self:
            self.env['account.move.line'].create({
                'move_id': invoice.id,
                'product_id': product.id,
                'quantity': 1,
                'price_unit': product.lst_price,
                'name': product.name,
            })

    def add_damage_fee(self):
        product = self.env['product.product'].search([('default_code', '=', 'DAMAGE_FEE')], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': 'Damage Fee',
                'default_code': 'DAMAGE_FEE',
                'lst_price': 0,
                'type': 'service',
            })
        for invoice in self:
            self.env['account.move.line'].create({
                'move_id': invoice.id,
                'product_id': product.id,
                'quantity': 1,
                'price_unit': product.lst_price,
                'name': product.name,
            })
