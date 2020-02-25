import os

DBEUG = True
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_todo_db',
        'USER': 'django_todo_admin',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'POST': '5432',
    }
}
