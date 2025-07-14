from django.urls import path
from gift.views import GiftCardView, AwardCardView, get_emails
from . import views

app_name = "awards"


urlpatterns = [
    path("gift-card/", GiftCardView.as_view(), name="gift_card"),
    path("award-card/", AwardCardView.as_view(), name="award_card"),
    path('get-emails/', get_emails, name='get_emails'),
    path('awards/', views.dashboard, name='dashboard'),
    path("add/", views.add_award, name="add_award"),
    path('categories/', views.category_list, name='category_list'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
]
