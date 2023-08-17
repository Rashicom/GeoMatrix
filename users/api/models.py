from django.db import models

from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.utils.translation import gettext_lazy as _

# overriding usermanager
class CustomUserManager(BaseUserManager):

    # overriding user based authentication methord to email base authentiction
    def _create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError("The given mail must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)


    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)



# custom customer for user
# extrafields are added to by inheriting the django user
class CustomUser(AbstractUser):

    # field doesnot needed
    username = None

    # extra fields
    email = models.EmailField(unique=True)
    adhar_id = models.CharField(max_length=10, unique=True)
    contact_number = models.CharField(max_length=12)
    profile_photo = models.ImageField(upload_to="Profile_photos", null=True, blank=True)
    social_rank = models.FloatField(default=2.5)
    user_otp = models.CharField(max_length=5, blank=True, null=True)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()



# address
# referencing user one to one reation
class Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=50)
    locality = models.CharField(max_length=20)
    district = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zipcode = models.CharField(max_length=10)
    country = models.CharField(max_length=20, default="INDIA")



# users wallet
# one to one relation with user
class Wallet(models.Model):
    wallet_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)


# one to many relation with wallet
class Wallet_transaction(models.Model):
    # choices
    class wallet_transaction_type_chices(models.TextChoices):
        DEPOSIT = "DEPOSIT"
        WITHDRAWAL = "WITHDRAWAL"

    wallet_transaction_id = models.AutoField(primary_key=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    wallet_transaction_type = models.CharField(
        max_length=50, choices=wallet_transaction_type_chices.choices
    )
    wallet_transaction_date = models.DateField(auto_now_add=True)
    wallet_transaction_status = models.BooleanField(default=True)
    wallet_transaction_amount = models.IntegerField()


"//////////////////////////  Gov_body_user  ////////////////////////////////"

"""
this is a user model for gov_body inherit from the Abstract user model
gov users have differect wallet accouts and transaction to recive transactions from the normal users

*Roles
gov_users can have 3 rols: locality, district, state
Role permission hierarchy: super_user > state > district > locality

locality gov_users can have the permission over user and lands registered inside the locality
district gov_users can have the permission over user and lands registered inside the district
state gov_users can have the permission over user and lands registered inside the state 

"""

# custom customer for user
# extrafields are added to by inheriting the django user
class Gov_body_user(AbstractUser):

    # field doesnot needed
    username = None
    first_name = None
    last_name = None
    
    # extra fields
    email = models.EmailField(unique=True,
        error_messages={
            "unique": _("A user with that username already exists."),
        },)
    gov_body_name = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=12)
    profile_photo = models.ImageField(upload_to="Govuser_Profile_photos", null=True, blank=True)
    user_otp = models.CharField(max_length=5, blank=True, null=True)

    # many to many field to  default groups and permission tables with defferent related_name argumets
    # helps to avoiding conflict with the Customuser, becouse both Custome user and gov_body_user inherit Abstract user
    groups = models.ManyToManyField(Group, verbose_name=_("groups"), blank=True, related_name="gov_body_set")
    user_permissions = models.ManyToManyField(Permission, verbose_name=_("user permissions"), blank=True, related_name="gov_body_set")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()



# Gov body address
# referencing user one to one reation
class Gov_body_Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    gov_body = models.OneToOneField(Gov_body_user, on_delete=models.CASCADE)
    locality = models.CharField(max_length=20)
    district = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    country = models.CharField(max_length=20, default="INDIA")


# gov_user wallet
# one to one relation with user
class Gov_body_wallet(models.Model):
    wallet_id = models.AutoField(primary_key=True)
    Gov_body = models.OneToOneField(Gov_body_user, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)


# one to many relation with wallet
class Gov_body_wallet_transaction(models.Model):
    # choices
    class wallet_transaction_type_chices(models.TextChoices):
        DEPOSIT = "DEPOSIT"
        WITHDRAWAL = "WITHDRAWAL"

    wallet_transaction_id = models.AutoField(primary_key=True)
    wallet = models.ForeignKey(Gov_body_wallet, on_delete=models.CASCADE)
    wallet_transaction_type = models.CharField(
        max_length=50, choices=wallet_transaction_type_chices.choices
    )

    wallet_transaction_date = models.DateField(auto_now_add=True)
    wallet_transaction_status = models.BooleanField(default=True)
    wallet_transaction_amount = models.IntegerField()