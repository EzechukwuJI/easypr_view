import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAT = 0.05
NAIRA_DOLLAR_RATE = float(330)
IMAGE_FEE_N       = float(10000)


if 'DB_NAME' in os.environ:
    PAYSTACK_SECRET_KEY  =   os.environ['PAYSTACK_SECRET_KEY']
    DJANGO_SECRET_KEY    =   os.environ['DJANGO_SECRET_KEY']
    DB_NAME              =   os.environ['DB_NAME']
    DB_USER              =   os.environ['DB_USERNAME']
    DB_PASSWORD          =   os.environ['DB_PASSWORD']
    DB_HOSTNAME          =   os.environ['DB_HOSTNAME']
    DB_PORT              =   os.environ['DB_PORT']
    EMAIL_PROVIDER       =   os.environ['EMAIL_PROVIDER']
    EMAIL_HOST_PASSWORD  =   os.environ['EMAIL_PASSWORD']

    DEBUG_STATUS         =   False
    ALLOWED_HOSTS        =   ['easypr-test.us-west-2.elasticbeanstalk.com','www.easypr.ng','easypr.ng']
else:
    PAYSTACK_SECRET_KEY  =   'sk_test_293d0e2e5e7450eb84a80d46455cc9b7ea3ff3c8'
    DJANGO_SECRET_KEY    =   '9cn$74iq@1)c8d=+q(pc=q#d5t*^m*c+ol-!%-*j0l+2m8_oux'
    DB_NAME              =   'easypr_db'
    DB_USER              =   'root'
    DB_PASSWORD          =   'root'
    DB_HOSTNAME          =   '127.0.0.1'
    DB_PORT              =   '3306'
    EMAIL_PROVIDER       =   'smtp.zoho.com'
    EMAIL_HOST_PASSWORD  =   '' #set in development

    DEBUG_STATUS = True
    ALLOWED_HOSTS = []

    

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    '/var/www/static/',
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


SECRET_KEY = '9cn$74iq@1)c8d=+q(pc=q#d5t*^m*c+ol-!%-*j0l+2m8_oux'

if 'RDB_DB_NAME' in os.environ:
    DEBUG = False
    ALLOWED_HOSTS = ['easypr-test.us-west-2.elasticbeanstalk.com']
else:
    DEBUG = True

ALLOWED_HOSTS = []

SITE_ID = 1


ZINNIA_ENTRY_CONTENT_TEMPLATES = [
  ('zinnia/_short_entry_detail.html', 'Short entry template'),
]

# Application definition
DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    )

EASYPR_APPS = (
    'easypr_general',
    'easypr_ng',
    'easypr_admin',
    )

EXTERNAL_APPS = ('django_coverage',)

BLOG_APPS = ('django_comments','mptt','tagging','zinnia',)

INSTALLED_APPS =  DJANGO_APPS + EASYPR_APPS + EXTERNAL_APPS + BLOG_APPS


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    
    'easypr_ng.middleware.MarketingBundlesMiddleware',
)

# PROFILER_MIDDLEWARE = ('easypr_ng.middleware.ProfileMiddleware',)
# if DEBUG == True:
#     MIDDLEWARE_CLASSES += PROFILER_MIDDLEWARE

ROOT_URLCONF = 'easypr.urls'

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
                'django.template.context_processors.i18n',
                'zinnia.context_processors.version',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'easypr.wsgi.application'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE'  : 'django.db.backends.mysql',
            # 'NAME'    : 'new_easypr_db_backup',
            'NAME'    : 'easypr_db',
            'USER'    : 'root',                      # Not used with sqlite3.
            'PASSWORD': 'root',                      # Not used with sqlite3.
            'HOST'    : '127.0.0.1',                 # Set to empty string for localhost. Not used with sqlite3.
            'PORT'    : '3306',                      # Set to empty string for default. Not used with sqlite3.
        }
    }


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/


EMAIL_BACKEND           =   'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS           =    True
EMAIL_HOST              =   'smtp.zoho.com'
EMAIL_HOST_USER         =   'info@easypr.ng'
EMAIL_HOST_PASSWORD     =   '@easypr_ng.admin'
EMAIL_PORT              =    587
DEFAULT_FROM_EMAIL      =    EMAIL_HOST_USER


if 'RDS_DB_NAME' in os.environ:
    STATIC_ROOT          =          os.path.join(BASE_DIR, "static")
    STATIC_URL           =         '/static/'
else:
    # STATIC_ROOT      =          '/'
    STATIC_ROOT      =          '/var/www/easypr.ng/static/'
    STATIC_URL       =          '/static/'
    
MEDIA_ROOT           =          'media'
MEDIA_URL            =          '/media/'
LOGIN_URL            =          '/login/'
LOGOUT_URL           =          '/logout/'
