from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import login
from django.views.generic import FormView
from django.contrib import messages
from django.views import View
from authentication.forms import EmailAuthenticationForm, SignUpForm, AddTeamMemberForm, DepartmentForm
from django.db.models import Q
from .models import UserProfile, User, Department, DepartmentQuiz, QuizAttempt
from django.contrib.auth import logout as auth_logout
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login as auth_login
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
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
import logging
from django.templatetags.static import static

# Helper function for permission
def is_manager_or_admin(user):
    return hasattr(user, "userprofile") and (
        user.is_superuser or user.userprofile.is_manager or user.userprofile.is_admin or user.userprofile.is_senior_management
    )


def can_manage_departments(user):
    # Keep this consistent with DepartmentForm manager queryset (manager role only)
    if hasattr(user, "userprofile"):
        return (user.is_superuser or 
                user.userprofile.is_admin or 
                user.userprofile.is_senior_management or 
                user.userprofile.is_manager)
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


@login_required
def resources_training_view(request):
    """View for Resources and Training page"""
    logger = logging.getLogger(__name__)
    
    try:
        # Get user profile with department in single query
        user_profile = request.user.userprofile
        user_department = user_profile.department
        
        # Determine if user is a manager
        is_manager = user_profile.is_manager or user_profile.is_senior_management
        quiz_type = 'manager' if is_manager else 'employee'
        
        logger.info(f"Resources training accessed by {request.user.username} (role: {quiz_type}, department: {user_department})")
        
        # Training course links - All courses available at LightSpeed VT Training Center
        training_courses = [
            {"title": "Welcome Training", "url": "https://vt.lightspeedvt.com/trainingCenter/", "description": "Introduction to company culture and policies"},
            {"title": "Driver Safety", "url": "https://vt.lightspeedvt.com/trainingCenter/", "description": "Essential safety guidelines for drivers"},
            {"title": "Growth and Profit Hacks You Can Master in 35 Mins or Less", "url": "https://vt.lightspeedvt.com/trainingCenter/", "description": "Quick strategies for business growth and profitability"},
            {"title": "Mover Training", "url": "https://vt.lightspeedvt.com/trainingCenter/", "description": "Comprehensive training for moving professionals"},
            {"title": "Compliance, Legal and Claims 101", "url": "https://vt.lightspeedvt.com/trainingCenter/", "description": "Understanding legal compliance and claims processes"},
            {"title": "Marketing", "url": "https://vt.lightspeedvt.com/trainingCenter/", "description": "Marketing strategies and best practices"},
            {"title": "Leadership", "url": "https://vt.lightspeedvt.com/trainingCenter/", "description": "Develop essential leadership skills"},
            {"title": "Door to Door Sales: Moving Playbook by Lenny Gray", "url": "https://vt.lightspeedvt.com/trainingCenter/", "description": "Master door-to-door sales techniques for the moving industry"},
            {"title": "Sales Training", "url": "https://vt.lightspeedvt.com/trainingCenter/", "description": "Comprehensive sales training and techniques"},
            {"title": "Fitness", "url": "https://vt.lightspeedvt.com/trainingCenter/", "description": "Physical fitness and wellness for moving professionals"},
            {"title": "Live Coaching Skills", "url": "https://vt.lightspeedvt.com/trainingCenter/", "description": "Develop effective coaching abilities"},
            {"title": "Speaker Presentations", "url": "https://vt.lightspeedvt.com/trainingCenter/", "description": "Master the art of public speaking and presentations"},
            {"title": "Webinars and Podcasts", "url": "https://vt.lightspeedvt.com/trainingCenter/", "description": "Access to company webinars and podcast series"},
        ]
        
        # Company manuals
        company_manuals = [
            {"title": "Employee Handbook", "url": static('authentication/documents/Employee_Handbook.pdf'), "description": "Complete guide to company policies"},
        ]
        
        # Check if department has quiz questions for the user's role
        has_quiz = False
        quiz_count = 0
        if user_department:
            quiz_count = user_department.quiz_questions.filter(audience=quiz_type).count()
            has_quiz = quiz_count > 0
            logger.info(f"Quiz availability for {user_department.title}: {quiz_count} {quiz_type} questions")
        else:
            logger.info(f"No department assigned for {request.user.username}")
        
        context = {
            "training_courses": training_courses,
            "company_manuals": company_manuals,
            "user_department": user_department,
            "has_quiz": has_quiz,
            "quiz_count": quiz_count,
            "is_manager": is_manager,
            "quiz_type": quiz_type,
        }
        
        return render(request, "authentication/resources_training.html", context)
        
    except Exception as e:
        logger.error(f"Error in resources_training_view for {request.user.username}: {str(e)}")
        messages.error(request, "An error occurred while loading resources. Please try again.")
        return redirect('authentication:profile')


@login_required
def start_quiz(request):
    """Start the quiz for user's department"""
    logger = logging.getLogger(__name__)
    
    try:
        user_profile = request.user.userprofile
        user_department = user_profile.department
        
        if not user_department:
            logger.warning(f"Quiz start attempted by {request.user.username} without department assignment")
            messages.error(request, "You are not assigned to a department.")
            return redirect('authentication:resources_training')
        
        # Determine quiz type based on user role
        is_manager = user_profile.is_manager or user_profile.is_senior_management
        quiz_type = 'manager' if is_manager else 'employee'
        
        # Get quiz questions for the department and user role in single query
        questions = list(user_department.quiz_questions.filter(audience=quiz_type).order_by('order'))
        
        if not questions:
            logger.warning(f"No {quiz_type} questions found for {user_department.title} department")
            messages.error(request, f"No quiz questions available for {quiz_type}s in your department.")
            return redirect('authentication:resources_training')
        
        # Store quiz session data
        request.session['quiz_questions'] = [q.id for q in questions]
        request.session['current_question'] = 0
        request.session['quiz_answers'] = {}
        request.session['quiz_type'] = quiz_type
        
        logger.info(f"Quiz started for {request.user.username} - {user_department.title} ({quiz_type}, {len(questions)} questions)")
        
        return redirect('authentication:quiz_question')
        
    except Exception as e:
        logger.error(f"Error starting quiz for {request.user.username}: {str(e)}")
        messages.error(request, "An error occurred while starting the quiz. Please try again.")
        return redirect('authentication:resources_training')


