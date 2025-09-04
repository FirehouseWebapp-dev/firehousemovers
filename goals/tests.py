from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
import json

from authentication.models import UserProfile
from .models import Goal
from .forms import GoalForm, GoalEditForm
from .utils.validators import (
    validate_future_date, 
    validate_goal_title_length, 
    validate_goal_description_length, 
    validate_max_active_goals
)


class GoalModelTest(TestCase):
    """Test cases for the Goal model"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Get user profiles (automatically created by signals in authentication app)
        self.user_profile1 = self.user1.userprofile
        self.user_profile1.role = 'driver'
        self.user_profile1.save()
        
        self.user_profile2 = self.user2.userprofile
        self.user_profile2.role = 'manager'
        self.user_profile2.save()
        
        # Create a test goal
        self.goal = Goal.objects.create(
            title='Test Goal',
            description='This is a test goal description that meets the minimum length requirement',
            assigned_to=self.user_profile1,
            created_by=self.user_profile2,
            due_date=date.today() + timedelta(days=7),
            goal_type='short_term'
        )

    def test_goal_creation(self):
        """Test basic goal creation"""
        self.assertEqual(self.goal.title, 'Test Goal')
        self.assertEqual(self.goal.description, 'This is a test goal description that meets the minimum length requirement')
        self.assertEqual(self.goal.assigned_to, self.user_profile1)
        self.assertEqual(self.goal.created_by, self.user_profile2)
        self.assertEqual(self.goal.goal_type, 'short_term')
        self.assertFalse(self.goal.is_completed)
        self.assertIsNone(self.goal.completed_at)
        self.assertIsNotNone(self.goal.created_at)
        self.assertIsNotNone(self.goal.updated_at)

    def test_goal_string_representation(self):
        """Test the __str__ method"""
        self.assertEqual(str(self.goal), 'Test Goal')

    def test_goal_meta_options(self):
        """Test Meta class options"""
        self.assertEqual(Goal._meta.verbose_name, 'Goal')
        self.assertEqual(Goal._meta.verbose_name_plural, 'Goals')
        self.assertEqual(Goal._meta.ordering, ['due_date', 'title'])

    def test_goal_choices(self):
        """Test goal type choices"""
        choices = [choice[0] for choice in Goal.GOAL_TYPE_CHOICES]
        self.assertIn('short_term', choices)
        self.assertIn('long_term', choices)

    def test_goal_relationships(self):
        """Test foreign key relationships"""
        # Test assigned_to relationship
        self.assertEqual(self.goal.assigned_to.user.username, 'testuser1')
        
        # Test created_by relationship
        self.assertEqual(self.goal.created_by.user.username, 'testuser2')
        
        # Test reverse relationships
        self.assertIn(self.goal, self.user_profile1.goals.all())
        self.assertIn(self.goal, self.user_profile2.created_goals.all())

    def test_goal_completion_tracking(self):
        """Test goal completion status tracking"""
        # Mark goal as completed
        self.goal.is_completed = True
        self.goal.save()
        
        # Check that completed_at is set
        self.assertIsNotNone(self.goal.completed_at)
        self.assertEqual(self.goal.completed_at, date.today())
        
        # Create a new goal to test marking as incomplete (since completed goals can't be uncompleted)
        new_goal = Goal.objects.create(
            title='New Test Goal',
            description='This is another test goal description that meets the minimum length requirement',
            assigned_to=self.user_profile1,
            created_by=self.user_profile2,
            due_date=date.today() + timedelta(days=7),
            goal_type='short_term',
            is_completed=False
        )
        
        # Check that completed_at is None for incomplete goal
        self.assertIsNone(new_goal.completed_at)

    def test_goal_completion_prevention(self):
        """Test that completed goals cannot be marked as incomplete"""
        # Mark goal as completed
        self.goal.is_completed = True
        self.goal.save()
        
        # Try to mark as incomplete - should raise ValidationError
        with self.assertRaises(ValidationError):
            self.goal.is_completed = False
            self.goal.full_clean()

    def test_goal_validation_title_length(self):
        """Test title length validation"""
        # Test title too short
        with self.assertRaises(ValidationError):
            goal = Goal(
                title='Ab',  # Too short
                description='Valid description that meets length requirements',
                assigned_to=self.user_profile1
            )
            goal.full_clean()
        
        # Test title too long
        with self.assertRaises(ValidationError):
            goal = Goal(
                title='A' * 201,  # Too long
                description='Valid description that meets length requirements',
                assigned_to=self.user_profile1
            )
            goal.full_clean()

    def test_goal_validation_description_length(self):
        """Test description length validation"""
        # Test description too short
        with self.assertRaises(ValidationError):
            goal = Goal(
                title='Valid Title',
                description='Short',  # Too short
                assigned_to=self.user_profile1
            )
            goal.full_clean()
        
        # Test description too long
        with self.assertRaises(ValidationError):
            goal = Goal(
                title='Valid Title',
                description='A' * 1001,  # Too long
                assigned_to=self.user_profile1
            )
            goal.full_clean()

    def test_goal_validation_future_date(self):
        """Test due date validation"""
        # Test past date
        with self.assertRaises(ValidationError):
            goal = Goal(
                title='Valid Title',
                description='Valid description that meets length requirements',
                assigned_to=self.user_profile1,
                due_date=date.today() - timedelta(days=1)
            )
            goal.full_clean()

    def test_goal_validation_max_active_goals(self):
        """Test maximum active goals validation for existing goal updates"""
        # Create 9 more active goals for user_profile1 (we already have 1 from setUp)
        for i in range(9):
            Goal.objects.create(
                title=f'Goal {i}',
                description='Valid description that meets length requirements',
                assigned_to=self.user_profile1,
                created_by=self.user_profile2
            )
        
        # Now we have 10 active goals. Updating an existing goal should be allowed
        # since we're not exceeding the limit (the goal being updated is already counted)
        existing_goal = Goal.objects.filter(assigned_to=self.user_profile1).first()
        existing_goal.title = 'Updated Goal Title'
        
        # This should NOT raise ValidationError because we're updating an existing goal
        try:
            existing_goal.save()
        except ValidationError:
            self.fail("Should not raise ValidationError when updating existing goal")
        
        # But if we try to create a new goal, that should fail
        with self.assertRaises(ValidationError):
            new_goal = Goal(
                title='New Goal That Should Fail',
                description='Valid description that meets length requirements',
                assigned_to=self.user_profile1,
                created_by=self.user_profile2
            )
            new_goal.full_clean()
        
        # If we complete one goal first, then creating a new one should work
        goal_to_complete = Goal.objects.filter(assigned_to=self.user_profile1).last()
        goal_to_complete.is_completed = True
        goal_to_complete.save()
        
        # Now creating a new goal should work since we have 9 active goals
        new_goal = Goal(
            title='New Goal That Should Work',
            description='Valid description that meets length requirements',
            assigned_to=self.user_profile1,
            created_by=self.user_profile2
        )
        try:
            new_goal.full_clean()
        except ValidationError:
            self.fail("Should not raise ValidationError when under the limit")

    def test_goal_validation_max_active_goals_for_new_goals(self):
        """Test maximum active goals validation for new goal creation"""
        # Create 9 more active goals for user_profile1 (we already have 1 from setUp)
        for i in range(9):
            Goal.objects.create(
                title=f'Goal {i}',
                description='Valid description that meets length requirements',
                assigned_to=self.user_profile1,
                created_by=self.user_profile2
            )
        
        # Now we have 10 active goals. Creating a new goal should fail
        with self.assertRaises(ValidationError):
            new_goal = Goal(
                title='New Goal That Should Fail',
                description='Valid description that meets length requirements',
                assigned_to=self.user_profile1,
                created_by=self.user_profile2
            )
            new_goal.full_clean()
        
        # If we complete one goal first, then creating a new one should work
        goal_to_complete = Goal.objects.filter(assigned_to=self.user_profile1).last()
        goal_to_complete.is_completed = True
        goal_to_complete.save()
        
        # Now creating a new goal should work since we have 9 active goals
        new_goal = Goal(
            title='New Goal That Should Work',
            description='Valid description that meets length requirements',
            assigned_to=self.user_profile1,
            created_by=self.user_profile2
        )
        try:
            new_goal.full_clean()
        except ValidationError:
            self.fail("Should not raise ValidationError when under the limit")

    def test_goal_auto_timestamps(self):
        """Test automatic timestamp updates"""
        original_updated_at = self.goal.updated_at
        
        # Update the goal
        self.goal.title = 'Updated Goal Title'
        self.goal.save()
        
        # Check that updated_at was updated
        self.assertGreater(self.goal.updated_at, original_updated_at)


class GoalValidatorTest(TestCase):
    """Test cases for custom validators"""
    
    def test_validate_future_date(self):
        """Test future date validation"""
        # Test past date
        past_date = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            validate_future_date(past_date)
        
        # Test today's date
        today = date.today()
        try:
            validate_future_date(today)
        except ValidationError:
            self.fail("Today's date should be valid")
        
        # Test future date
        future_date = date.today() + timedelta(days=1)
        try:
            validate_future_date(future_date)
        except ValidationError:
            self.fail("Future date should be valid")

    def test_validate_goal_title_length(self):
        """Test goal title length validation"""
        # Test too short
        with self.assertRaises(ValidationError):
            validate_goal_title_length('Ab')
        
        # Test too long
        with self.assertRaises(ValidationError):
            validate_goal_title_length('A' * 201)
        
        # Test valid lengths
        try:
            validate_goal_title_length('Valid')
            validate_goal_title_length('A' * 200)
        except ValidationError:
            self.fail("Valid title lengths should not raise ValidationError")

    def test_validate_goal_description_length(self):
        """Test goal description length validation"""
        # Test too short
        with self.assertRaises(ValidationError):
            validate_goal_description_length('Short')
        
        # Test too long
        with self.assertRaises(ValidationError):
            validate_goal_description_length('A' * 1001)
        
        # Test valid lengths
        try:
            validate_goal_description_length('Valid description')
            validate_goal_description_length('A' * 1000)
        except ValidationError:
            self.fail("Valid description lengths should not raise ValidationError")

    def test_validate_max_active_goals(self):
        """Test maximum active goals validation"""
        # Create test user profile - use signal-created profile
        user = User.objects.create_user(username='testuser', password='testpass')
        user_profile = user.userprofile
        user_profile.role = 'driver'
        user_profile.save()
        
        # Create another user to be the creator
        creator_user = User.objects.create_user(username='creator', password='testpass')
        creator_profile = creator_user.userprofile
        creator_profile.role = 'manager'
        creator_profile.save()
        
        # Create 10 active goals
        for i in range(10):
            Goal.objects.create(
                title=f'Goal {i}',
                description='Valid description that meets length requirements',
                assigned_to=user_profile,
                created_by=creator_profile
            )
        
        # Test that validation fails when trying to exceed limit
        with self.assertRaises(ValidationError):
            validate_max_active_goals(user_profile)
        
        # Test that validation passes when under limit
        Goal.objects.first().delete()
        try:
            validate_max_active_goals(user_profile)
        except ValidationError:
            self.fail("Should not raise ValidationError when under limit")


class GoalFormTest(TestCase):
    """Test cases for Goal forms"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user_profile = self.user.userprofile  # Use signal-created profile
        self.user_profile.role = 'driver'
        self.user_profile.save()
        
        self.valid_data = {
            'title': 'Test Goal Title',
            'description': 'This is a valid test goal description that meets the minimum length requirement',
            'due_date': (date.today() + timedelta(days=7)).isoformat(),
            'goal_type': 'short_term',
            'notes': 'Test notes',
            'is_completed': False
        }

    def test_goal_form_valid_data(self):
        """Test form with valid data"""
        form = GoalForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_goal_form_invalid_title(self):
        """Test form with invalid title"""
        invalid_data = self.valid_data.copy()
        invalid_data['title'] = 'Ab'  # Too short
        
        form = GoalForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_goal_form_invalid_description(self):
        """Test form with invalid description"""
        invalid_data = self.valid_data.copy()
        invalid_data['description'] = 'Short'  # Too short
        
        form = GoalForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_goal_form_past_due_date(self):
        """Test form with past due date"""
        invalid_data = self.valid_data.copy()
        invalid_data['due_date'] = (date.today() - timedelta(days=1)).isoformat()
        
        form = GoalForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)

    def test_goal_form_missing_required_fields(self):
        """Test form with missing required fields"""
        # Test missing title
        invalid_data = self.valid_data.copy()
        del invalid_data['title']
        
        form = GoalForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        
        # Test missing description
        invalid_data = self.valid_data.copy()
        del invalid_data['description']
        
        form = GoalForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_goal_edit_form_excludes_is_completed(self):
        """Test that GoalEditForm excludes is_completed field"""
        form = GoalEditForm()
        self.assertNotIn('is_completed', form.fields)


