from .models import Gov_body_user
from django.contrib.auth.hashers import make_password

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
        user = Gov_body_user.objects.get(email=email)
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



