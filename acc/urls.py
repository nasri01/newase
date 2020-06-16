from django.urls import include, path
from . import views


urlpatterns = [
    path('', views.login, name='login1'),
    path('log_out/', views.logout, name='logout1'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('request_list/', views.show_request_list, name='req_list'),
    path('recalibration_list/', views.show_recalibration_list, name='recal_list'),
    path('report_list/', views.show_report_list, name='report_list'),
    path('edit/', views.edit_report, name='edit_report'),
    path('recal/', views.recal_report, name='recal_report'),
    path('change_email/', views.change_email, name='change_email'),
    path('make_done/', views.make_done, name='make_done'),

]
