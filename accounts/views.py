from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, redirect, RequestContext, get_object_or_404
from django.core.context_processors import csrf

from ToolShare.models import Tool, Checkout
from notifications.models import Notification
from accounts.models import UserProfile, Locations
from accounts.forms import UserProfileCreateForm, UserProfileEditForm, UserRegisterForm, AddLocation
from accounts.com.location.query import locationQuery


@login_required
def create_profile(request):
    """
    Creates page to create a profile for a user.
    """
    if len(Locations.objects.filter(user=request.user)) != 0:
        return redirect('accounts.views.edit_profile')
    context = {}
    if request.method == 'POST':
        profile_form = UserProfileCreateForm(request.POST, request.FILES, instance=request.user.profile)
        lid = None
        loc_form = AddLocation(request.POST, request.user)
        lc = locationQuery()
        address = request.POST['address']
        address = address.strip()
        address = " ".join(address.split())
        lc.query(location=address)
        if len(Locations.objects.filter(user=request.user, address=lc.formatted_address)) > 0:
            print("Address already exists")
            messages.error(request, "This address already exists")
            return redirect('accounts.views.create_profile')
        elif loc_form.is_valid() and lc.status is True:
            lf = loc_form.save(commit=False)
            lf.user = request.user
            lf.location = lc.tostring()
            lf.address = lc.formatted_address
            lf.default = True
            lf.save()
            lid = lf.loc_id
            loc_form.save_m2m()
        else:
            messages.error(request, "Google had a problem with that address. Please check the address and try again")
            return redirect('accounts.views.create_profile')
        loc = Locations.objects.get(loc_id=lid)
        if profile_form.is_valid():
            userprofile = profile_form.save(commit=False)
            userprofile.location = loc
            userprofile.save()
            profile_form.save_m2m()
            return redirect('accounts.views.my_account')
        else:
            messages.error(request, "Profile Update failed!")
            context['profile_form'] = profile_form
            return render_to_response('accounts/edit_profile.html', context, context_instance=RequestContext(request))
    else:
        context.update(csrf(request))  # Add CSRF token
        profile_form = UserProfileCreateForm(instance=request.user.profile)
        loc_form = AddLocation()
        context['profile_form'] = profile_form
        context['loc_form'] = loc_form
        context['Title'] = "Create Profile"
        return render_to_response('accounts/edit_profile.html', context, context_instance=RequestContext(request))


@login_required
def edit_profile(request):
    """
    Creates page to edit a user's profile.
    """
    if len(Locations.objects.filter(user=request.user)) == 0:
        return redirect('accounts.views.create_profile')

    profile = get_object_or_404(UserProfile, user=request.user)
    context = {}
    if request.method == 'POST':
        profile_form = UserProfileEditForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('accounts.views.my_account')
        else:
            messages.error(request, "Profile Update failed!")
            context['profile_form'] = profile_form
            return render_to_response('accounts/edit_profile.html', context, context_instance=RequestContext(request))
    else:
        profile_form = UserProfileEditForm(instance=profile)
        context.update(csrf(request))  # Add CSRF token
        context['Title'] = "Edit Profile"
        context['profile_form'] = profile_form
        return render_to_response('accounts/edit_profile.html', context, context_instance=RequestContext(request))


# User Login View
def user_login(request):
    """
    Creates page to log a user in.
    """
    if request.user.is_anonymous():  # If there is no logged in user
        if request.method == 'POST':  # If we have a post request
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')

            # This authenticates the user with given data
            user = authenticate(username=username, password=password)

            # A user was found
            if user is not None:
                # If the user has an active account, log them in
                if user.is_active:
                    login(request, user)
                    if request.GET.get('next'):
                        return HttpResponseRedirect(request.GET.get('next'))
                else:
                    messages.error(request, "Not an active account.")
                    return render_to_response('accounts/login.html', {}, context_instance=RequestContext(request))
            else:
                messages.error(request, "Wrong username/password.")
                return render_to_response('accounts/login.html', {}, context_instance=RequestContext(request))
        else:
            context = {}
            # Add the CSRF key to the data we are passing to the template
            context.update(csrf(request))
            # Render and return the template, sending it to the client
            return render_to_response('accounts/login.html', context, context_instance=RequestContext(request))
    return redirect('ToolShare.views.dashboard')  # Catch all redirect to the dashboard


# User Logout View
def user_logout(request):
    """
    Logs out the currently logged in user.
    """
    # Try and logout the user. If there is no logged in user, who cares?
    logout(request)
    messages.success(request, "You have successfully logged out!")
    return redirect('ToolShare.views.dashboard')

