"""
URL configuration for firehousemovers project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),  # Admin panel
    path("", include("inventory_app.urls")),  # Include inventory_app routes
    path("", include("authentication.urls")),  # Include authentication routes
    path("", include("vehicle.urls")),  # Include vehicle routes
    path("station/", include("station.urls")),  # Include station routes
    path("", include("gift.urls")),  # Include gift routes
    path("", include("inspection.urls")),  # Include gift routes
    path("packaging/", include("packaging_supplies.urls")),  # Include packaging_supplies routes
    path("marketing/", include("marketing.urls", namespace="marketing")),
    path("awards/", include("gift.urls", namespace="awards")),
    path('evaluation/', include('evaluation.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("emails/", include('django_mail_viewer.urls'))]
