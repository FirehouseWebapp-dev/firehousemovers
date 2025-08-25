from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import login
from django.views.generic import FormView
from django.contrib import messages
from django.views import View
from authentication.forms import EmailAuthenticationForm, SignUpForm, AddTeamMemberForm
from django.db.models import Q
from .models import UserProfile, User, Goal
from django.contrib.auth import logout as auth_logout
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login as auth_login
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ProfileUpdateForm, TeamMemberEditForm, GoalForm
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms import modelformset_factory
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST

# Define the formset for Goal model
GoalFormSet = modelformset_factory(Goal, form=GoalForm, extra=1, can_delete=True)

# Helper function for permission
def is_manager_or_admin(user):
    if not hasattr(user, "userprofile"):
        return False
    return user.userprofile.role in ["manager", "admin"]


class SignUpView(View):

    def get(self, request):
        form = SignUpForm()
        return render(request, "signup.html", {"form": form})

    def post(self, request):
        form = SignUpForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            email = form.cleaned_data.get("email")
            profile_pic = form.cleaned_data.get("profile_picture")

            # ✅ Check if user already exists (correct model)
            if User.objects.filter(email=email).exists():
                messages.error(
                    request, "Email already exists. Please choose another one."
                )
                return render(request, "signup.html", {"form": form})

            # ✅ Generate a unique username
            if first_name:
                existing_user_count = User.objects.filter(
                    username__startswith=first_name.lower()
                ).count()
                user_name = f"{first_name.lower()}{existing_user_count + 1}"
            else:
                user_name = email.split("@")[0]

            # ✅ Save user
            user = form.save(commit=False)
            user.username = user_name
            user.set_password(form.cleaned_data["password1"])
            user.save()

            # ✅ Create user profile
            user_profile = user.userprofile
            user_profile.profile_picture = profile_pic
            user_profile.save()

            # ✅ Log in and redirect
            login(request, user)
            messages.success(request, "You have successfully signed up!")
            return redirect("authentication:profile")


        # ❌ If form is invalid
        print("Form errors:", form.errors)
        return render(request, "signup.html", {"form": form})


class RedirectURLMixin:
    next_page = None
    redirect_field_name = REDIRECT_FIELD_NAME
    success_url_allowed_hosts = set()

    def get_success_url(self):
        return self.get_redirect_url() or self.get_default_redirect_url()

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name, self.request.GET.get(self.redirect_field_name)
        )
        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ""

    def get_success_url_allowed_hosts(self):
        return {self.request.get_host(), *self.success_url_allowed_hosts}

    def get_default_redirect_url(self):
        """Return the default redirect URL."""
        if self.next_page:
            return resolve_url(self.next_page)
        return "/"


class LoginView(RedirectURLMixin, FormView):
    """
    Display the login form and handle the login action.
    """

    form_class = EmailAuthenticationForm
    authentication_form = None
    template_name = "login.html"
    redirect_authenticated_user = False
    extra_context = None

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:

            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def get_default_redirect_url(self):
        """Return the default redirect URL."""
        if self.next_page:
            return resolve_url(self.next_page)
        else:
            return resolve_url("/")

    def get_form_class(self):
        return self.authentication_form or self.form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        messages.success(self.request, "Login successful!")
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_site = get_current_site(self.request)
        context.update(
            {
                self.redirect_field_name: self.get_redirect_url(),
                "site": current_site,
                "site_name": current_site.name,
                **(self.extra_context or {}),
            }
        )
        return context


