from django.urls import path

from gift.views import GiftCardView,AwardCardView

urlpatterns = [
    path('gift-card/', GiftCardView.as_view(), name='gift_card'),
    path('award-card/', AwardCardView.as_view(), name='award_card'),
]
