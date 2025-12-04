from odoo import models, fields, api

class BikeModel(models.Model):
    _name = 'bike.model'
    _description = 'Bike'

    name = fields.Char(string="Name", required=True)
    brand = fields.Char(string="Brand")
    
    bike_type = fields.Selection(
        [('vtt', 'Mountain Bike'), ('ville', 'City Bike'), ('route', 'Road Bike')],
        string="Type"
    )

    product_id = fields.Many2one(
        'product.product',
        string="Product in Sales",
        ondelete='restrict'
    )
    
    price = fields.Float(string="Price per day")
    description = fields.Text(string="Description")
    
    # Image principale
    image = fields.Binary(string="Main Image")
   
    contract_ids = fields.One2many(
        'bike.rental.contract',
        'bike_id',
        string="Contracts"
    )

    available = fields.Boolean(
        string="Available",
        compute='_compute_available',
        store=True
    )

    sale_count = fields.Integer(
        string="Sales Count",
        compute='_compute_sale_count'
    )

    @api.depends('contract_ids.start_date', 'contract_ids.end_date')
    def _compute_available(self):
        today = fields.Date.today()
        for bike in self:
            active = bike.contract_ids.filtered(
                lambda c: c.start_date <= today <= c.end_date
            )
            bike.available = not bool(active)

    def _compute_sale_count(self):
        for bike in self:
            if bike.product_id:
                bike.sale_count = self.env['sale.order.line'].search_count([
                    ('product_id', '=', bike.product_id.id)
                ])
            else:
                bike.sale_count = 0

    def action_create_product(self):
        for bike in self:
            if not bike.product_id:
                product = self.env['product.product'].create({
                    'name': f"Rental - {bike.name}",
                    'type': 'service',
                    'list_price': bike.price,
                    'default_code': bike.name,
                    'categ_id': self.env['product.category'].search([], limit=1).id,                })
                bike.product_id = product.id
        return True

    def action_view_sales(self):
        self.ensure_one()
        if not self.product_id:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': f'Sales of {self.name}',
            'res_model': 'sale.order.line',
            'view_mode': 'list,form',
            'domain': [('product_id', '=', self.product_id.id)],
            'context': {'create': False},
        }

    @api.model
    def create(self, vals):
        bike = super(BikeModel, self).create(vals)
        bike.action_create_product()
        return bike