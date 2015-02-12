from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext, get_object_or_404, redirect
from django.core.context_processors import csrf
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q

from ToolShare.forms import AddToolForm, CheckInForm, OptionsForm, AddCat

# Import a necessary objects
from ToolShare.models import Tool, Checkout, Category
from notifications.models import Notification
from accounts.com.location.query import locationQuery
from accounts.models import Locations


"""
    Copyright 2014. #SWEG
"""


def generate_rating_array(tool):
    """
    Generates the appropriate boolean array for a specific tool's rating.
    """
    ratings = [False]*5
    for rates in range(0, int(tool.rating)):
        ratings[rates] = True
    return ratings


def index(request):
    return HttpResponseRedirect('/app/dashboard')


def dashboard(request):
    """
    Creates the dashboard view with relevant data to the logged in user.
    """
    if request.user.is_anonymous():  # No logged in user
        return render_to_response('index_no_user.html',
                                  context_instance=RequestContext(request))
    elif len(Locations.objects.filter(user=request.user)) == 0:
        return redirect('accounts.views.create_profile')
    else:  # Someone is logged in
        context = {}
        if Tool.objects.all() is not None:
            latest_check = Checkout.objects.all().last()
            latest_check_tool = latest_check.tool
            all_tools = Tool.objects.all()
            most_active_tool = Tool
            most_reviewed_tool = Tool
            most_active_tool_count = 0
            most_reviewed_tool_count = 0
            for curr_tool in all_tools:
                activity_tool_count = len(Checkout.objects.filter(tool=curr_tool))
                review_tool_count = len(Checkout.objects.filter(tool=curr_tool, review__isnull=False))

                if activity_tool_count > most_active_tool_count:
                    most_active_tool_count = activity_tool_count
                    most_active_tool = curr_tool
                if review_tool_count > most_reviewed_tool_count:
                    most_reviewed_tool_count = review_tool_count
                    most_reviewed_tool = curr_tool
            highly_rated_tool = all_tools.order_by('-rating')[0]
            if len(Checkout.objects.all()) != 0:
                tool_stat_dict = {'Recent Transaction': latest_check_tool, 'Most Actively Used': most_active_tool,
                                  'Most Reviewed ('+str(most_reviewed_tool_count)+' reviews)': most_reviewed_tool,
                                  'Highest Rated ('+str(highly_rated_tool.rating)+' stars)': highly_rated_tool}
                context['Tool_Stats'] = tool_stat_dict
        if User.objects.all() is not None:
            all_users = User.objects.all()
            print(all_users)
            most_active_user = None
            most_tools_user = None
            most_active_user_count = 0
            most_tools_user_count = 0
            for curr_user in all_users:
                activity_user_count = len(Checkout.objects.filter(uid=curr_user))
                tools_per_user = len(Tool.objects.filter(owner=curr_user))

                if activity_user_count > most_active_user_count:
                    most_active_user_count = activity_user_count
                    most_active_user = curr_user
                if tools_per_user > most_tools_user_count:
                    most_tools_user_count = tools_per_user
                    most_tools_user = curr_user
            recently_joined_user = all_users.order_by('-date_joined')[0]
            if most_active_user is None:
                most_active_user = request.user
            if most_tools_user is None:
                most_tools_user = request.user
            user_stat_dict = {'Most Active': most_active_user,
                              'Most Tools ('+str(most_tools_user_count)+' tools)': most_tools_user,
                              'Newest Member': recently_joined_user}
            context['User_Stats'] = user_stat_dict
        context['My_Tools'] = Tool.objects.filter(owner=request.user)
        context['My_Out_Tools'] = (Tool.objects.filter(owner=request.user, status="OUT"))
        return render_to_response('dashboard.html', context, context_instance=RequestContext(request))


