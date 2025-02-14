from django import forms
from .models import Onsite_inspection, Trailer_inspection, Truck_inspection


class TrailerInspectionForm(forms.ModelForm):
    class Meta:
        model = Trailer_inspection
        fields = [
            "date",
            "trailer",
            "clean_status",
            "trash",
            "blanket_84",
            "hand_trucks_with_covers",
            "four_wheel_dolly",
            "short_straps",
            "long_straps",
            "ramp",
            "rubber_bands",
            "red_floor_runner",
            "forearm_straps",
            "wardrobe_boxes_with_bars",
            "tv_box_for_rental",
            "multi_tool_set",
            "hand_tools_bag",
            "two_carabiner",
            "broom",
        ]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                    "type": "date",
                }
            ),
            "trailer": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "clean_status": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "trash": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "blanket_84": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "hand_trucks_with_covers": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "four_wheel_dolly": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "short_straps": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "long_straps": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "ramp": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "rubber_bands": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "red_floor_runner": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "forearm_straps": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "wardrobe_boxes_with_bars": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "tv_box_for_rental": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "multi_tool_set": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "hand_tools_bag": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "two_carabiner": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "broom": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "saved_by": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
        }


class TruckInspectionForm(forms.ModelForm):
    class Meta:
        model = Truck_inspection
        fields = [
            "date",
            "truck",
            "clean_status",
            "in_cab",
            "bed_of_truck",
            "first_aid_kit",
            "floor_mats",
            "business_cards",
            "business_cards_magnetic",
            "fuses",
            "two_pens",
            "sharpie",
            "camera",
            "flash_light",
            "sun_visor",
            "geo_tab",
            "jack_and_links",
            "cab_card",
            "registration",
            "insurance_card",
            "accident_report_form",
            "process_of_accident",
            "fire_extinguisher",
            "expiry_date_fe",
            "four_way",
            "min_7_orange",
            "hazard_triangle_x3",
            "jumper_cables",
            "large_door_stops",
            "trash_bag",
            "roll_paper_towels",
            "small_hand",
            "bottle_jack",
            "cones",
            "spare_tire",
            "condition_spare_tyre",
        ]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                    "type": "date",
                }
            ),
            "truck": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "clean_status": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "in_cab": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "bed_of_truck": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "first_aid_kit": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "floor_mats": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "business_cards": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "business_cards_magnetic": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "fuses": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "two_pens": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "sharpie": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "camera": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "flash_light": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "sun_visor": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "geo_tab": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "jack_and_links": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "cab_card": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "registration": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "insurance_card": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "accident_report_form": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "process_of_accident": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "fire_extinguisher": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "expiry_date_fe": forms.DateInput(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                    "type": "date",
                }
            ),
            "four_way": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "min_7_orange": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "hazard_triangle_x3": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "jumper_cables": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "large_door_stops": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "trash_bag": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "roll_paper_towels": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "small_hand": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "bottle_jack": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "cones": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "spare_tire": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
            "condition_spare_tyre": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                }
            ),
        }


class OnsiteInspectionForm(forms.ModelForm):
    class Meta:
        model = Onsite_inspection
        fields = "__all__"  # Include all fields from the model
        widgets = {
            # Basic Information
            "job_number": forms.TextInput(attrs={"class": "form-control"}),
            "customer_name": forms.TextInput(attrs={"class": "form-control"}),
            "customer_phone": forms.TextInput(attrs={"class": "form-control"}),
            "pickup_address": forms.Textarea(
                attrs={"class": "form-control", "rows": 2}
            ),
            "delivery_address": forms.Textarea(
                attrs={"class": "form-control", "rows": 2}
            ),
            "crew_leader": forms.Select(attrs={"class": "form-select"}),
            "crew_members": forms.SelectMultiple(attrs={"class": "form-select"}),
            "materials_check_rating": forms.RadioSelect(
                choices=[(i, i) for i in range(6)]
            ),
            # Rating Fields (Radio Buttons)
            **{
                field_name: forms.RadioSelect(choices=[(i, i) for i in range(6)])
                for field_name in [
                    "materials_check_rating",
                    "vehicle_inventory_rating",
                    "customer_communication_rating",
                    "parking_arranged_rating",
                    "customer_greeted_rating",
                    "crew_introduction_rating",
                    "initial_walkthrough_rating",
                    "estimate_comparison_rating",
                    "damage_inspection_rating",
                    "paperwork_signed_rating",
                    "valuables_secured_rating",
                    "protection_setup_rating",
                    "photos_sent_rating",
                    "inventory_management_rating",
                    "furniture_disassembly_rating",
                    "parts_management_rating",
                    "loading_quality_rating",
                    "padding_used_rating",
                    "load_secured_rating",
                    "final_walkthrough_rating",
                    "customer_initials_rating",
                    "follow_instructions_rating",
                    "truck_prepared_rating",
                    "dispatch_complete_rating",
                    "dispatch_unload_rating",
                    "protection_setup_rating",
                    "placement_accuracy_rating",
                    "pad_management_rating",
                    "furniture_reassembly_rating",
                    "customer_walkthrough_rating",
                    "vehicle_inspection_rating",
                    "final_charges_rating",
                    "customer_review_rating",
                    "paperwork_rating",
                    "payment_collection_rating",
                    "video_testimonial_rating",
                    "completion_notice_rating",
                ]
            },
            # Comments and Feedback
            "comments": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "customer_feedback": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].required = False
