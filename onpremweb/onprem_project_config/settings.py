from pathlib import Path
import os
from dotenv import load_dotenv

# settings.py 파일 위치 기준
current_file = os.path.abspath(__file__)
print("Django settings file:", current_file)

# 프로젝트 루트(Base dir)를 settings.py의 두 단계 상위로 잡습니다.
BASE_DIR = Path(current_file).resolve().parent.parent
print("Computed BASE_DIR:", BASE_DIR)

# .env는 BASE_DIR 아래에 있어야 하므로
ENV_PATH = BASE_DIR / '.env'
print("Looking for .env at:", ENV_PATH)
print("ENV file exists?:", ENV_PATH.exists())

# 실제 로드
load_dotenv(str(ENV_PATH))

# 이후 환경변수 사용
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS 안전하게 분리
raw_hosts = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = raw_hosts.split(',') if raw_hosts else []

print("Loaded ALLOWED_HOSTS:", ALLOWED_HOSTS)


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'community',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'onprem_project_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],
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
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'community:post_list'
LOGOUT_REDIRECT_URL = 'home'

WSGI_APPLICATION = 'onprem_project_config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR / 'static' ]
STATIC_ROOT = BASE_DIR / 'staticfiles'
#STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_collected')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