@login_required
def quiz_question(request):
    """Display current quiz question"""
    logger = logging.getLogger(__name__)
    
    try:
        user_profile = request.user.userprofile
        user_department = user_profile.department
        
        if not user_department or 'quiz_questions' not in request.session:
            logger.warning(f"Invalid quiz access by {request.user.username} - missing department or session")
            return redirect('authentication:resources_training')
        
        question_ids = request.session.get('quiz_questions', [])
        current_index = request.session.get('current_question', 0)
        
        if current_index >= len(question_ids):
            logger.info(f"Quiz completed for {request.user.username} - redirecting to results")
            return redirect('authentication:quiz_results')
        
        # Get question in single query
        question = DepartmentQuiz.objects.get(id=question_ids[current_index])
        total_questions = len(question_ids)
        
        logger.debug(f"Quiz question {current_index + 1}/{total_questions} displayed for {request.user.username}")
        
        context = {
            'question': question,
            'current_index': current_index,
            'question_number': current_index + 1,
            'total_questions': total_questions,
            'user_department': user_department,
        }
        
        return render(request, 'authentication/quiz_question.html', context)
        
    except DepartmentQuiz.DoesNotExist:
        logger.error(f"Quiz question not found for {request.user.username} at index {current_index}")
        messages.error(request, "Quiz question not found. Please restart the quiz.")
        return redirect('authentication:resources_training')
    except Exception as e:
        logger.error(f"Error displaying quiz question for {request.user.username}: {str(e)}")
        messages.error(request, "An error occurred while loading the question. Please try again.")
        return redirect('authentication:resources_training')


@login_required
def submit_answer(request):
    """Submit answer and move to next question"""
    logger = logging.getLogger(__name__)
    
    try:
        if request.method != 'POST':
            logger.warning(f"Invalid submit_answer request method from {request.user.username}")
            return redirect('authentication:resources_training')
        
        question_id = request.POST.get('question_id')
        answer = request.POST.get('answer')
        
        if not question_id or not answer:
            logger.warning(f"Missing question_id or answer from {request.user.username}")
            messages.error(request, "Please select an answer before proceeding.")
            return redirect('authentication:quiz_question')
        
        # Store answer in session
        quiz_answers = request.session.get('quiz_answers', {})
        quiz_answers[question_id] = answer
        request.session['quiz_answers'] = quiz_answers
        
        # Move to next question
        current_index = request.session.get('current_question', 0)
        request.session['current_question'] = current_index + 1
        
        logger.debug(f"Answer submitted by {request.user.username} for question {question_id}: {answer}")
        
        return redirect('authentication:quiz_question')
        
    except Exception as e:
        logger.error(f"Error in submit_answer for {request.user.username}: {str(e)}")
        messages.error(request, "An error occurred while submitting your answer. Please try again.")
        return redirect('authentication:quiz_question')


@login_required
def quiz_results(request):
    """Display quiz results"""
    logger = logging.getLogger(__name__)
    
    try:
        user_profile = request.user.userprofile
        user_department = user_profile.department
        
        if not user_department or 'quiz_questions' not in request.session:
            logger.warning(f"Invalid quiz results access by {request.user.username}")
            return redirect('authentication:resources_training')
        
        question_ids = request.session.get('quiz_questions', [])
        quiz_answers = request.session.get('quiz_answers', {})
        quiz_type = request.session.get('quiz_type', 'employee')
        
        # Get all questions in single query to avoid N+1
        questions = DepartmentQuiz.objects.filter(id__in=question_ids)
        question_dict = {q.id: q for q in questions}
        
        # Calculate score
        score = 0
        results = []
        
        for question_id in question_ids:
            question = question_dict.get(question_id)
            if not question:
                logger.error(f"Question {question_id} not found for {request.user.username}")
                continue
                
            user_answer = quiz_answers.get(str(question_id), '')
            is_correct = user_answer == question.correct_answer
            
            if is_correct:
                score += 1
            
            results.append({
                'question': question,
                'user_answer': user_answer,
                'is_correct': is_correct,
            })
        
        total_questions = len(question_ids)
        percentage = round((score / total_questions) * 100, 1) if total_questions > 0 else 0
        
        # Save quiz attempt
        QuizAttempt.objects.create(
            user=request.user,
            department=user_department,
            score=score,
            total_questions=total_questions,
            quiz_type=quiz_type
        )
        
        # Clear quiz session
        request.session.pop('quiz_questions', None)
        request.session.pop('current_question', None)
        request.session.pop('quiz_answers', None)
        
        incorrect_count = total_questions - score
        
        logger.info(f"Quiz completed by {request.user.username} - Score: {score}/{total_questions} ({percentage}%)")
        
        context = {
            'score': score,
            'incorrect_count': incorrect_count,
            'total_questions': total_questions,
            'percentage': percentage,
            'results': results,
            'user_department': user_department,
        }
        
        return render(request, 'authentication/quiz_results.html', context)
        
    except Exception as e:
        logger.error(f"Error in quiz_results for {request.user.username}: {str(e)}")
        messages.error(request, "An error occurred while calculating your results. Please try again.")
        return redirect('authentication:resources_training')
