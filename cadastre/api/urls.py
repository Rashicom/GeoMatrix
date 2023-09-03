from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'land_filter', views.LandFilteres, basename='land_filter')


urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    path('register_land/', views.RegisterLand.as_view()),
    path('get_land/', views.GetLand.as_view()),
    path('change_land_ownership/', views.ChangeLandOwnership.as_view()),
    path('get_user_land/',views.GetUserLand.as_view()),
    path('bulk_register_land/',views.BulkRegisterLand.as_view()),
    path('land_split/',views.LandSplitRegistration.as_view()),
    path('land_tax_rates/',views.LandTaxRates.as_view()),
    path('generate_tax_invoice/',views.GenerateTaxInvoice.as_view()),
    
    # land filters
    path('', include(router.urls)),



]