@login_required
def deactivate_user(request):
    """
    Deactivates the currently logged in user.
    """
    user = request.user

    # check for cases when someone cannot deactivate
    count_my_out = len(Tool.objects.filter(owner=user, status="OUT"))
    count_my_borrowing = len(Checkout.objects.filter(tool__status="OUT", uid=user))
    if count_my_out > 0:
        messages.error(request, "You cannot deactivate! " + str(count_my_out) + " of your tools are still out!")
        return redirect('accounts.views.my_account')
    if count_my_borrowing > 0:
        messages.error(request, "You cannot deactivate! You are still borrowing "+str(count_my_borrowing)+" tool(s)!")
        return redirect('accounts.views.my_account')

    # delete related instances of objects
    for tool in Tool.objects.filter(owner=user):
        # deleted checkouts associated with the tool
        for check in Checkout.objects.filter(tool=tool):
            check.delete()
        # delete the tool itself
        tool.delete()
    # delete logged in user's checkouts
    for check in Checkout.objects.filter(uid=user):
        check.delete()
    # delete notifications from inbox
    for notif in Notification.notif_objects.inbox_for(user):
        notif.delete()
    # delete logged in user's associated locations
    for loc in Locations.objects.filter(user=user):
        loc.delete()
    # delete logged in user's associated profile
    for profile in UserProfile.objects.filter(user=user):
        profile.delete()
    # actually deactivate account.
    logout(request)
    user.is_active = False
    # delete user profile
    user.delete()
    messages.success(request, "You have deleted your account. Thank you for using ToolShare!")
    return redirect('ToolShare.views.dashboard')


@login_required
def my_account(request):
    """
    Creates page to view the currently logged in user's data.
    """
    if len(Locations.objects.filter(user=request.user)) == 0:
        return redirect('accounts.views.create_profile')

    if request.method == 'POST':
        ## Do validation and updating here
        return
    else:
        user = request.user

        context = {
            'Full_Name': user.get_full_name(), 'Email': user.email,
            'Username': user.username, 'Profile': user.profile,
        }
        if Tool.objects.all() is not None:
            my_tools = Tool.objects.filter(owner=user)
            my_out_tools = Tool.objects.filter(status="OUT", owner=user)

            context['My_Tools'] = my_tools
            context['My_Out_Tools'] = my_out_tools

        context.update(csrf(request))  # Add CSRF token
        return render_to_response('accounts/my_account.html', context, context_instance=RequestContext(request))


def view_user(request, u_id=None):
    """
    Creates page to view other peoples' user-pages with basic contact and details.
    """
    if u_id is None:
        return HttpResponseRedirect("/app/browse/1")
    else:
        user = get_object_or_404(User, username=u_id)
        context = {
            'Full_Name': user.get_full_name(), 'Email': user.email,
            'Username': user.username, 'Profile': user.profile,
        }
        if Tool.objects.all() is not None:
            owner_tools = Tool.objects.filter(owner=user)
            owner_out_tools = Tool.objects.filter(status="OUT", owner=user)
            context['Owner_Tools'] = owner_tools
            context['Owner_Out_Tools'] = owner_out_tools

        return render_to_response('accounts/user_account.html', context,
                                  context_instance=RequestContext(request))


# User Register View
def user_register(request):
    """
    Creates page to register a new user.
    """
    if request.user.is_anonymous():  # If there is no logged in user
        context = {}     # Add CSRF token
        context.update(csrf(request))
        if request.method == 'POST':
            # Build the form, and validate it
            user_form = UserRegisterForm(request.POST)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "User Account Created. Please fill out profile details.")
                return redirect('accounts.views.create_profile')
            else:
                messages.error(request, "An Error has occurred.")
                context['user_form'] = user_form
                return render_to_response('accounts/register.html', context,
                                          context_instance=
                                          RequestContext(request))
        else:
            user_form = UserRegisterForm()
        context['user_form'] = user_form
        #Pass the context to a template
        return render_to_response('accounts/register.html', context, context_instance=RequestContext(request))
    else:
        return redirect('ToolShare.views.dashboard')


# TODO: Other choice in choose location
@login_required
def location(request):
    """
    Creates page to add a new location.
    """
    if not request.user.is_anonymous():
        if request.method == 'POST':
            # normalize address input
            address = request.POST['address']
            address = address.strip()
            address = " ".join(address.split())
            form = AddLocation(request.POST, request.user)
            lc = locationQuery()
            lc.query(location=address)

            if len(Locations.objects.filter(user=request.user, address=lc.formatted_address)) > 0:
                messages.error(request, "This address already exists")
            elif form.is_valid() and lc.status is True:
                lf = form.save(commit=False)
                lf.user = request.user
                lf.location = lc.tostring()
                lf.address = lc.formatted_address

                lf.save()
                form.save_m2m()
                return redirect('accounts.views.my_account')
            else:
                messages.error(request,
                               "Google had a problem with that address. Please check the address and try again")
                context = {}
                context.update(csrf(request))  # Add CSRF token
                context['form'] = form
                return render_to_response('accounts/location.html', context, context_instance=RequestContext(request))

        else:
            form = AddLocation()

        context = {}

        if request.GET.get('loc_id') and request.GET.get('action'):
            active_obj = Locations.objects.get(loc_id=request.GET.get('loc_id'))
            tools = Tool.objects.filter(location=active_obj)
            if len(tools) > 0:
                messages.error(request, "There are tools at this location. Please remove the "+str(len(tools))+
                               " tool(s) and try again.")
                return redirect('accounts.views.location')

            if request.user.profile.location == active_obj:
                messages.error(request, "You can't delete your default location.")
                return redirect('accounts.views.location')
            else:
                active_obj.delete()
                messages.success(request, "Delete OK.")
                return redirect('accounts.views.my_account')
        else:
            context['locations'] = Locations.objects.filter(user=request.user)
            if len(context['locations']) is 1:
                context['locations'] = None

        context.update(csrf(request))  # Add CSRF token
        context['form'] = form
        return render_to_response('accounts/location.html', context, context_instance=RequestContext(request))
    else:
        return HttpResponse("Please Login")