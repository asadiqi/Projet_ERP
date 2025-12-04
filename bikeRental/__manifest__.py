{
    'name': 'Bike_Rental',
    'version': '0.0.8',
    'category': 'Services',
    'summary': 'Gestion des contrats de location de vélos',
    'author': 'TeamAnasAmirOussama',
    'depends': ['base', 'contacts'],
    'data': [
        "security/ir.model.access.csv",
        'views/bike_model_view.xml',
        'views/rental_contract_views.xml',
        'views/availability_wizard_views.xml',
        'views/menus.xml',
        # CSVs à charger après
        'data/bike.model.csv',
        'data/res.partner.csv',
        'data/bike.rental.contract.csv',
    ],
    'installable': True,
    'application': True,
}
