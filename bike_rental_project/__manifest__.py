{
    'name': 'bike_rental',
    'version': '0.0.8',
    'category': 'Services',
    'summary': 'Gestion des contrats de location de vélos',
    'author': 'TeamAnasAmirOussama',
    'depends': ['base', 'contacts', 'sale'],
    'data': [
        "security/ir.model.access.csv",
        'views/bike_model_views.xml',
        'views/rental_contract_views.xml',
        'views/availability_wizard_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',  
}