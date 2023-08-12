from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


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



# main section
class main_section(models.Model):
    title = models.CharField(max_length=100)
    

class main_section_images(models.Model):
    main_section = models.ForeignKey(main_section, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=None)

class main_section_description(models.Model):
    main_section = models.ForeignKey(main_section, on_delete=models.CASCADE)
    description = models.TextField()





# about section
class about_section(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="about_section", height_field=None, width_field=None, max_length=None)
    description = models.TextField()




# product section
class product_section(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="about_section", height_field=None, width_field=None, max_length=None)
    description = models.TextField()



# service section
class service_section(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="about_section", height_field=None, width_field=None, max_length=None)
    description = models.TextField()