import random, datetime
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone

from .signals import membership_dates_update
from .utils import check_membership_status, update_braintree_membership


def user_logged_in_receiver(sender, user, **kwargs):
    try:
        update_braintree_membership(user)
    except:
        pass

user_logged_in.connect(user_logged_in_receiver)


class Membership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    date_start = models.DateTimeField(default=timezone.now(), verbose_name="Start Date")
    date_end = models.DateTimeField(default=timezone.now(), verbose_name="End Date")


    def __str__(self):
        return str(self.user.username)

    def update_status(self):
        if self.date_end >= timezone.now():
            self.user.is_member = True
            self.user.save()
        else:
            self.user.is_member = False
            self.user.save()


def update_membership_status(sender, instance, created, **kwargs):
    if not created:
        instance.update_status()


post_save.connect(update_membership_status, sender=Membership)


def update_membership_dates(sender, new_date_start,  **kwargs):
    membership = sender
    current_date_end = membership.date_end
    if current_date_end >= new_date_start:
        membership.date_end = current_date_end + datetime.timedelta(days=30, hours=10)
        membership.save()
    else:
        membership.date_start = new_date_start
        membership.date_end = new_date_start + datetime.timedelta(days=30, hours=10)
        membership.save()



membership_dates_update.connect(update_membership_dates)


class TransactionManager(models.Manager):
    def create_new(self, user, transaction_id, amount, card_type, success=None, transaction_status=None,\
                   last_four=None):
        if not user:
            raise ValueError('Must be a user.')
        if not transaction_id:
            raise ValueError('Must complete a transaction.')
        new_order = "{}{}{}".format(transaction_id[:2], random.randint(100,9999), transaction_id[2:])
        new_trans = self.model(
            user=user,
            transaction_id=transaction_id,
            amount=amount,
            card_type=card_type,
            order_id=new_order
        )
        if success is not None:
            new_trans.success = success
            new_trans.transaction_status = transaction_status
        if last_four is not None:
            new_trans.last_four = last_four
        new_trans.save(using=self._db)

        return new_trans


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    transaction_id = models.CharField(max_length=120)  #Braintree or Stripe
    order_id = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    success = models.BooleanField(default=True)
    transaction_status = models.CharField(max_length=220, null=True, blank=True)
    card_type = models.CharField(max_length=120)   #or paypal
    last_four = models.PositiveIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    objects = TransactionManager()

    def __str__(self):
        return self.order_id

    class Meta:
        ordering = ["-timestamp"]

class UserMerchantID(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    customer_id =models.CharField(max_length=120)
    subscription_id =models.CharField(max_length=120, blank=True, null=True)
    plan_id =models.CharField(max_length=120, blank=True, null=True)
    merchant_name =models.CharField(max_length=120, default="Braintree")

    def __str__(self):
        return self.customer_id