def browse_tools(request, page=1):
    """
    Creates page to browse the Tools within ToolShare.
    """

    if not request.user.is_anonymous():
        loc_data = request.user.profile.location.location
    else:
        loc_data = "0,0"


    # Holds all options that we want to pass to the query
    options = {}
    # Holds the Q functions....
    filtQ = Q()

    # If we are not showing all the tools, only show the IN tools
    if request.GET.get("show_all") != "true":
        options['status'] = 'IN'

    # If we are passed a location ID, query the object and then pass that to the query
    if request.GET.get("location"):
        # TODO this might fail on its face
        lObj = Locations.objects.filter(loc_id=request.GET.get("location"))
        options['location'] = lObj

    if request.GET.get("cat_id"):
        cObj = Category.objects.filter(cat_id=request.GET.get("cat_id"))
        options['category'] = cObj


    # If we are given a text search string, make a Q object
    if request.GET.get("search"):
        filtQ = Q(title__icontains=request.GET.get("search")) | Q(description__icontains=request.GET.get("search"))

    # Query the database
    objects = Tool.objects.filter(filtQ, **options)

    ## SORTING11!!1!11!!!!!!
    if request.GET.get('sort_by') == "nearest":
        # Use python sort to sort by distance away. We are using the user's default location
        # TODO this might fail on its face if there is no user logged in
        objects = sorted(objects, key=lambda obtj: obtj.location.getDistance(loc_data))
    elif request.GET.get('sort_by') == "furthest":
        objects = sorted(objects, key=lambda obtj: obtj.location.getDistance(loc_data), reverse=True)

    # If we are passed an inter for the maximum distance
    if str(request.GET.get('distance')).isdigit() and int(request.GET.get('distance')) > 0:
        nobj = []
        for obj in objects:  # Loop through the objects, and compare the distance.
            if obj.location.compareDistance(request.user.profile.location.location, distance=float(request.GET.get('distance'))):
                nobj.append(obj)  # If the distance is less than the inputted radius
        objects = sorted(nobj, key=lambda myobj: myobj.location.getDistance(loc_data))

    '''
    paginator = Paginator(objects, 12)  # Show 12 Tools per page
    page = request.GET.get('page')
    try:
        #print("Attempt to reach page " + page)
        p_objects = paginator.page(page)
    except PageNotAnInteger:
        #messages.warning(request, "Page '" + page + "' is an invalid page number.")
        p_objects = paginator.page(1)  # If page is not an integer, deliver first page.
    except EmptyPage:
        messages.warning(request, "Page '" + page + "' is out of page bounds.")
        p_objects = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page of results.
    '''

    # We can't modify the tool object its self, so we have to build a custom object to pass to the template
    # that has the distance information.
    f_tools = []
    for m_tools in objects:
        f_tools.append([m_tools, m_tools.location.getDistance(loc_data)])
    context = {
        'Tools': f_tools,
        'MForm': OptionsForm(request.GET),
        'Catgs': Category.objects.all()
    }
    return render_to_response('browse.html', context, context_instance=RequestContext(request))


def view_tool(request, tool_id=None):
    """
    Creates page to view specified tool's page.
    """
    if tool_id is None:
        return redirect('ToolShare.views.browse_tools')
    else:
        current_tool = get_object_or_404(Tool, tid=tool_id)
        ratings = generate_rating_array(current_tool)
        checkins = Checkout.objects.filter(tool_id=current_tool, rating__isnull=False)
        context = {'Tool': current_tool, 'rating_stars': ratings, 'CheckIns': checkins}
        return render_to_response('view_tool.html', context,
                                  context_instance=RequestContext(request))


def add_tool(request):
    """
    Creates page to add a tool to ToolShare.
    """
    # The user has to be logged in to add a tool
    if not request.user.is_anonymous():
        # TODO Do this cleaner
        if len(Locations.objects.filter(user=request.user)) == 0:  # The user does not have a location in their profile
            return redirect('accounts.views.create_profile')

        if request.method == "POST":
            form = AddToolForm(request.user, request.POST, request.FILES)  # Build the form, and validate it
            # If the input is valid, and the form is M'Kay, then take apart the object, inject our own data, and put it back
            if form.is_valid():
                tool = form.save(commit=False)
                tool.owner = request.user
                tool.status = 'IN'  # TODO: explicitly define the various status states
                tool.rating = 0
                tool.save()
                #form.save_m2m()
                message = "Tool \"" + tool.title + "\" created successfully!"
                messages.success(request, message)
                Notification.objects.create(recipient=request.user,
                                            title="Tool created successfully!",
                                            message="Tool \"" + tool.title + "\" created successfully!\nTool ID: "
                                            + tool.tid + ".  ")
                return redirect('ToolShare.views.view_tool', tool_id=tool.tid)
            else:
                messages.error(request, "Tool creation failed!")
                return redirect('ToolShare.views.add_tool')  # TODO We should keep the user's data.

        else:
            form = AddToolForm(request.user)
        context = {}
        context.update(csrf(request))  # Add CSRF token
        context['form'] = form
        context['Title'] = "Edit Tool"
        return render_to_response('add_tool.html', context,
                                  context_instance=RequestContext(request))
    else:
        messages.error(request, "You are not logged in!")
        return HttpResponseRedirect('/a/login')


