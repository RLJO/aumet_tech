# -*- coding: utf-8 -*-
# Copyright 2016, 2020 Openworx - Mario Gielissen
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Aumet backend theme",
    "summary": "Aumet backend theme",
    "version": "14.0.0.2",
    "category": "Theme/Backend",

    "description": """
    """,

    'images': [
        'description/icon.png'
    ],
    "depends": [
        'base',
        'web',
        'web_responsive',
    ],

    "data": [
        'views/assets.xml',
        'views/sidebar.xml',
        'views/users.xml',

    ],

    'css': ["static/src/css/aumet.css"],
    "author": "Ihab Shhadat",
    'pre_init_hook': '_icon_pre_init_hook',
    'post_init_hook': '_icon_post_init_hook',

    "installable": True,

}
