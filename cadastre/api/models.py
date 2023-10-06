# from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.geos import point
from datetime import date
from django.db.models import Q



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
class NormalUser(AbstractUser):

    # field doesnot needed
    username = None

    # extra fields
    email = models.EmailField(unique=True)
    adhar_id = models.CharField(max_length=10, unique=True)
    contact_number = models.CharField(max_length=12)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()



class Land(models.Model):

    land_number = models.AutoField(primary_key=True)
    
    # preventing delete user if any land exist for the user
    user = models.ForeignKey(NormalUser, on_delete=models.PROTECT)
    
    # self join to find out which land is splited to form the new land
    parent_land_id = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    
    locality = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)

    # active form is actually the registration date
    # active from and till gives the timespan of a perticular property
    active_from = models.DateField(auto_now_add=True)
    active_till = models.DateField(default=None, blank=True, null=True)
    
    # if a property is splited to multiple properties, this became the parent property of it, and set is_acitve state to false
    # after split set to false becouse the property doesnt no longer exist and other services like tax, data genaration models doesnt include this property
    is_active = models.BooleanField(default=True)

    

class LandOwnershipRegistry(models.Model):
    """
    keep tracking the owners  of the land.
    one land can go through many users. this info keep tracked be the registry
    """
    user = models.ForeignKey(NormalUser, on_delete=models.PROTECT)
    land = models.ForeignKey(Land, on_delete=models.CASCADE)
    registration_date = models.DateField(auto_now_add=True)



# land geography
class LandGeography(models.Model):
    class Choices(models.TextChoices):
        RESIDENTIAL = "RESIDENTIAL"
        AGRICULTURAL = "AGRICULTURAL"
        COMMERCIAL = "COMMERCIAL"
        INDUSTRIAL = "INDUSTRIAL"
        TRANSPORT = "TRANSPORT"
        RECREATIONAL = "RECREATIONAL"
        INVESTMENT = "INVESTMENT"
        ECOSENSITIVE = "ECOSENSITIVE"
        FOREST = "FOREST"
        WET = "WET"
        RANGE = "RANGE"
        BARREN = "BARREN"


    land = models.OneToOneField(Land,related_name="land_geography" ,on_delete=models.CASCADE)
    land_type = models.CharField(max_length=20, choices=Choices.choices)
    location_coordinate = models.PointField()
    boundary_polygon = models.PolygonField()
    # slop
    area = models.FloatField()


# land tax invoice
class TaxInvoice(models.Model):
    tax_invoice_id = models.AutoField(primary_key=True)

    land = models.ForeignKey(Land, on_delete=models.CASCADE)
    registry_user = models.ForeignKey(LandOwnershipRegistry, on_delete=models.CASCADE)
    area = models.IntegerField()
    amount = models.IntegerField()
    tax_date = models.DateField(auto_now_add=True)
    
    # True if the invoice not paide still active, false invoice is paid and closed
    # status set to False if the invoice amount completely paide, calculated from invoice payment table
    is_active = models.BooleanField(default=True)


# diferent land have differenct land taxes
class LandTypeTaxList(models.Model):

    class Choices(models.TextChoices):
        RESIDENTIAL = "RESIDENTIAL"
        AGRICULTURAL = "AGRICULTURAL"
        COMMERCIAL = "COMMERCIAL"
        INDUSTRIAL = "INDUSTRIAL"
        TRANSPORT = "TRANSPORT"
        RECREATIONAL = "RECREATIONAL"
        INVESTMENT = "INVESTMENT"
        ECOSENSITIVE = "ECOSENSITIVE"
        FOREST = "FOREST"
        WET = "WET"
        RANGE = "RANGE"
        BARREN = "BARREN"

    land_type = models.CharField(max_length=20, choices=Choices.choices, unique=True)
    land_tax = models.IntegerField()



class TaxInvoicePayment(models.Model):
    tax_payment_id = models.AutoField(primary_key=True)

    tax_invoice = models.ForeignKey(TaxInvoice, on_delete=models.CASCADE)
    payed_amount = models.IntegerField()
    payment_date = models.DateField(auto_now_add=True)



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
class GovbodyUser(AbstractUser):

    # field doesnot needed
    username = None
    first_name = None
    last_name = None
    
    # extra fields
    class Role(models.TextChoices):
        LOCAL = "LOCAL"
        DISTRICT = "DISTRICT"
        STATE = "STATE"

    role = models.CharField(max_length=20, choices=Role.choices)
    email = models.EmailField(unique=True,
        error_messages={
            "unique": _("A user with the same email already exists."),
        },)
    gov_body_name = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=12)
    
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
    gov_body = models.OneToOneField(GovbodyUser, on_delete=models.CASCADE)
    locality = models.CharField(max_length=20)
    district = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    country = models.CharField(max_length=20, default="INDIA")







# # gov user
# class GovbodyUser(models.Model):
    
#     # extra fields
#     class Role(models.TextChoices):
#         LOCAL = "LOCAL"
#         DISTRICT = "DISTRICT"
#         STATE = "STATE"

#     role = models.CharField(max_length=20, choices=Role.choices)
#     email = models.EmailField(unique=True,
#         error_messages={
#             "unique": _("A user with the same email already exists."),
#         },)
#     gov_body_name = models.CharField(max_length=50)
#     contact_number = models.CharField(max_length=12)



