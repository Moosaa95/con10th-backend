

from pathlib import Path
import os, sys
from os import getenv
from django.core.management.utils import get_random_secret_key
import cloudinary
from datetime import timedelta
from dotenv import load_dotenv



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

env_path = BASE_DIR  / '.env.local'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
# load_dotenv()



SECRET_KEY = getenv('DJANGO_SECRET_KEY')

DEBUG = True

# ALLOWED_HOSTS = []



# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = getenv('DEBUG', 'False') == 'True'


ALLOWED_HOSTS = getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost,https://platform-skills-xih5.vercel.app/,https://con10th-frontend.vercel.app/,con10th-backend.onrender.com').split(',')


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'cloudinary',
    'drf_spectacular',
    'rest_framework',
    'corsheaders',
    'djoser',
    'rest_framework_simplejwt',
    'django_celery_results',
    'debug_toolbar',                            
    # 'django_filters',
    # 'channels',
]

LOCAL_APPS = [
    'accounts',
    # 'projects',
    # 'dashboard',
    'services',
    'category',
    'clients',
    # 'chats'
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS



INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]




MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'  # or your chosen backend
# SESSION_COOKIE_NAME = 'sessionid'
# SESSION_COOKIE_SECURE = False  # in development; True in production with HTTPS
# SESSION_COOKIE_DOMAIN = None  # or the proper domain if needed


ROOT_URLCONF = 'coronith.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'coronith.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


AUTH_USER_MODEL = "accounts.CustomUser"

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True



# DRF_STANDARDIZED_ERRORS = {"EXCEPTION_FORMATTER_CLASS": "common.exceptions.APIExceptionFormatter"}
# DJOSER
# DJOSER = {
#     # 'LOGIN_FIELD': 'email',
#     'USER_CREATE_PASSWORD_RETYPE': True,
#     # 'USERNAME_CHANGED_EMAIL_CONFIRMATION': True,
#     'SEND_ACTIVATION_EMAIL': False,
#     # 'SET_PASSWORD_RETYPE': True,
#     'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
#     'USERNAME_RESET_CONFIRM_RETYPE': True,
#     'ACTIVATION_URL': 'activate/{uid}/{token}',
#     'SEND_CONFIRMATION_EMAIL': False,
#     'PASSWORD_RESET_CONFIRM_RETYPE': False,
#     'SERIALIZERS': {
#         'user_create': 'accounts.serializers.CustomUserCreateSerializer',  # Ensure this exists
#     },
#     # 'ACTIVATION_EMAIL_TEMPLATES': {
#     #     'subject': 'accounts/activation_email_subject.txt',
#     #     'body': 'accounts/activation_email_body.html',
#     # },
#     # 'SERIALIZERS': {
#     #     'user_create': 'accounts.serializers.CustomUserCreateSerializer',
#     #     'user': 'accounts.serializers.CustomUserCreateSerializer',
#     #     'current_user': 'accounts.serializers.CustomUserCreateSerializer',
#     # },
#     # 'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
#     # 'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True,
#     # 'PASSWORD_RESET_CONFIRM_RETYPE': True,
# }

# SIMPLEJWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    # 'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication',
    # 'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    # 'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    # 'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    # 'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),

    # 'TOKEN_OBTAIN_SERIALIZER': 'accounts.serializers.TokenObtainPairSerializer',
    # 'TOKEN_REFRESH_SERIALIZER': 'accounts.serializers.TokenRefreshSerializer',
    # 'TOKEN_VERIFY_SERIALIZER': 'accounts.serializers.TokenVerifySerializer',
    'EXCEPTION_HANDLER': 'accounts.utils.custom_exception_handler',
    'NON_FIELD_ERRORS_KEY': 'non_field_errors',
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Directory where collectstatic will gather all static files (for production)
# STATIC_ROOT = BASE_DIR / "staticfiles"

# # Directories where Django will search for additional static files (for development)
# STATICFILES_DIRS = [
#     BASE_DIR / "static",  # ✅ Adjusted for your custom BASE_DIR
# ]
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


cloudinary.config( 
  cloud_name = getenv("CLOUD_NAME"),
  api_key = getenv("CLOUD_API_KEY"),
  api_secret = getenv("CLOUD_SECRET_KEY"), 
)



REST_FRAMEWORK = {
    # 'DEFAULT_AUTHENTICATION_CLASSES': (
    #     'rest_framework.authentication.SessionAuthentication',  # Optional, for browsing API
    #     'rest_framework.authentication.TokenAuthentication',  # If using token authentication
    # ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.accounts.authentication.CustomJWTAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', 
    ],
    # YOUR SETTINGS
    # "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
    'EXCEPTION_HANDLER': 'commons.exceptions.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


DRF_STANDARDIZED_ERRORS = {"EXCEPTION_FORMATTER_CLASS": "common.exceptions.APIExceptionFormatter"}


SPECTACULAR_SETTINGS = {
    'TITLE': 'Con10th API',
    'DESCRIPTION': 'API for Con10th project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SERVE_URLCONF': 'coronith.urls',
    'SCHEMA_PATH_PREFIX': '/api/schema',
    
    # OTHER SETTINGS
}



EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.mailgun.org"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST = getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = "moosaabdullahi45@gmail.com"



# CELERY SETTINGS
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
# CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://red-cvli5npr0fns73ckuepg:6379")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
# save Celery task results in Django's database
CELERY_RESULT_BACKEND = "django-db"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
