{
    'name': 'bike_rental',
    'version': '0.0.8',
    'category': 'Services',
    'summary': 'Gestion des contrats de location de vélos',
    'author': 'TeamAnasAmirOussama',
    'depends': ['base', 'contacts', 'sale'],
    'data': [
        # Sécurité
        'security/ir.model.access.csv',

        # Vues
        'views/bike_model_views.xml',
        'views/rental_contract_views.xml',
        'views/availability_wizard_views.xml',
        'views/rental_invoice_views.xml',
        'views/menu.xml',

        # Données initiales (CSV)
        'data/bike.model.csv',
        'data/res.partner.csv',
        'data/bike.rental.contract.csv',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
