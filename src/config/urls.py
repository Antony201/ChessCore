from api.views import CustomTokenObtainPairView, CustomTokenRefreshView

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView

from rest_framework.authtoken.views import obtain_auth_token

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Capablanca API",
        description="Multiplayer Chess API",
        default_version="0.2.0",
        urlconf="config.api_router",
    ),
)

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("core.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # OpenAPI
    path(
        "docs/", schema_view.with_ui("swagger", cache_timeout=0), name="openapi-schema",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # Simple JWT
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
    # DRF auth
    path("api-auth/", include("rest_framework.urls")),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]

""" Django exceptions """
handler400 = 'core.exceptions.bad_request_view'
handler403 = 'core.exceptions.permission_denied_view'
handler404 = 'core.exceptions.page_not_found_view'
handler500 = 'core.exceptions.server_error_view'

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
