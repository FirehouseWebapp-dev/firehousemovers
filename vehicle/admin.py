from django.contrib import admin

from .models import (Vehicle,AvailabilityData, Support, Dispatch, Order, Inspection, Evaluation)

admin.site.register([ Vehicle,AvailabilityData, Support, Dispatch, Inspection, Evaluation ,Order])
