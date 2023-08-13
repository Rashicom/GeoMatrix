from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from . import views

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('main_section_data/',views.main_section_data.as_view()),
    path('about_section_data/', views.about_section_data.as_view()),
    path('product_section_data/', views.product_section_data.as_view()),
    path('service_section_data/', views.service_section_data.as_view()),

]
