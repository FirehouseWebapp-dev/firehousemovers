from django.urls import path
from . import views

app_name = "awards"

urlpatterns = [
    # Dashboard and award CRUD
    path("awards/", views.DashboardView.as_view(), name="dashboard"),
    path("add/", views.AwardCreateView.as_view(), name="add_award"),
    path("edit/<int:pk>/", views.AwardUpdateView.as_view(), name="edit_award"),
    path("delete/<int:pk>/", views.AwardDeleteView.as_view(), name="delete_award"),

    # Category CRUD
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/edit/<int:pk>/", views.CategoryUpdateView.as_view(), name="edit_category"),
    path("categories/delete/<int:pk>/", views.CategoryDeleteView.as_view(), name="delete_category"),

    # Gift card & award card (still FBVs)
    path("gift-card/", views.gift_card_view, name="gift_card"),
    path("award-card/", views.award_card_view, name="award_card"),
    path("get-emails/", views.get_emails, name="get_emails"),
]
