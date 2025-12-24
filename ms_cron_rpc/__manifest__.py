# -*- coding: utf-8 -*-
{
    'name': "CRON RPC",
    'summary': "CRON RPC",
    'description': "CRON RPC",
    'author': "MS solution ERP",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': ['base','product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
}

