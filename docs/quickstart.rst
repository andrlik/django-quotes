.. _quickstart:

=========================
Quickstart
=========================

Django-Quotes uses `markovify <https://github.com/jsvine/markovify>`_ in conjunction with natural language processing functions from `spacy <https://spacy.io>`_ so installation and configuration requires some additional steps.

Installation
============

First, install ``django-quotes`` using a tool like pip.

.. code-block::
   :caption: 🎉 Look, it's the way you install almost every library!

   pip install django-quotes

Because we're using ``spacy``, we also need to download the language model we are using, which is ``en_core_web_sm``. While there are a number of ugly ways to automate this process, it's safer for you to do the installation directly using the following command.

.. code-block::
   :caption: It's an extra step because academia.

   python -m spacy download en_core_web_sm

Configuration
=============

Now we need to configure our Django project to use ``django-quotes``. Because we provide object-based permissions and a REST API, you'll also need to enable `Django REST Framework <https://www.django-rest-framework.org>`_ and `django-rules <https://github.com/dfunckt/django-rules>`_. Unless you plan on overriding the included templates, you should also include ``crispy-forms``.

.. code-block:: python
   :caption: settings.py

   # Number of quotes to fetch when doing random selections from a single source.
   # Optional. Default is 50.
   MAX_QUOTES_FOR_RANDOM_SET = 50

   # Number of quotes to fetch when doing random selections from a SourceGroup.
   # Optional. Default is 50.
   MAX_QUOTES_FOR_RANDOM_GROUP_SET = 50

   INSTALLED_APPS = [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.sites",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # "django.contrib.humanize", # Handy template tags
        "django.contrib.admin",
        "django.forms",
        "crispy_forms",
        "rest_framework",
        "rest_framework.authtoken",
        "corsheaders",
        "drf_spectacular",
        "rules.apps.AutodiscoverRulesConfig",
        "django_quotes",
        # Your stuff: custom apps go here
    ]

    # AUTHENTICATION
    # ------------------------------------------------------------------------------
    # https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
    AUTHENTICATION_BACKENDS = [
        "rules.permissions.ObjectPermissionBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]

    # MIDDLEWARE
    # ------------------------------------------------------------------------------
    # https://docs.djangoproject.com/en/dev/ref/settings/#middleware
    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.common.BrokenLinkEmailsMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    # django-rest-framework
    # -------------------------------------------------------------------------------
    # django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.TokenAuthentication",
        ),
        "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    }

    # django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
    CORS_URLS_REGEX = r"^/api/.*$"

    # By Default swagger ui is available only to admin user. You can change permission classs to change that
    # See more configuration options at https://drf-spectacular.readthedocs.io/en/latest/settings.html#settings
    SPECTACULAR_SETTINGS = {
        "TITLE": "Django Quotes API",
        "DESCRIPTION": "Documentation of API endpoints of Django Quotes",
        "VERSION": "1.0.0",
        "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
        "SERVERS": [
            {"url": "https://127.0.0.1:8000", "description": "Local Development server"},
        ],
    }


Setup URLS
==========

You'll need to wire up the views to your project URLs configuration as displayed below.

First configure your API router.

.. code-block:: python
   :caption: api_router.py

    from django.conf import settings
    from rest_framework.routers import DefaultRouter, SimpleRouter

    from django_quotes.api.views import SourceGroupViewSet, SourceViewSet

    if settings.DEBUG:
        router = DefaultRouter()
    else:
        router = SimpleRouter()

    router.register("groups", SourceGroupViewSet, basename="group")
    router.register("sources", SourceViewSet, basename="source")


    app_name = "api"
    urlpatterns = router.urls

.. code-block:: python
   :caption: urls.py

   urlpatterns = [
        # Chose whatever path your want, but keep the namespace as ``quotes``.
        path("app/", include("django_quotes.urls", namespace="quotes")),
        # API base url. You can change this path if you like.
        path("api/", include("path.to.your.api_router")),
        # DRF auth token
        path("auth-token/", obtain_auth_token),
        path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="api-schema"),
            name="api-docs",
        ),
        # Insert your other URLS here.
   ]

Customizing Templates (Optional)
================================

If you want to override the existing templates, you can. By default, they are `Bootstrap 5 <https://getbootstrap.com>`_-compatible, although we do not bundle Bootstrap within the project. To override, create a ``templates/quotes`` directory in your project and add the following templates:

.. code-block:: bash
   :caption: Their purposes should be self explanatory. You can see the :ref:`views` documentation for more information.

    ls django_quotes/templates/quotes

    group_create.html
    group_delete.html
    group_detail.html
    group_list.html
    group_update.html
    quote_create.html
    quote_delete.html
    quote_detail.html
    quote_list.html
    quote_update.html
    source_create.html
    source_delete.html
    source_detail.html
    source_list.html
    source_update.html

Usage
=====

By default, django-quotes provides access via the admin site, and provides a set of basic views for managing the quotes and associated data. See :ref:`manage_quotes` for more information.