def edit_tool(request, tool_id=None):
    """
    Creates page to edit a specified tool.
    """
    if not request.user.is_anonymous():
        # TODO Do this cleaner
        if len(Locations.objects.filter(user=request.user)) == 0: # The user has not default location
            return redirect('accounts.views.create_profile')
        if tool_id is None:
            return redirect('ToolShare.views.browse_tools')

        tool = get_object_or_404(Tool, tid=tool_id)
        if tool.owner != request.user:
            messages.error(request, "You cannot edit tools which you do not own!")
            return redirect('ToolShare.views.browse_tools')

        form = AddToolForm(request.user, instance=tool)

        context = {}

        if request.method == "POST":
            form = AddToolForm(request.user, request.POST, request.FILES, instance=tool)
            if form.is_valid():
                form.save()
                messages.success(request, "Tool \"" + tool.title +
                                 "\" edited successfully!")
                return HttpResponseRedirect('/app/tools/'+tool.tid+'/')
            else:
                messages.error(request, "Tool edit failed!")
                context.update(csrf(request))  # Add CSRF token
                context['form'] = form
                context['Title'] = "Edit Tool"
                return render_to_response('add_tool.html', context, context_instance=RequestContext(request))

        #else:
        #    form = AddToolForm(request.user, instance=tool)
        context.update(csrf(request))  # Add CSRF token
        context['form'] = form
        context['Title'] = "Edit Tool"
        return render_to_response('add_tool.html', context, context_instance=RequestContext(request))
    else:
        messages.error(request, "You are not logged in!")
        return HttpResponseRedirect('/a/login')


@login_required
def confirm_delete_tool(request, tool_id=None):
    """
    Creates page to confirm/deny deletion of a specified tool.
    """
    if len(Locations.objects.filter(user=request.user)) == 0:
        return redirect('accounts.views.create_profile')
    if tool_id is None:
        return redirect('ToolShare.views.browse_tools')

    tool = get_object_or_404(Tool, tid=tool_id)
    if tool.owner != request.user:
            messages.error(request, "You cannot delete tools which you do not own!")
            return redirect('ToolShare.views.browse_tools')

    if tool.status == "OUT":
        messages.warning(request, "Tool cannot be deleted because it is still out!")
        return redirect('ToolShare.views.view_tool', tool_id=tool.tid)
    elif tool.owner != request.user:
        messages.error(request, "You do not have permissions to delete this tool!")
        return redirect('ToolShare.views.view_tool', tool_id=tool.tid)
    else:
        context = {'Tool': tool}
        return render_to_response('confirm_delete.html', context, context_instance=RequestContext(request))


def flag_tool(request, tool_id=None):
    """
    Creates page to delete a specified tool.
    """
    if not request.user.is_anonymous():

        # TODO Do this cleaner
        if len(Locations.objects.filter(user=request.user)) == 0:
            return redirect('accounts.views.create_profile')
        if tool_id is None:
            return redirect('ToolShare.views.browse_tools')

        current_tool = get_object_or_404(Tool, tid=tool_id)
        if current_tool.owner != request.user:
            messages.error(request, "You cannot delete tools which you do not own!")
            return redirect('ToolShare.views.browse_tools')

        if current_tool.status == "OUT":
            messages.warning(request, "Tool cannot be deleted because it is still out!")
            return redirect('ToolShare.views.view_tool', tool_id=tool_id)
        elif current_tool.owner != request.user:
            messages.error(request, "You do not have permissions to delete this tool!")
            return redirect('ToolShare.views.view_tool', tool_id=tool_id)
        else:
            title = current_tool.title
            toolid = current_tool.tid
            current_tool.delete()
            if len(Tool.objects.filter(tid=tool_id)) != 0:
                messages.error(request, "Tool did not delete!")
                return redirect('ToolShare.views.view_tool', tool_id=tool_id)
            else:
                messages.success(request, "Tool successfully deleted")
                Notification.objects.create(recipient=request.user,
                                            title="Tool deleted successfully!",
                                            message="Tool \"" + title + "\" deleted successfully!\nTool ID: "
                                            + toolid + ".  ")
                return redirect('ToolShare.views.browse_tools')
    return redirect('ToolShare.views.browse_tools')


