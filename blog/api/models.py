from django.contrib.gis.db import models

# Create your models here.

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


"--------------------  Gov_body_user  ----------------------------------"

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
class GovBodyUser(AbstractUser):

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
# referencing user one to one reltion
class GovBodyAddress(models.Model):
    address_id = models.AutoField(primary_key=True)
    gov_body = models.OneToOneField(GovBodyUser, on_delete=models.CASCADE)
    locality = models.CharField(max_length=20)
    district = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    country = models.CharField(max_length=20, default="INDIA")





"-------------------------  BLOGS  ---------------------------------"
# blogs
class Blogs(models.Model):
    blog_number = models.AutoField(primary_key=True)
    blogger = models.ForeignKey(GovBodyUser, on_delete=models.CASCADE)

    blog_image = models.ImageField(upload_to="blog_images")
    blog_descripton = models.TextField()
    blog_date = models.DateField(auto_now_add=True)
    is_vote = models.BooleanField(default=False)



class VoteReaction(models.Model):
    class Reaction(models.TextChoices):
        STRONGLY_SUPPORT = "STRONGLY_SUPPORT"
        SUPPORT = "SUPPORT"
        MODERATE = "MODERATE"
        DISAGREE = "DISAGREE"
        STRONGLY_DISAGREE = "STRONGLY_DISAGREE"

    blog_number = models.ForeignKey(Blogs,related_name='vote_reactions' , on_delete=models.CASCADE)
    voter = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=50, choices=Reaction.choices)
    voted_date = models.DateField(auto_now=True)



class BlogReaction(models.Model):

    blog_number = models.ForeignKey(Blogs,related_name='blog_reactions', on_delete=models.CASCADE)
    user = models.ForeignKey(NormalUser, on_delete=models.CASCADE)

    # true = liked
    # false = unliked
    # no records if not both like and unlike
    like = models.BooleanField(default=True)
    like_date = models.DateField(auto_now=True)



# blog comments
class Comments(models.Model):

    blog_number = models.ForeignKey(Blogs, related_name="comment_set", on_delete=models.CASCADE)
    commenter = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name='replay_set',blank=True,null=True)

    comment_text = models.TextField()
    comment_date = models.DateField(auto_now=True)

    class Meta:
        ordering = ['comment_date']
