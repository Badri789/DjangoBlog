from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('User must have an email address.')
        if not username:
            raise ValueError('User must have an username.')

        user = self.model(
            email=self.normalize_email(email),
            username=username
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email,
            username=username,
            password=password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


def get_profile_image_path(instance, filename):
    return f'profile_images/user_{instance.username}/{filename}'


def get_default_profile_image():
    return 'images/default-profile-picture.jpg'


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=80, unique=True, verbose_name='Email')
    username = models.CharField(max_length=40, unique=True, verbose_name='Username')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Date joined')
    last_login = models.DateTimeField(auto_now=True, verbose_name='Last login')
    is_admin = models.BooleanField(default=False, verbose_name='Admin Status')
    is_active = models.BooleanField(default=False, verbose_name='Active Status')
    is_staff = models.BooleanField(default=False, verbose_name='Staff Status')
    is_superuser = models.BooleanField(default=False, verbose_name='Superuser Status')
    first_name = models.CharField(max_length=60, blank=True, null=True, verbose_name='First name')
    last_name = models.CharField(max_length=60, blank=True, null=True, verbose_name='Last name')
    user_info = models.TextField(validators=[MinLengthValidator(10)], max_length=300, blank=True, null=True)
    gender = models.BooleanField(blank=True, null=True, verbose_name='Gender',
                                 choices=((False, 'Female'), (True, 'Male'), (None, 'Not set')))
    profile_image = models.ImageField(upload_to=get_profile_image_path, blank=True, null=True,
                                      verbose_name='Profile Image', default=get_default_profile_image)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyAccountManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