def delete_tool(request, tool_id=None):
    """
    Creates page to delete a specified tool.
    """
    if not request.user.is_anonymous():

        # TODO Do this cleaner
        if len(Locations.objects.filter(user=request.user)) == 0:
            return HttpResponseRedirect('/a/create_profile')
        if tool_id is None:
            return redirect('ToolShare.views.browse_tools')

        current_tool = get_object_or_404(Tool, tid=tool_id)
        if current_tool.owner != request.user:
            messages.error(request, "You cannot delete tools which you do not own!")
            return redirect('ToolShare.views.browse_tools')

        if current_tool.status == "OUT":
            messages.warning(request, "Tool cannot be deleted because it is still out!")
            return redirect('ToolShare.views.view_tool', tool_id=tool_id)
        elif current_tool.owner != request.user:
            messages.error(request, "You do not have permissions to delete this tool!")
            return redirect('ToolShare.views.view_tool', tool_id=tool_id)
        else:
            title = current_tool.title
            toolid = current_tool.tid
            current_tool.delete()
            if len(Tool.objects.filter(tid=tool_id)) != 0:
                messages.error(request, "Tool did not delete!")
                return redirect('ToolShare.views.view_tool', tool_id=tool_id)
            else:
                messages.success(request, "Tool successfully deleted")
                Notification.objects.create(recipient=request.user,
                                            title="Tool deleted successfully!",
                                            message="Tool \"" + title + "\" deleted successfully!\nTool ID: "
                                            + toolid + ".  ")
                return redirect('ToolShare.views.browse_tools')
    return redirect('ToolShare.views.browse_tools')


def Ratings(tool):
    current_tool = tool
    currentcheck = Checkout.objects.get(cid=current_tool.checkout)

    if current_tool.rating == 0:
        current_tool.rating = currentcheck.rating
        print(currentcheck.rating)
        print(current_tool.rating)
        current_tool.save()
    else:
        checktool = Checkout.objects.filter(tool__tid=current_tool.tid)
        check_ratings = Checkout.objects.exclude(rating__isnull=True)
        length = len(check_ratings)
        total = 0
        for elem in check_ratings:
            total = elem.rating + total
        current_tool.rating = (total/length)
        current_tool.save()
        currentcheck.save()
    ratings = generate_rating_array(current_tool)
    return ratings


@login_required
def checkout_tool(request, tool_id):
    current_tool = get_object_or_404(Tool, tid=tool_id)
    check = Checkout()
    check.uid = request.user
    check.tool = current_tool
    if current_tool.status == "OUT":
        ## Check if the user who owns the checkout object is the current user
        if current_tool.owner != request.user:
            ## If not, fail. Fail hard.
            return HttpResponse("<pre>403. Forbidden</pre>")

        if request.method == "POST":
            form = CheckInForm(request.user, request.POST)  # Build the form, and validate it
            if form.is_valid():
                checkin = form.save(commit=False)
                checkin.tool = current_tool
                checkin.uid = check.uid
                check = checkin
                check.save()
                current_tool.checkout = check.cid
                current_tool.status = 'IN'
                current_tool.save()
                Ratings(current_tool)

                return redirect('ToolShare.views.browse_tools')
        else:
            form = CheckInForm(request.user)

        current_tool.status = "IN"
        check.time_in = timezone.now()
        context = {}
        context.update(csrf(request))  # Add CSRF token
        context['form'] = form
        #context['Title'] = "Edit Tool"
        return render_to_response('check-in.html', context, context_instance=RequestContext(request))
    else:
        if current_tool.request is False:
            current_tool.status = 'OUT'
            check.time_out = timezone.now()
    check.save()
    current_tool.checkout = check.cid
    current_tool.save()
    return redirect('ToolShare.views.browse_tools')


@login_required
def cancel_Checkout(request, tool_id):
    currentTool = Tool.objects.get(tid=tool_id)
    if currentTool.status == "OUT":
        currentTool.status = "IN"
        check = Checkout.objects.get(cid=currentTool.checkout)
        check.delete()
        currentTool.save()
    return redirect('ToolShare.views.browse_tools')


## Ah, fuck it.
def add_cat(request):
    if request.method == "POST":
        form = AddCat(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/app/add_cat')
        else:
            return HttpResponse("FAIL")
    else:
        form = AddCat()

    import pprint
    pprint.pprint(Category.objects.all())
    context = {}
    context.update(csrf(request))  # Add CSRF token
    context['Data'] = Category.objects.all()
    context['form'] = form
    return render_to_response('add_cat.html', context, context_instance=RequestContext(request))