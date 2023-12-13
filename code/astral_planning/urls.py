"""
URL configuration for astral_planning project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from planning import views as planning_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('planning/', planning_views.PlanningView.as_view(), name='planning'),
    path('apply_planning/', planning_views.ApplyPlanningView.as_view(), name='apply_planning'),
    path('cancel_planning/', planning_views.CancelPlanningView.as_view(), name='cancel_planning'),
    path('resources/', planning_views.ResourcesView.as_view(), name='resources'),
    path('geocoding/', planning_views.GeocodingView.as_view(), name='geocoding'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
