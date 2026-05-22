{
    'name': 'FOP Encuestas Portal',
    'version': '17.0.1.0.0',
    'category': 'Website/Portal',
    'summary': 'Portal para que los usuarios autenticados vean sus encuestas en Documents',
    'author': 'Observatorio PyME',
    'website': 'https://observatoriopyme.org.ar',
    'license': 'OPL-1',
    'depends': [
        'portal',
        'website',
        'documents',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/document_user_rule.xml',
        'views/fop_encuestas_my_surveys.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
