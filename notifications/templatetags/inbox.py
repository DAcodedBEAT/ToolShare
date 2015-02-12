from django.template import Library, Node, TemplateSyntaxError
from notifications.models import Notification, NotificationManager


class UnreadInboxOutput(Node):
    def __init__(self, var=None):
        self.var = var

    def render(self, context):
        try:
            user = context['user']
            count = 0
            if user.is_authenticated():
                count = len(Notification.notif_objects.unread_for(user=user))
        except (KeyError, AttributeError):
            count = ""
        if self.var is not None:
            context[self.var] = count
            return ""
        else:
            return "%s" % count


def unread_inbox_count(parser, token):
    """
    Creates tags to get unread messages in notifications.
    """
    args = token.contents.split()
    if len(args) > 1:
        if len(args) != 3:
            raise TemplateSyntaxError("unread_inbox_count tag takes either no arguments or exactly two arguments")
        if args[1] != 'as':
            raise TemplateSyntaxError("first argument to unread_inbox_count tag must be 'as'")
        return UnreadInboxOutput(args[2])
    else:
        return UnreadInboxOutput()


class InboxOutput(Node):
    def __init__(self, var=None):
        self.var = var

    def render(self, context):
        try:
            user = context['user']
            count = 0
            if user.is_authenticated():
                count = len(Notification.notif_objects.inbox_for(user=user))
        except (KeyError, AttributeError):
            count = ""
        if self.var is not None:
            context[self.var] = count
            return ""
        else:
            return "%s" % count


def inbox_count(parser, token):
    """
    Creates tags to get messages in notifications.
    """
    args = token.contents.split()
    if len(args) > 1:
        if len(args) != 3:
            raise TemplateSyntaxError("inbox_count tag takes either no arguments or exactly two arguments")
        if args[1] != 'as':
            raise TemplateSyntaxError("first argument to inbox_count tag must be 'as'")
        return InboxOutput(args[2])
    else:
        return InboxOutput()


class OutboxOutput(Node):
    def __init__(self, var=None):
        self.var = var

    def render(self, context):
        try:
            user = context['user']
            count = 0
            if user.is_authenticated():
                count = len(Notification.notif_objects.outbox_for(user=user))
        except (KeyError, AttributeError):
            count = ""
        if self.var is not None:
            context[self.var] = count
            return ""
        else:
            return "%s" % count


def outbox_count(parser, token):
    """
    Creates tags to get messages in notifications.
    """
    args = token.contents.split()
    if len(args) > 1:
        if len(args) != 3:
            raise TemplateSyntaxError("outbox_count tag takes either no arguments or exactly two arguments")
        if args[1] != 'as':
            raise TemplateSyntaxError("first argument to outbox_count tag must be 'as'")
        return OutboxOutput(args[2])
    else:
        return OutboxOutput()


class UnreadCheckoutOutput(Node):
    def __init__(self, var=None):
        self.var = var

    def render(self, context):
        try:
            user = context['user']
            count = 0
            if user.is_authenticated():
                count = len(Notification.notif_objects.unread_checkout_for(user=user))
        except (KeyError, AttributeError):
            count = ''
        if self.var is not None:
            context[self.var] = count
            return ""
        else:
            return "%s" % count


def unread_checkout_count(parser, token):
    """
    Creates tags to get unread checkouts in notifications.
    """
    args = token.contents.split()
    if len(args) > 1:
        if len(args) != 3:
            raise TemplateSyntaxError("unread_checkout_count tag takes either no arguments or exactly two arguments")
        if args[1] != 'as':
            raise TemplateSyntaxError("first argument to unread_checkout_count tag must be 'as'")
        return UnreadCheckoutOutput(args[2])
    else:
        return UnreadCheckoutOutput()

register = Library()
register.tag('unread_inbox_count', unread_inbox_count)
register.tag('inbox_count', inbox_count)
register.tag('outbox_count', outbox_count)
register.tag('unread_checkout_count', unread_checkout_count)