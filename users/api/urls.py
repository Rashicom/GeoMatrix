from django.urls import path, include
from . import views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("signup/", views.signup.as_view()),
    path("login/", views.login.as_view()),
    path("add_address/", views.add_address.as_view()),
    path("edit_address/", views.edit_address.as_view()),
    path("get_address/", views.get_address.as_view()),
    path("update_user/", views.update_user.as_view()),
    path("new_transaction/", views.new_transaction.as_view()),
    path("get_wallet_balance/", views.get_wallet_balance.as_view()),
    path("get_wallet_transaction/", views.get_wallet_transaction.as_view()),
    path("transaction_history/", views.transaction_history.as_view()),
    path("gov_body_signup/", views.gov_body_signup.as_view()),


    # admin routs
    path("gov_body_signup/", views.gov_body_signup.as_view()),
    path("gov_login/", views.GovBodylogin.as_view()),
    path("get_govwallet_balance/", views.GetGovwalletbalance.as_view()),
    path("gov_transaction/", views.GovnewTransaction.as_view()),
    path("gov_transaction_history/", views.GovTransactionHistory.as_view()),


]


