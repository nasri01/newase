"""ww URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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

from django.urls import include, path
from . import views


urlpatterns = [

    path('', views.router, name='router'),
    path('save/<slug:formtype>/', views.save_router, name='save_router'),
    # path('save_edit/<slug:formtype>/', views.save_edit_router, name='save_edit_router'),
    # path('save_recal/<slug:formtype>/', views.save_recal_router, name='save_recal_router'),
    # path('save_recal_edit/<slug:formtype>/', views.save_recal_edit_router, name='save_recal_edit_router'),
    path('delete/', views.delete_report, name='delete_report'),
    path('reload/<slug:formtype>/', views.reload, name='reload'),
]