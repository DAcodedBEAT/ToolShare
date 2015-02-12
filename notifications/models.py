from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.utils import timezone
from ToolShare.models import Checkout


class NotificationManager(models.Manager):

    def inbox_for(self, user):
        """
        Returns all notifications received by the given user.
        """
        return self.filter(recipient=user)

    def unread_for(self, user):
        """
        Returns all unread notifications received by the given user.
        """
        return self.filter(recipient=user, viewed=False)

    def checkout_for(self, user):
        """
        Returns all  checkout notifications received by the given user.
        """
        return self.filter(recipient=user, checkout__isnull=False)

    def unread_checkout_for(self, user):
        """
        Returns all unread checkout notifications received by the given user.
        """
        return self.filter(recipient=user, checkout__isnull=False, viewed=False)

    def outbox_for(self, user):
        """
        Returns all messages that were sent by the given user.
        """
        return self.filter(sender=user)


class Notification(models.Model):
    title = models.CharField(max_length=256)
    message = models.TextField()
    viewed = models.BooleanField(default=False)
    sender = models.ForeignKey(User, blank=True, null=True, related_name="n_sender")
    recipient = models.ForeignKey(User, related_name="n_recipient")
    checkout = models.ForeignKey(Checkout, blank=True, null=True, related_name="n_checkout")
    sent_date = models.DateTimeField(default=lambda: timezone.localtime(timezone.now()))
    objects = models.Manager()
    notif_objects = NotificationManager()

    def __str__(self):
        return self.title + " ( " + str(self.recipient.username) + " [" + str(self.id) + "] )"

    class Meta:
        ordering = ['-sent_date']
        verbose_name = "notification"
        verbose_name_plural = "notifications"


def inbox_count_for(user):
    """
    Returns the number of unread notifications for the given user.
    """
    return Notification.objects.filter(recipient=user, viewed=False).count()


@receiver(post_save, sender=User)
def create_welcome_message(sender,**kwargs):
    """
    Creates a welcome notification for every new user.
    """
    if kwargs.get('created', False):
        Notification.objects.create(recipient=kwargs.get('instance'),
                                    title="Welcome to ToolShare!",
                                    message="Thanks for signing up!")