class LogoutView(RedirectURLMixin, TemplateView):
    """
    Log out the user and display the 'You are logged out' message.
    """

    http_method_names = ["post", "options"]
    template_name = "home.html"
    extra_context = None

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Logout may be done via POST."""
        auth_logout(request)
        redirect_to = self.get_success_url()
        if redirect_to != request.get_full_path():
            # Redirect to target page once the session has been cleared.
            return HttpResponseRedirect(redirect_to)
        return super().get(request, *args, **kwargs)

    def get_default_redirect_url(self):
        """Return the default redirect URL."""
        if self.next_page:
            return resolve_url(self.next_page)
        else:
            return resolve_url("/")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_site = get_current_site(self.request)
        context.update(
            {
                "site": current_site,
                "site_name": current_site.name,
                "title": _("Logged out"),
                "subtitle": None,
                **(self.extra_context or {}),
            }
        )
        return context


def check_email_availability(request):
    email = request.GET.get("email", None)
    data = {"is_taken": UserProfile.objects.filter(user__email=email).exists()}
    return JsonResponse(data)



@login_required
def profile_view(request):
    user = request.user
    profile = user.userprofile
    team_members = UserProfile.objects.filter(manager=profile)

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, user=user)
        if form.is_valid():
            form.save()
            # ✅ Reload fresh data after saving
            user.refresh_from_db()
            profile = user.userprofile
            form = ProfileUpdateForm(instance=profile, user=user)  # re-init form with user
            messages.success(request, "Profile updated successfully!")
    else:
        form = ProfileUpdateForm(instance=profile, user=user)

    manager = profile.manager
    teammates = UserProfile.objects.filter(manager=manager).exclude(user=user) if manager else []

    return render(request, "authentication/profile.html", {
        "form": form,
        "profile": profile,
        "team_members": team_members,
        "teammates": teammates,
    })





@login_required
def view_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=profile_user)

    # Get team mates (same manager)
    if profile.manager:
        teammates = UserProfile.objects.filter(manager=profile.manager).exclude(user=profile_user)
    else:
        teammates = []

    # Get team members (users where this profile is their manager)
    team_members = UserProfile.objects.filter(manager=profile)

    return render(request, "authentication/view_profile.html", {
        "profile_user": profile_user,
        "profile": profile,
        "team_members": team_members,
        "teammates": teammates,
    })


from django.contrib.auth.views import PasswordChangeView
from .forms import StyledPasswordChangeForm

class CustomPasswordChangeView(PasswordChangeView):
    form_class = StyledPasswordChangeForm
    template_name = 'authentication/change_password.html'
    success_url = '/profile/'



@login_required
@user_passes_test(is_manager_or_admin)
def team_view(request):
    user_profile = request.user.userprofile
    team_members = []

    selected_role = request.GET.get("role")

    if user_profile.role in ["manager", "admin"]:
        team_members = UserProfile.objects.filter(manager=user_profile)
        if selected_role:
            team_members = team_members.filter(role=selected_role)
    else:
        team_members = []

    roles = UserProfile.EMPLOYEE_CHOICES

    return render(request, "authentication/team_view.html", {
        "team_members": team_members,
        "roles": roles,
        "selected_role": selected_role
    })

@login_required
@user_passes_test(is_manager_or_admin)
def add_team_member(request):
    if request.method == 'POST':
        form = AddTeamMemberForm(request.POST, current_user=request.user)
        if form.is_valid():
            team_member = form.cleaned_data['user']
            role = form.cleaned_data['role']

            profile = team_member.userprofile
            profile.manager = request.user.userprofile
            profile.role = role
            profile.save()

            return redirect('authentication:team')
    else:
        form = AddTeamMemberForm(current_user=request.user)

    return render(request, 'authentication/add_member.html', {'form': form})

from django.views.decorators.http import require_POST

@login_required
@user_passes_test(is_manager_or_admin)
def remove_team_member(request, user_id):
    member_profile = get_object_or_404(UserProfile, user__id=user_id)

    if member_profile.manager != request.user.userprofile:
        messages.error(request, "You do not have permission to remove this user.")
        return redirect("authentication:team")

    if request.method == "POST":
        member_profile.manager = None
        member_profile.save()
        messages.success(request, f"{member_profile.user.get_full_name()} was removed from your team.")
        return redirect("authentication:team")


@login_required
@user_passes_test(is_manager_or_admin)
def edit_team_member(request, user_id):
    user_profile = get_object_or_404(UserProfile, user__id=user_id)

    # Ensure only managers or admins can edit
    if request.user.userprofile != user_profile.manager and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to edit this profile.")

    if request.method == "POST":
        form = TeamMemberEditForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Team member profile updated successfully.")
            return redirect("authentication:team")
    else:
        form = TeamMemberEditForm(instance=user_profile)

    return render(request, "authentication/edit_team_member.html", {
        "form": form,
        "team_member": user_profile
    })

@login_required
def goals_management_view(request):
    """Main goals management page - lists all employees with goals"""
    user_profile = request.user.userprofile

    if user_profile.is_senior_management:
        employees = UserProfile.objects.filter(is_employee=True).order_by('user__first_name', 'user__last_name')
    elif user_profile.is_manager:
        employees = UserProfile.objects.filter(manager=user_profile).order_by('user__first_name', 'user__last_name')
    else:
        employees = UserProfile.objects.filter(id=user_profile.id)

    for employee in employees:
        employee.goal_count = Goal.objects.filter(assigned_to=employee).count()
        employee.has_goals = employee.goal_count > 0

    context = {
        'employees': employees,
        'can_add_goals': user_profile.is_senior_management or user_profile.is_manager,
        'has_team_members': employees.exists() if user_profile.is_manager else True,
    }

    return render(request, 'authentication/goals_management.html', context)

@login_required
@require_POST
def toggle_goal_completion_view(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)
    user_profile = request.user.userprofile

    # Permission check: Only assigned user, manager, or senior management can toggle completion
    if not (user_profile.is_senior_management or user_profile.is_manager or goal.assigned_to == user_profile):
        return JsonResponse({'success': False, 'error': 'You don\'t have permission to modify this goal.'}, status=403)

    try:
        goal.is_completed = not goal.is_completed
        goal.save()
        return JsonResponse({'success': True, 'is_completed': goal.is_completed})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def add_goals_view(request, employee_id):
    """Add goals for a specific employee"""
    user_profile = request.user.userprofile
    employee = get_object_or_404(UserProfile, id=employee_id)

    # Check permissions
    if user_profile.is_senior_management:
        pass  # Senior management can add goals for any employee
    elif user_profile.is_manager:
        if employee.manager != user_profile:
            raise PermissionDenied("You can only add goals for your direct team members.")
    else:
        raise PermissionDenied("You don't have permission to add goals.")

    # Check if employee already has 10 goals
    existing_goals_count = Goal.objects.filter(assigned_to=employee).count()
    if existing_goals_count >= 10:
        messages.error(request, f"{employee} already has the maximum of 10 goals.")
        return redirect('authentication:goals_management')

    remaining_goals = 10 - existing_goals_count

    if request.method == 'POST':
        formset = GoalFormSet(request.POST, queryset=Goal.objects.none())
        if formset.is_valid():
            with transaction.atomic():
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                        goal = form.save(commit=False)
                        goal.assigned_to = employee
                        goal.created_by = user_profile
                        goal.department = employee.department
                        goal.save()
            messages.success(request, f"Goals added successfully for {employee}.")
            return redirect('authentication:goals_management')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        formset = GoalFormSet(queryset=Goal.objects.none())

    context = {
        'employee': employee,
        'existing_goals_count': existing_goals_count,
        'remaining_goals': remaining_goals,
        'formset': formset,
    }

    return render(request, 'authentication/add_goals.html', context)


@login_required
def view_goals_view(request, employee_id):
    """View goals for a specific employee"""
    user_profile = request.user.userprofile
    employee = get_object_or_404(UserProfile, id=employee_id)

    if not (user_profile.is_senior_management or user_profile.is_manager) and user_profile.id != employee.id:
        raise PermissionDenied("You can only view your own goals.")

    goals = Goal.objects.filter(assigned_to=employee)

    # Apply goal type filter
    selected_goal_type = request.GET.get('goal_type')
    if selected_goal_type and selected_goal_type != 'all':
        goals = goals.filter(goal_type=selected_goal_type)

    goals = goals.order_by('is_completed', '-created_at') # Order by completion status then creation date

    context = {
        'employee': employee,
        'goals': goals,
        'can_edit': user_profile.is_senior_management or user_profile.is_manager,
        'selected_goal_type': selected_goal_type,
    }

    return render(request, 'authentication/view_goals.html', context)


@login_required
def edit_goal_view(request, goal_id):
    """Edit a specific goal"""
    user_profile = request.user.userprofile
    goal = get_object_or_404(Goal, id=goal_id)

    if not (user_profile.is_senior_management or user_profile.is_manager):
        raise PermissionDenied("You don't have permission to edit goals.")

    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, "Goal updated successfully.")
            return redirect('authentication:view_goals', employee_id=goal.assigned_to.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = GoalForm(instance=goal)

    context = {
        'goal': goal,
        'form': form,
    }

    return render(request, 'authentication/edit_goal.html', context)

@login_required
def remove_goal_view(request, goal_id):
    """Remove a specific goal"""
    goal = get_object_or_404(Goal, id=goal_id)
    user_profile = request.user.userprofile

    # Only senior management or the creator can delete
    if not (user_profile.is_senior_management or goal.created_by == user_profile):
        raise PermissionDenied("You don't have permission to remove this goal.")

    if request.method == 'POST':
        goal.delete()
        messages.success(request, "Goal removed successfully.")
        return redirect('authentication:goals_management')

    return redirect('authentication:goals_management')  # Fallback
