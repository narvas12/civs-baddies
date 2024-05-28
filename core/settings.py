from datetime import timedelta
import os
from pathlib import Path
# from decouple import Config, Csv
from pathlib import Path
import django
import environ
import cloudinary_storage

import cloudinary
import cloudinary.uploader
import cloudinary.api
import cloudinary_storage


env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(BASE_DIR / '.env')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&08=$hi14+qe_=)e$9k1g*j%@4so05pr=^2@7fl0^vvf)1ag@-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # apps
    'users', 
    'common',
    'products',
    'orders',
    'cart',
    'checkout',
    
    #third party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_apscheduler',
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'django_rest_passwordreset',
    'cloudinary',
    'cloudinary_storage',
]


MIDDLEWARE = [
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    
    # third part
    "users.middleware.UserVisitMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]
    
AUTHENTICATION_BACKENDS = [
    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
]

CORS_ORIGIN_ALLOW_ALL = True
# # Provider specific settings
# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         # For each OAuth based provider, either add a ``SocialApp``
#         # (``socialaccount`` app) containing the required client
#         # credentials, or list them here:
#         'APP': {
#             'client_id': '123',
#             'secret': '456',
#             'key': ''
#         }
#     }
# }


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    
    }
}

ROOT_URLCONF = 'core.urls'
BASE_URL = 'http://127.0.0.1:8000/api/v1/users/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]

# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'users.CustomUser'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.CustomPagination',
    'PAGE_SIZE': 20,
}


SIMPLE_JWT = {
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'AUTH_TOKEN_CLASSES': ['rest_framework_simplejwt.tokens.AccessToken'],
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(levelname)s %(message)s"}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    },
    "loggers": {
        "": {"handlers": ["console"], "propagate": True, "level": "DEBUG"},
        # 'django': {
        #     'handlers': ['console'],
        #     'propagate': True,
        #     'level': 'WARNING',
        # },
        # 'request_profiler': {
        #     'handlers': ['console'],
        #     'propagate': True,
        #     'level': 'WARNING',
        # },
    },
}

ROOT_URLCONF = "core.urls"

###################################################
# django_coverage overrides

# Specify a list of regular expressions of module paths to exclude
# from the coverage analysis. Examples are ``'tests$'`` and ``'urls$'``.
# This setting is optional.
COVERAGE_MODULE_EXCLUDES = [
    "tests$",
    "settings$",
    "urls$",
    "locale$",
    "common.views.test",
    "__init__",
    "django",
    "migrations",
    "request_profiler.admin",
    "request_profiler.signals",
]
# COVERAGE_REPORT_HTML_OUTPUT_DIR = 'coverage/html'
# COVERAGE_USE_STDOUT = True

# turn off caching for tests
REQUEST_PROFILER_RULESET_CACHE_TIMEOUT = 0

# AUTH_USER_MODEL = 'tests.CustomUser'
if not DEBUG:
    raise django.core.exceptions.ImproperlyConfigured(
        "This settings file can only be used with DEBUG=True"
    )


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'dvc.africa@gmail.com' # Replace with your Gmail address
EMAIL_HOST_PASSWORD = 'mfpkqcpawzmtrzpi' # Replace with your Gmail password or app password
EMAIL_USE_TLS = True




# Social Auth Config 
# client_id = 1030132047010-iipdf4mhb39ape0ba636dq3beejcm2q6.apps.googleusercontent.com
# client_secret = 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 




# Cloudinary configuration
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dsmgwxyzi',
    'API_KEY': '818626184762193',
    'API_SECRET': 'vkvy1acRglD1laypnLQW2RCsBzs'
}


# CLOUDINARY_STORAGE = {
#     'CLOUD_NAME': 'your_cloud_name',
#     'API_KEY': os.environ.get('CLOUDINARY_API'),
#     'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET')
# }




# Number of minutes of inactivity before a user is marked offline
USER_ONLINE_TIMEOUT = 10

# Number of seconds that we will keep track of inactive users for before 
# their last seen is removed from the cache
USER_LASTSEEN_TIMEOUT = 60 * 60 * 24 * 7


# PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
# PAYSTACK_PUBLIC_KEY = env('PAYSTACK_PUBLIC_KEY')