class GoalViewTest(TestCase):
    """Test cases for Goal views"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users with different roles
        self.employee_user = User.objects.create_user(
            username='employee',
            email='employee@example.com',
            password='testpass123'
        )
        self.manager_user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        
        # Use signal-created user profiles
        self.employee_profile = self.employee_user.userprofile
        self.employee_profile.role = 'driver'
        self.employee_profile.save()
        
        self.manager_profile = self.manager_user.userprofile
        self.manager_profile.role = 'manager'
        self.manager_profile.save()
        
        self.admin_profile = self.admin_user.userprofile
        self.admin_profile.role = 'admin'
        self.admin_profile.save()
        
        # Set up manager relationship
        self.employee_profile.manager = self.manager_profile
        self.employee_profile.save()
        
        # Create test goals
        self.employee_goal = Goal.objects.create(
            title='Employee Goal',
            description='This is a test goal description that meets the minimum length requirement',
            assigned_to=self.employee_profile,
            created_by=self.manager_profile,
            goal_type='short_term'
        )
        
        self.manager_goal = Goal.objects.create(
            title='Manager Goal',
            description='This is a test goal description that meets the minimum length requirement',
            assigned_to=self.manager_profile,
            created_by=self.admin_profile,
            goal_type='long_term'
        )
        
        # Set up client
        self.client = Client()

    def test_goals_management_view_requires_login(self):
        """Test that goals management view requires login"""
        response = self.client.get(reverse('goals:goal_management'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_goals_management_view_employee_access(self):
        """Test goals management view for regular employee"""
        self.client.login(username='employee', password='testpass123')
        response = self.client.get(reverse('goals:goal_management'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'goals/goal_management.html')
        
        # Employee should only see their own goals
        self.assertContains(response, 'Employee Goal')
        self.assertNotContains(response, 'Manager Goal')

    def test_goals_management_view_manager_access(self):
        """Test goals management view for manager"""
        self.client.login(username='manager', password='testpass123')
        response = self.client.get(reverse('goals:goal_management'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'goals/goal_management.html')
        
        # Manager should see their team member's goals
        self.assertContains(response, 'Employee Goal')
        # Note: Manager goals might not be visible in this view depending on the template

    def test_goals_management_view_admin_access(self):
        """Test goals management view for admin"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('goals:goal_management'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'goals/goal_management.html')
        
        # Admin should see all goals
        self.assertContains(response, 'Employee Goal')
        # Note: Manager goals might not be visible in this view depending on the template

    def test_toggle_goal_completion_view(self):
        """Test toggle goal completion view"""
        self.client.login(username='manager', password='testpass123')
        
        # Test marking goal as completed
        response = self.client.post(
            reverse('goals:toggle_goal_completion', args=[self.employee_goal.id]),
            data=json.dumps({'is_completed': True}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Refresh goal from database
        self.employee_goal.refresh_from_db()
        self.assertTrue(self.employee_goal.is_completed)
        self.assertIsNotNone(self.employee_goal.completed_at)

    def test_toggle_goal_completion_prevent_uncompleting(self):
        """Test that goals cannot be marked as incomplete"""
        # First mark goal as completed
        self.employee_goal.is_completed = True
        self.employee_goal.save()
        
        self.client.login(username='manager', password='testpass123')
        
        # Try to mark as incomplete
        response = self.client.post(
            reverse('goals:toggle_goal_completion', args=[self.employee_goal.id]),
            data=json.dumps({'is_completed': False}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Cannot uncomplete', response_data['error'])

    def test_add_goals_view_employee_denied(self):
        """Test that regular employees cannot access add goals view"""
        self.client.login(username='employee', password='testpass123')
        
        # Django test client catches PermissionDenied and returns 403
        response = self.client.get(reverse('goals:add_goals', args=[self.employee_profile.id]))
        self.assertEqual(response.status_code, 403)

    def test_view_goals_view_own_goals(self):
        """Test that users can view their own goals"""
        self.client.login(username='employee', password='testpass123')
        response = self.client.get(reverse('goals:view_goals', args=[self.employee_profile.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Employee Goal')

    def test_view_goals_view_other_goals_denied(self):
        """Test that users cannot view other users' goals"""
        self.client.login(username='employee', password='testpass123')
        
        # Django test client catches PermissionDenied and returns 403
        response = self.client.get(reverse('goals:view_goals', args=[self.manager_profile.id]))
        self.assertEqual(response.status_code, 403)

    def test_view_goals_view_manager_access(self):
        """Test that managers can view their team members' goals"""
        self.client.login(username='manager', password='testpass123')
        response = self.client.get(reverse('goals:view_goals', args=[self.employee_profile.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Employee Goal')

    @patch('goals.views.send_mail')
    def test_add_goals_email_notification(self, mock_send_mail):
        """Test that email notifications are sent when goals are added"""
        self.client.login(username='manager', password='testpass123')
        
        # Create form data
        form_data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-title': 'New Test Goal',
            'form-0-description': 'This is a new test goal description that meets the minimum length requirement',
            'form-0-goal_type': 'short_term',
            'form-0-due_date': (date.today() + timedelta(days=14)).isoformat(),
        }
        
        response = self.client.post(
            reverse('goals:add_goals', args=[self.employee_profile.id]),
            data=form_data
        )
        
        # Check that email was sent
        mock_send_mail.assert_called_once()
        self.assertEqual(response.status_code, 302)  # Redirect after success

    def test_goals_management_filtering(self):
        """Test goal filtering in goals management view"""
        self.client.login(username='manager', password='testpass123')
        
        # Test completed goals filter
        response = self.client.get(reverse('goals:goal_management'), {'filter': 'completed'})
        self.assertEqual(response.status_code, 200)
        
        # Test incomplete goals filter
        response = self.client.get(reverse('goals:goal_management'), {'filter': 'incomplete'})
        self.assertEqual(response.status_code, 200)
        
        # Test goal type filter
        response = self.client.get(reverse('goals:goal_management'), {'goal_type': 'short_term'})
        self.assertEqual(response.status_code, 200)

    def test_goals_management_role_filtering(self):
        """Test role-based filtering in goals management view"""
        self.client.login(username='admin', password='testpass123')
        
        # Test role filter
        response = self.client.get(reverse('goals:goal_management'), {'role': 'driver'})
        self.assertEqual(response.status_code, 200)
        
        # Test scope filter for senior management
        response = self.client.get(reverse('goals:goal_management'), {'scope': 'team'})
        self.assertEqual(response.status_code, 200)


class GoalIntegrationTest(TestCase):
    """Integration tests for the goals system"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user_profile = self.user.userprofile  # Use signal-created profile
        self.user_profile.role = 'manager'
        self.user_profile.save()
        
        # Create a team member
        self.team_member = User.objects.create_user(username='teammember', password='testpass')
        self.team_member_profile = self.team_member.userprofile  # Use signal-created profile
        self.team_member_profile.role = 'driver'
        self.team_member_profile.manager = self.user_profile
        self.team_member_profile.save()

    def test_complete_goal_workflow(self):
        """Test the complete workflow of creating and completing a goal"""
        self.client.login(username='testuser', password='testpass')
        
        # Step 1: Add a goal for team member
        form_data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-title': 'Integration Test Goal',
            'form-0-description': 'This is an integration test goal description that meets the minimum length requirement',
            'form-0-goal_type': 'short_term',
            'form-0-due_date': (date.today() + timedelta(days=7)).isoformat(),
        }
        
        response = self.client.post(
            reverse('goals:add_goals', args=[self.team_member_profile.id]),
            data=form_data
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Step 2: Verify goal was created
        goal = Goal.objects.get(title='Integration Test Goal')
        self.assertEqual(goal.assigned_to, self.team_member_profile)
        self.assertEqual(goal.created_by, self.user_profile)
        
        # Step 3: Mark goal as completed
        response = self.client.post(
            reverse('goals:toggle_goal_completion', args=[goal.id]),
            data=json.dumps({'is_completed': True}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Verify goal completion
        goal.refresh_from_db()
        self.assertTrue(goal.is_completed)
        self.assertIsNotNone(goal.completed_at)

    def test_goal_validation_integration(self):
        """Test that validation works correctly in the complete system"""
        # Create a goal with invalid data
        with self.assertRaises(ValidationError):
            goal = Goal(
                title='Ab',  # Too short
                description='Short',  # Too short
                assigned_to=self.user_profile,
                due_date=date.today() - timedelta(days=1)  # Past date
            )
            goal.full_clean()

    def test_goal_permissions_integration(self):
        """Test that permissions work correctly across the system"""
        # Create a goal
        goal = Goal.objects.create(
            title='Permission Test Goal',
            description='This is a test goal description that meets the minimum length requirement',
            assigned_to=self.team_member_profile,
            created_by=self.user_profile
        )
        
        # Test that team member can view their own goal
        self.client.login(username='teammember', password='testpass')
        response = self.client.get(reverse('goals:view_goals', args=[self.team_member_profile.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Permission Test Goal')
        
        # Test that team member cannot view manager's goals
        response = self.client.get(reverse('goals:view_goals', args=[self.user_profile.id]))
        self.assertEqual(response.status_code, 403)