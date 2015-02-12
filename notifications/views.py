from django.core.context_processors import csrf
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render_to_response, get_object_or_404, RequestContext

from notifications.models import Notification
from notifications.forms import ComposeNotification
from ToolShare.models import Checkout
from accounts.models import Locations


@login_required
def inbox(request):
    """
    Displays a list of received notifications for the current user.
    """
    notif_list = Notification.notif_objects.inbox_for(request.user)
    return render_to_response('notifications/view_notifs.html', {
        'notif_list': notif_list, 'Full_Name': request.user.first_name + " " + request.user.last_name,
        'Page_Title': "Inbox"
    }, context_instance=RequestContext(request))


@login_required
def unread_inbox(request):
    """
    Displays a list of unread received notifications for the current user.
    """
    notif_list = Notification.notif_objects.unread_for(request.user)
    return render_to_response('notifications/view_notifs.html', {
        'notif_list': notif_list, 'Full_Name': request.user.first_name + " " + request.user.last_name,
        'Page_Title': "Unread"
    }, context_instance=RequestContext(request))


@login_required
def unread_checkout(request):
    """
    Displays a list of unread received checkouts for the current user.
    """
    notif_list = Notification.notif_objects.unread_checkout_for(request.user)
    return render_to_response('notifications/view_notifs.html', {
        'notif_list': notif_list, 'Full_Name': request.user.first_name + " " + request.user.last_name,
        'Page_Title': "Unread Checkout"
    }, context_instance=RequestContext(request))


@login_required
def checkout_inbox(request):
    """
    Displays a list of received checkouts for the current user.
    """
    notif_list = Notification.notif_objects.checkout_for(request.user)
    return render_to_response('notifications/view_notifs.html', {
        'notif_list': notif_list, 'Full_Name': request.user.first_name + " " + request.user.last_name,
        'Page_Title': "Checkout"
    }, context_instance=RequestContext(request))


@login_required
def outbox(request):
    """
    Displays a list of sent notifications from the current user.
    """
    notif_list = Notification.notif_objects.outbox_for(request.user)
    return render_to_response('notifications/view_notifs.html', {
        'notif_list': notif_list, 'Full_Name': request.user.first_name + " " + request.user.last_name,
        'Page_Title': "Sent"
    }, context_instance=RequestContext(request))


@login_required
def show_notif(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id)
    if (notif.recipient != request.user) and (notif.sender != request.user):
        messages.error(request, "You cannot access the requested notification!")
        return redirect('notifications.views.inbox')
    notif.viewed = True
    notif.save()
    return render_to_response('notifications/show_notif.html',
                              {'notification': notif}, context_instance=RequestContext(request))


@login_required
def viewed_notif(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id)
    if notif.recipient != request.user:
        messages.error(request, "You cannot change the state of this message!")
        return redirect('accounts.views.my_account')
    notif.viewed = True
    notif.save()
    messages.success(request, "Changed message state to read.")
    return redirect('notifications.views.inbox')


@login_required
def not_viewed_notif(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id)
    if notif.recipient != request.user:
        messages.error(request, "You cannot change the state of this message!")
        return redirect('accounts.views.my_account')
    notif.viewed = False
    notif.save()
    messages.success(request, "Changed message state to unread.")
    return redirect('notifications.views.inbox')


@login_required
def delete_notif(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id)
    if notif.recipient != request.user:
        messages.error(request, "You cannot delete this message!")
        return redirect('accounts.views.my_account')
    notif.delete()
    if len(Notification.objects.filter(id=notif_id)) != 0:
        messages.error(request, "Notification did not delete!")
        return redirect('notifications.views.show_notif', id=notif_id)
    messages.success(request, "Deleted Notification")
    return redirect('notifications.views.inbox')


@login_required
def approve_checkout(request, cid=None):
    checkout = get_object_or_404(Checkout, cid=cid)
    if checkout.uid != request.user:
        messages.error(request, "You cannot approve this checkout!")
        return redirect('accounts.views.my_account')
    if checkout.approved is True:
        messages.warning(request, "This checkout doesn't require further action!")
        return redirect('accounts.views.my_account')
    checkout.approved = True
    checkout.save()
    c_tool = checkout.tool
    # delete the request notification
    #notif.delete()
    #if len(Notification.objects.filter(id=notif_id)) != 0:
    #    messages.error(request, "Notification did not delete!")
    #    return redirect('notifications.views.show_notif', id=notif_id)

    # send a notification to the person requesting the tool
    messages.success(request, "Approved checkout request.")
    Notification.objects.create(recipient=checkout.uid,
                                title="Congrats! You tool checkout request has been approved!",
                                message="Your checkout request of tool \"" + c_tool.title +
                                        "\" has been approved! Please remember to return it on time!" +
                                        "\nTool Info= Tool Title: " + c_tool.title + ".  Tool ID: " + c_tool.tid + ".")
    return redirect('accounts.views.my_account')


@login_required
def deny_checkout(request, cid=None):
    checkout = get_object_or_404(Checkout, cid=cid)
    if checkout.uid != request.user:
        messages.error(request, "You cannot approve this checkout!")
        return redirect('accounts.views.my_account')
    if checkout.approved is True:
        messages.warning(request, "This checkout doesn't require further action!")
        return redirect('accounts.views.my_account')
    cid = checkout.cid
    #c_time_in = checkout.time_in
    #c_time_out = checkout.time_out
    c_tool = checkout.tool
    c_user = checkout.uid

    # delete the denied checkout
    checkout.delete()
    if len(Checkout.objects.filter(cid=cid)) != 0:
        messages.error(request, "Checkout Request did not delete!")
        return redirect('notifications.views.show_notif', id=notif_id)

    # delete the request notification
    #notif.delete()
    #if len(Notification.objects.filter(id=notif_id)) != 0:
    #    messages.error(request, "Notification did not delete!")
    #    return redirect('notifications.views.show_notif', id=notif_id)

    messages.success(request, "Denied checkout request.")
    # send a notification to the person requesting the tool
    Notification.objects.create(recipient=c_user,
                                title="Sorry! You tool checkout request has been denied.",
                                message="Your checkout request of tool \"" + c_tool.title +
                                        "\" has been rejected! For further information, please contact me, " +
                                        request.user.get_full_name() + " (" + request.user.username + ")." +
                                        #"\n\nOriginal checkout info= " +
                                        #"Time In: " + c_time_in + ", Time Out: " + c_time_out + ".  " +
                                        "\nTool Info= Tool Title: " + c_tool.title + ", Tool ID: " + c_tool.tid + ".  ")
    return redirect('accounts.views.my_account')


@login_required
def compose(request):
    """
    Composes new notification to send.
    """
    if len(Locations.objects.filter(user=request.user)) == 0:
        return redirect('accounts.views.create_profile')

    if request.method == "POST":
        compose_form = ComposeNotification(request.POST)
        if compose_form.is_valid():
            compose_form.save(request.user)
            messages.success(request, "Message successfully sent.")
            return redirect('notifications.views.inbox')
        else:
            messages.error(request, "Message failed to send.")
            return redirect('notifications.views.compose')

    else:
        compose_form = ComposeNotification()
    context = {'compose_form': compose_form}
    context.update(csrf(request))  # Add CSRF token

    return render_to_response('notifications/compose.html', context, context_instance=RequestContext(request))