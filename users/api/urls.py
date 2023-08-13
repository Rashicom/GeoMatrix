from django.urls import path, include
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('signup/',views.signup.as_view()),
    path('login/',views.login.as_view()),
    path('add_address/', views.add_address.as_view()),
    path('edit_address/',views.edit_address.as_view()),
    path('update_user/',views.update_user.as_view()),
    path('new_transaction/',views.new_transaction.as_view()),
    path('get_wallet_balance/',views.get_wallet_balance.as_view()),
    path('get_wallet_transaction/',views.get_wallet_transaction.as_view()),
    path('trasaction_history/',views.trasaction_history.as_view()),


]