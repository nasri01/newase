from django.urls import path
from . import views

urlpatterns = [
    path(
        'xlsx/<slug:filtering>/<int:query_start_year>/<int:query_start_month>/<int:query_start_day>/<int:query_end_year>/<int:query_end_month>/<int:query_end_day>/<slug:operation_type>/',
        views.xlsx, name='report-xlsx'),
    path('request_summary/', views.show_request_summary, name='req_summary'),
    # path('pdf/', views.pdf1, name='report-pdf1'),
    # path('pdf1/', views.pdf, name='report-pdf'),
    path('view/', views.reportview , name='view_report'),
]
