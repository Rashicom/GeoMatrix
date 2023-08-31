from rest_framework.authentication import BaseAuthentication
from rest_framework.authentication import BasicAuthentication
from django.conf import settings
from django.apps import apps as django_apps
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication

# serverless jwt is ok for normal customers
# additional email check and role check layer for gov users


# get the normal user model from setting.py
def get_normaluser_model():
    """
    Return the Normal User model that is set in settings.py
    """
    try:
        return django_apps.get_model(settings.AUTH_USER_MODEL_NORMALUSER, require_ready=False)
    except Exception as e:
        print("AUTH_USER_MODEL_NORMALUSER not found in settings")



# get the normal user model from setting.py
def get_govuser_model():
    """
    Return the Normal User model that is set in settings.py
    """
    try:
        return django_apps.get_model(settings.AUTH_USER_MODEL_GOV, require_ready=False)
    except Exception as e:
        print("AUTH_USER_MODEL_GOV not found in settings")






# custom auth for normal user
class CustomAuthenticationNormalUser(BaseAuthentication):

    def __init__(self):
        """
        authentication should be perform in the Normal user Table
        """
        self.user_model = get_normaluser_model()
        
    def authenticate(self, request):
        """
        """
        email = request.data.get('email')
        if not email:
            return Response({"details":"email not provided"}, status=403)
        user = self.user_model.objects.get(email = request.data.get("email"))



# cutom auth for gov
class CustomAuthenticationGovUser(BasicAuthentication):

    def __init__(self):
        """
        authentication should be perform in the Gov user Table
        """
        self.user_model = get_govuser_model()

    def authenticate(self, request):
        pass