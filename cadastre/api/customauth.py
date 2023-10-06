from .models import GovbodyUser
from django.apps import apps as django_apps
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import BaseAuthentication




# govermentUserauthentication for gov user authentication
# default authentication only work for auth_user_mode in settings.py 
def authenticate_govuser(email=None,password=None):
    """
    filtering the gov_user form the data base and crossmatching the with password provided
    if user is matched returning user instance
    """

    # checking for auth credencials
    if email is None or password is None:
        raise Exception("authentication credencials where not provided")
    
    # get gov user which is matched to the provided email
    try:
        user = GovbodyUser.objects.get(email=email)
    except Exception as e:
        return None

    # if users array is not empty
    if user:

        # validating password
        if user.check_password(password):
            return user
        else:
            print("password not match")
            return None
    else:
        return None


# get the gov user model from setting.py
def get_Govuser_model():
    """
    Return the User model that is active in this project.
    """

    try:
        return django_apps.get_model(settings.AUTH_USER_MODEL_GOV, require_ready=False)
    except Exception as e:
        print("AUTH_USER_MODEL_GOV not found in settings")


# overriding jwt authentication for governmet user
class GovuserJwtAuthentication(JWTAuthentication):

    def __init__(self, *args, **kwargs):
        BaseAuthentication.__init__(self,*args, **kwargs)
        self.user_model = get_Govuser_model()
    