from django.db import models
from django.core.exceptions import ValidationError
from authentication.models import UserProfile


class Gift_company(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Gift_card(models.Model):
    company = models.ForeignKey(Gift_company, on_delete=models.CASCADE)
    date_of_purchase = models.DateField(null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    added_by = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="added_by_user"
    )

    def clean(self):
        if self.amount:
            if self.amount < 1:
                raise ValidationError(
                    f"The Gift Card amount cannot be less then one ({self.amount})."
                )

    def __str__(self):
        return f"{self.company }- {self.amount}"


class Award(models.Model):
    date_award = models.DateField(null=True, blank=True)
    employee_name = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="employee_names"
    )
    card = models.ForeignKey(
        Gift_card, on_delete=models.CASCADE, related_name="gift_card"
    )
    amount = models.IntegerField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    awarded_by = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="awarded_user"
    )
    date_saved = models.DateField(null=True, blank=True)

    def clean(self):
        # Check that the amount does not exceed the associated GiftCard's amount
        if self.amount and self.card:
            if self.amount > self.card.amount:
                raise ValidationError(
                    f"The award amount cannot exceed the amount of the associated gift card ({self.card.amount})."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Award, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_name }- {self.card}"
