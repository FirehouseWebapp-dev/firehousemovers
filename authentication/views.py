from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import login
from django.views.generic import FormView
from django.contrib import messages
from django.views import View
from authentication.forms import EmailAuthenticationForm, SignUpForm, AddTeamMemberForm, DepartmentForm
from django.db.models import Q
from .models import UserProfile, User, Department
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
from .forms import ProfileUpdateForm, TeamMemberEditForm
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.db import transaction

# Helper function for permission
def is_manager_or_admin(user):
    return hasattr(user, "userprofile") and (
        user.is_superuser or user.userprofile.is_manager or user.userprofile.is_admin or user.userprofile.is_senior_management
    )


def can_manage_departments(user):
    # Keep this consistent with DepartmentForm manager queryset (manager role only)
    if hasattr(user, "userprofile"):
        return user.is_superuser or user.userprofile.role in ["ceo", "vp", "llc/owner", "admin", "manager"]
    return False


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

    http_method_names = ["get", "post", "options"]
    template_name = "react_landing.html"  # Use React landing page template
    extra_context = None

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Logout may be done via GET."""
        auth_logout(request)
        # Force redirect to home page with cache-busting to show React landing page
        response = HttpResponseRedirect("/")
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

    def post(self, request, *args, **kwargs):
        """Logout may be done via POST."""
        auth_logout(request)
        # Force redirect to home page with cache-busting to show React landing page
        response = HttpResponseRedirect("/")
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

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

    if user_profile.role in ["manager", "admin"] or user_profile.is_senior_management:
        team_members = UserProfile.objects.filter(manager=user_profile)
        # Only apply role filter if not senior management
        if selected_role and not user_profile.is_senior_management:
            team_members = team_members.filter(role=selected_role)
    else:
        team_members = []

    roles = UserProfile.EMPLOYEE_CHOICES

    return render(request, "authentication/team_view.html", {
        "team_members": team_members,
        "roles": roles,
        "selected_role": selected_role,
        "is_senior_management": user_profile.is_senior_management,
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
def edit_team_member(request, user_id):
    user_profile = get_object_or_404(UserProfile, user_id=user_id)

    # Ensure only managers or admins can edit
    if request.user.userprofile != user_profile.manager and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to edit this profile.")

    if request.method == "POST":
        form = TeamMemberEditForm(request.POST, instance=user_profile, current_user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Team member updated.")
            return redirect("authentication:team")
    else:
        form = TeamMemberEditForm(instance=user_profile, current_user=request.user)

    return render(request, "authentication/edit_team_member.html", {
        "form": form,
        "team_member": user_profile
    })
   
@login_required
def department_view(request):
    departments = (
        Department.objects
        .select_related('manager__user')
        .prefetch_related('members__user')
        .order_by('title')
    )
    return render(request, "authentication/department.html", {"departments": departments})

@login_required
@user_passes_test(can_manage_departments)
@transaction.atomic
def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()  # includes title/description/manager

            # Assign employees
            selected_employees = form.cleaned_data.get("employees") or []
            UserProfile.objects.filter(id__in=[e.id for e in selected_employees]).update(department=department)

            messages.success(request, f'Department "{department.title}" added successfully!')
            return redirect("authentication:department")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = DepartmentForm()

    return render(request, "authentication/add_department.html", {"form": form})
    
@login_required
@user_passes_test(can_manage_departments)
@transaction.atomic
def edit_department(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()

            # Clear current employees of this dept
            UserProfile.objects.filter(department=department).update(department=None)

            # Re-assign selected employees
            selected_employees = form.cleaned_data.get('employees') or []
            UserProfile.objects.filter(id__in=[e.id for e in selected_employees]).update(department=department)

            messages.success(request, f'Department "{department.title}" updated successfully!')
            return redirect("authentication:department")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = DepartmentForm(instance=department)

    return render(request, "authentication/edit_department.html", {
        "form": form,
        "department": department,
    })

@login_required
@user_passes_test(can_manage_departments)
@transaction.atomic
def remove_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        # Unassign members before delete to avoid dangling FKs
        UserProfile.objects.filter(department=department).update(department=None)
        department.delete()
        messages.success(request, f"Department '{department.title}' removed successfully.")
        return redirect("authentication:department")
    return redirect("authentication:department")

@login_required
def get_department_employees(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    members = department.members.select_related("user").all()
    member_data = [
        {
            "name": (m.user.get_full_name() or m.user.username),
            "link": reverse('authentication:view_profile', args=[m.user.id])
        }
        for m in members
    ]
    return JsonResponse({"employees": member_data})


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
