from django.urls import path, include
from . import views

urlpatterns = [
    path('main_section_data/',views.main_section_data.as_view()),
    path('about_section_data/', views.about_section_data.as_view()),
    path('product_section_data/', views.product_section_data.as_view()),
    path('service_section_data/', views.service_section_data.as_view()),

]
