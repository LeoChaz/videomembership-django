from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.db.models.signals import post_save
from django.shortcuts import redirect
from django.utils import timezone


import braintree
braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id=settings.BRAINTREE_MERCHANT_ID,
                                  public_key=settings.BRAINTREE_PUBLIC_KEY,
                                  private_key=settings.BRAINTREE_PRIVATE_KEY)


from billing.models import Membership, UserMerchantID
from notifications.signals import notify


class MyUserManager(BaseUserManager):
    def create_user(self, username=None, email=None, password=None):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('Users must have a username')
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given username, email and password.
        """
        user = self.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    username = models.CharField(
        max_length=255,
        unique=True,
    )
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=120, null=True, blank=True)
    last_name = models.CharField(max_length=120, null=True, blank=True)

    is_member = models.BooleanField(default=False, verbose_name='Is Paid Member') # ex: membre payant/non-payant dans
    # modele freemium
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        # The user is identified by their email address
        return "{} {}".format(self.first_name, self.last_name)

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def __str__(self):              # __unicode__ on Python 2
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin






def user_logged_in_signal(request, sender, signal, user, **kwargs):
    request.session.set_expiry(30000)
    membership_obj, created = Membership.objects.get_or_create(user=user)
    if created:
        membership_obj.date_end = timezone.now()
        membership_obj.save()
        user.is_member = True
        user.save()
    #membership_obj.update_status()
    user.membership.update_status()


user_logged_in.connect(user_logged_in_signal)


class UserProfile(models.Model):
    user = models.OneToOneField(MyUser)
    bio = models.TextField(max_length=500, null=True, blank=True)
    facebook_profile = models.CharField(max_length=300, null=True, blank=True, verbose_name='FB Profile URL')

    def __str__(self):
        return self.user.username


def new_user_receiver(sender, instance, created, *args, **kwargs):
    if created:
        new_profile, is_created = UserProfile.objects.get_or_create(user=instance)
        #print(new_profile, is_created)
        notify.send(
                    instance,
                    recipient=MyUser.objects.get(username='leomaltrait'),   #admin user
                    verb="New user created."
                )
    try:
        merchant_obj = UserMerchantID.objects.get(user=instance)
    except:
        # Merchant account customer id -- stripe or braintree
        new_customer_result = braintree.Customer.create({
            "email": instance.email
        })
        if new_customer_result.is_success:
            merchant_obj, created = UserMerchantID.objects.get_or_create(user=instance)
            merchant_obj.customer_id = new_customer_result.customer.id
            merchant_obj.save()
            print("billing with braintree is a success. Customer ID is: {}".format(new_customer_result.customer.id))
        else:
            print("billing with braintree is a failure. Error: {}".format(new_customer_result.message))
            messages.error(request, "There was an error with your account. Please contact us. ")

        # Send email to verify user

post_save.connect(new_user_receiver, sender=MyUser)









