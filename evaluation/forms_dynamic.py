# evaluation/forms_dynamic.py
from django import forms
from .models_dynamic import DynamicEvaluation, DynamicManagerEvaluation, Answer, ManagerAnswer, Question, QuestionChoice, EvalForm
from authentication.models import Department

class EvalFormForm(forms.ModelForm):
    class Meta:
        model = EvalForm
        fields = ["department", "name"]
        widgets = {
            "department": forms.Select(attrs={"class": "input-field"}),
            "name": forms.TextInput(attrs={"class": "input-field"}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "qtype", "required", "min_value", "max_value", "order"]
        widgets = {
            "text": forms.TextInput(attrs={"class": "input-field"}),
            "qtype": forms.Select(attrs={"class": "input-field"}),
            "required": forms.CheckboxInput(attrs={"class": "h-4 w-4"}),
            "min_value": forms.NumberInput(attrs={"class": "input-field", "min": "0"}),
            "max_value": forms.NumberInput(attrs={"class": "input-field"}),
            "order": forms.NumberInput(attrs={"class": "input-field"}),
        }

    def _toggle_numeric_fields_disabled_state(self, qtype):
        """Helper method to toggle disabled state for numeric fields based on question type."""
        numeric_qtypes = ['stars', 'emoji', 'rating', 'number']
        is_disabled = qtype and qtype not in numeric_qtypes
        
        for field_name in ['min_value', 'max_value']:
            if field_name in self.fields:
                if is_disabled:
                    self.fields[field_name].widget.attrs['disabled'] = True
                    self.fields[field_name].widget.attrs['class'] = 'input-field disabled'
                else:
                    self.fields[field_name].widget.attrs.pop('disabled', None)
                    self.fields[field_name].widget.attrs['class'] = 'input-field'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get current question type
        qtype = self.data.get('qtype') if self.data else (self.instance.qtype if self.instance else None)
        
        # Use helper method to manage disabled state
        self._toggle_numeric_fields_disabled_state(qtype)

    def clean_min_value(self):
        """Validate min_value field individually."""
        min_value = self.cleaned_data.get('min_value')
        qtype = self.cleaned_data.get('qtype')
        
        # Validate that min_value cannot be negative for any question type that uses it
        numeric_qtypes = ['stars', 'emoji', 'rating', 'number']
        if qtype in numeric_qtypes and min_value is not None and min_value < 0:
            raise forms.ValidationError(f'Minimum value cannot be negative for {qtype} questions.')
        
        return min_value

    def clean(self):
        """Custom validation to ensure required fields are filled."""
        cleaned_data = super().clean()
        
        # Handle disabled fields - set them to None for non-numeric question types
        qtype = cleaned_data.get('qtype')
        if qtype and qtype not in ['stars', 'emoji', 'rating', 'number']:
            cleaned_data['min_value'] = None
            cleaned_data['max_value'] = None
        
        # Model validation will handle max_value constraints
        return cleaned_data


class QuestionChoiceForm(forms.ModelForm):
    class Meta:
        model = QuestionChoice
        fields = ["value", "label"]
        widgets = {
            "value": forms.TextInput(attrs={"class": "input-field"}),
            "label": forms.TextInput(attrs={"class": "input-field"}),
        }

class DynamicEvaluationForm(forms.Form):
    @staticmethod
    def _build_field_for_question(q, existing_answers=None, is_preview=False):
        """
        Helper method to build form field for a given question.
        
        Args:
            q: Question instance
            existing_answers: Dict of existing answers {question_id: answer}
            is_preview: Whether this is for preview mode (affects required/disabled state)
        
        Returns:
            tuple: (field, initial_value)
        """
        initial = None
        required = q.required if not is_preview else False
        
        if q.qtype == Question.QType.STARS:
            max_stars = q.max_value or 5
            choices = [(i, str(i)) for i in range(q.min_value or 1, max_stars + 1)]
            field = forms.ChoiceField(choices=choices, required=required, widget=StarRadioSelect)
            
            if existing_answers and q.id in existing_answers and existing_answers[q.id].int_value is not None:
                initial = str(existing_answers[q.id].int_value)

        elif q.qtype == Question.QType.RATING:
            max_rating = q.max_value or 5
            choices = [(i, str(i)) for i in range(q.min_value or 1, max_rating + 1)]
            field = forms.ChoiceField(choices=choices, required=required, widget=PillRadioSelect)
            
            if existing_answers and q.id in existing_answers and existing_answers[q.id].int_value is not None:
                initial = str(existing_answers[q.id].int_value)

        elif q.qtype == Question.QType.EMOJI:
            choices = [(i, str(i)) for i in range(q.min_value or 1, (q.max_value or 5) + 1)]
            field = forms.ChoiceField(choices=choices, required=required, widget=EmojiRadioSelect)
            
            if existing_answers and q.id in existing_answers and existing_answers[q.id].int_value is not None:
                initial = str(existing_answers[q.id].int_value)

        elif q.qtype == Question.QType.NUMBER:
            min_val = q.min_value or 0
            max_val = q.max_value
            field = forms.IntegerField(
                required=required, 
                min_value=min_val,
                max_value=max_val,
                widget=forms.NumberInput(attrs={"min": str(min_val), "max": str(max_val) if max_val else ""})
            )
            
            if existing_answers and q.id in existing_answers:
                initial = existing_answers[q.id].int_value

        elif q.qtype == Question.QType.BOOL:
            choices = [(1, "Yes"), (0, "No")]
            field = forms.ChoiceField(choices=choices, required=required, widget=BoolRadioSelect)
            
            if existing_answers and q.id in existing_answers and existing_answers[q.id].int_value is not None:
                initial = str(existing_answers[q.id].int_value)

        elif q.qtype == Question.QType.SELECT:
            # Note: q.choices.all() uses prefetched data from prefetch_related("choices") in __init__
            # This avoids N+1 queries when multiple questions have choices
            choices = [(c.value, c.label) for c in q.choices.all()]
            field = forms.ChoiceField(choices=choices, required=required)
            
            if existing_answers and q.id in existing_answers:
                initial = existing_answers[q.id].choice_value

        elif q.qtype == Question.QType.LONG:
            field = forms.CharField(required=required, widget=forms.Textarea(attrs={"rows": 4}))
            
            if existing_answers and q.id in existing_answers:
                initial = existing_answers[q.id].text_value

        else:  # SHORT
            field = forms.CharField(required=required, widget=forms.TextInput())
            
            if existing_answers and q.id in existing_answers:
                initial = existing_answers[q.id].text_value

        # Set help text if available
        if q.help_text:
            field.help_text = q.help_text
            
        # Set initial value if available
        if initial is not None:
            field.initial = initial
            
        return field, initial

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        # Store prefetched questions to avoid extra queries in clean() and save()
        self.questions = instance.form.questions.prefetch_related("choices").all()
        self.existing_answers = {a.question_id: a for a in instance.answers.all()}

        for q in self.questions:
            if q.qtype == Question.QType.SECTION:
                # No input; rendered by template as a step header
                self.fields[f"section_{q.id}"] = forms.CharField(required=False, initial=q.text, widget=forms.HiddenInput())
                continue

            name = f"q_{q.id}"
            
            # Use the shared helper method to build the field
            field, initial = self._build_field_for_question(q, self.existing_answers, is_preview=False)

            self.fields[name] = field
            self.fields[name].label = q.text
            # Store the required status for custom validation
            self.fields[name].question_required = q.required

    def clean(self):
        """Custom validation to ensure required fields are filled and values are within range."""
        cleaned_data = super().clean()
        
        # Validate numeric fields against their min/max constraints
        # Reuse prefetched questions to avoid extra query
        q_by_id = {q.id: q for q in self.questions}
        
        for name, value in cleaned_data.items():
            if not name.startswith("q_"):
                continue
            qid = int(name.split("_", 1)[1])
            q = q_by_id[qid]
            
            # Validate NUMBER type questions
            if q.qtype == Question.QType.NUMBER and value is not None:
                min_val = q.min_value or 0
                max_val = q.max_value
                
                if value < min_val:
                    self.add_error(name, f"Value must be at least {min_val}.")
                elif max_val is not None and value > max_val:
                    self.add_error(name, f"Value cannot exceed {max_val}.")
        
        return cleaned_data

    def save(self):
        """Save the form data to the evaluation instance (employee or manager)."""
        inst = self.instance
        cleaned = self.cleaned_data

        # Reuse prefetched questions and existing answers to avoid extra queries
        q_by_id = {q.id: q for q in self.questions}
        ans_by_qid = self.existing_answers

        new_answers, updates = [], []

        for name, value in cleaned.items():
            if not name.startswith("q_"):
                continue
            qid = int(name.split("_", 1)[1])
            q = q_by_id[qid]

            int_val = None
            text_val = None
            choice_val = None

            if q.qtype in (Question.QType.STARS, Question.QType.RATING, Question.QType.EMOJI, Question.QType.NUMBER):
                int_val = int(value) if value not in (None, "") else None
            elif q.qtype == Question.QType.BOOL:
                if value == "True":
                    int_val = 1
                elif value == "False":
                    int_val = 0
                else:
                    int_val = 1 if value else 0
            elif q.qtype == Question.QType.SELECT:
                choice_val = value or None
            elif q.qtype in (Question.QType.SHORT, Question.QType.LONG):
                text_val = value or None

            if qid in ans_by_qid:
                a = ans_by_qid[qid]
                a.int_value, a.text_value, a.choice_value = int_val, text_val, choice_val
                updates.append(a)
            else:
                # Determine which Answer model to use based on instance type
                if isinstance(inst, DynamicManagerEvaluation):
                    answer_class = ManagerAnswer
                else:
                    answer_class = Answer
                
                new_answers.append(answer_class(
                    instance=inst,
                    question=q,
                    int_value=int_val,
                    text_value=text_val,
                    choice_value=choice_val,
                ))

        if new_answers:
            # Use the appropriate Answer model for bulk_create
            if isinstance(inst, DynamicManagerEvaluation):
                ManagerAnswer.objects.bulk_create(new_answers, ignore_conflicts=True)
            else:
                Answer.objects.bulk_create(new_answers, ignore_conflicts=True)
        if updates:
            # Use the appropriate Answer model for bulk_update
            if isinstance(inst, DynamicManagerEvaluation):
                ManagerAnswer.objects.bulk_update(updates, ["int_value", "text_value", "choice_value"])
            else:
                Answer.objects.bulk_update(updates, ["int_value", "text_value", "choice_value"])

        return inst

class PreviewEvalForm(forms.Form):
    def __init__(self, *args, eval_form: EvalForm, existing_answers=None, **kwargs):
        """
        Initialize preview form for an evaluation form (employee or manager).
        
        Args:
            eval_form: The EvalForm instance to preview
            existing_answers: Optional dict of existing answers {question_id: answer} 
                            to show filled responses in preview mode
        """
        super().__init__(*args, **kwargs)
        qs = eval_form.questions.prefetch_related("choices").all()

        for q in qs:
            if q.qtype == Question.QType.SECTION:
                self.fields[f"section_{q.id}"] = forms.CharField(required=False, initial=q.text, widget=forms.HiddenInput())
                continue

            name = f"q_{q.id}"

            # Use the shared helper method to build the field (from preview mode)
            # Pass existing_answers if provided to show filled responses
            field, initial = DynamicEvaluationForm._build_field_for_question(q, existing_answers=existing_answers, is_preview=True)

            # Apply preview-specific styling
            field.widget.attrs["disabled"] = True
            if getattr(field.widget, "input_type", "") not in ("radio", "checkbox"):
                field.widget.attrs.setdefault(
                    "class", "w-full px-3 py-2 rounded bg-[#1e1e1e] border border-gray-700 text-white"
                )
            
            self.fields[name] = field
            self.fields[name].label = q.text


# ---------- WIDGET TEMPLATES ----------

class StarRadioSelect(forms.RadioSelect):
    template_name = "evaluation/widgets/star_radio.html"
    option_template_name = "evaluation/widgets/star_option.html"

class EmojiRadioSelect(forms.RadioSelect):
    template_name = "evaluation/widgets/emoji_radio.html"
    option_template_name = "evaluation/widgets/emoji_option.html"

class PillRadioSelect(forms.RadioSelect):
    """0–10 'pill' style (or any min..max pills)."""
    template_name = "evaluation/widgets/pill_radio.html"
    option_template_name = "evaluation/widgets/pill_option.html"

class BoolRadioSelect(forms.RadioSelect):
    """Yes/No boolean radio buttons."""
    template_name = "evaluation/widgets/bool_radio.html"
    option_template_name = "evaluation/widgets/bool_option.html"
# -------------------------------------
