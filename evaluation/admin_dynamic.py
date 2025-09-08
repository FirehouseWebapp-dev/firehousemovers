from django import forms
from .models_dynamic import DynamicEvaluation, Answer, Question, EvalForm

# ---------- WIDGET TEMPLATES ----------
class StarRadioSelect(forms.RadioSelect):
    template_name = "evaluation/widgets/star_radio.html"
    option_template_name = "evaluation/widgets/star_option.html"

class EmojiRadioSelect(forms.RadioSelect):
    template_name = "evaluation/widgets/emoji_radio.html"
    option_template_name = "evaluation/widgets/emoji_option.html"
# -------------------------------------


class DynamicEvaluationForm(forms.Form):
    """
    Built from Questions for a specific DynamicEvaluation instance.
    """
    def __init__(self, *args, instance: DynamicEvaluation, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

        qs = (instance.form.questions
              .prefetch_related("choices")
              .all())
        existing = {a.question_id: a for a in instance.answers.all()}

        for q in qs:
            name = f"q_{q.id}"
            initial = None

            if q.qtype in (Question.QType.STARS, Question.QType.RATING):
                choices = [(i, str(i)) for i in range(q.min_value or 1, (q.max_value or 5) + 1)]
                field = forms.ChoiceField(choices=choices, required=q.required,
                                          widget=StarRadioSelect if q.qtype == Question.QType.STARS else forms.RadioSelect)
                if q.id in existing and existing[q.id].int_value is not None:
                    initial = str(existing[q.id].int_value)

            elif q.qtype == Question.QType.EMOJI:
                choices = [(i, str(i)) for i in range(q.min_value or 1, (q.max_value or 5) + 1)]
                field = forms.ChoiceField(choices=choices, required=q.required, widget=EmojiRadioSelect)
                if q.id in existing and existing[q.id].int_value is not None:
                    initial = str(existing[q.id].int_value)

            elif q.qtype == Question.QType.NUMBER:
                field = forms.IntegerField(required=q.required)
                if q.id in existing:
                    initial = existing[q.id].int_value

            elif q.qtype == Question.QType.BOOL:
                field = forms.BooleanField(required=False)
                if q.id in existing and existing[q.id].int_value is not None:
                    initial = bool(existing[q.id].int_value)

            elif q.qtype == Question.QType.SELECT:
                choices = [(c.value, c.label) for c in q.choices.all()]
                field = forms.ChoiceField(choices=choices, required=q.required)
                if q.id in existing:
                    initial = existing[q.id].choice_value

            elif q.qtype == Question.QType.LONG:
                field = forms.CharField(required=q.required, widget=forms.Textarea(attrs={"rows": 4}))
                if q.id in existing:
                    initial = existing[q.id].text_value

            else:  # SHORT
                field = forms.CharField(required=q.required, widget=forms.TextInput())
                if q.id in existing:
                    initial = existing[q.id].text_value

            if q.help_text:
                field.help_text = q.help_text
            if initial is not None:
                field.initial = initial

            self.fields[name] = field
            self.fields[name].label = q.text

    def save(self) -> DynamicEvaluation:
        inst = self.instance
        cleaned = self.cleaned_data

        q_by_id = {q.id: q for q in inst.form.questions.all()}
        ans_by_qid = {a.question_id: a for a in inst.answers.all()}

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
                new_answers.append(Answer(
                    instance=inst,
                    question=q,
                    int_value=int_val,
                    text_value=text_val,
                    choice_value=choice_val,
                ))

        if new_answers:
            Answer.objects.bulk_create(new_answers, ignore_conflicts=True)
        if updates:
            Answer.objects.bulk_update(updates, ["int_value", "text_value", "choice_value"])

        return inst


class PreviewEvalForm(forms.Form):
    """Read-only preview of an EvalForm (manager view)."""
    def __init__(self, *args, eval_form: EvalForm, **kwargs):
        super().__init__(*args, **kwargs)
        qs = eval_form.questions.prefetch_related("choices").all()

        for q in qs:
            name = f"q_{q.id}"
            if q.qtype in (Question.QType.STARS, Question.QType.RATING):
                choices = [(i, str(i)) for i in range(q.min_value or 1, (q.max_value or 5) + 1)]
                widget = StarRadioSelect if q.qtype == Question.QType.STARS else forms.RadioSelect
                field = forms.ChoiceField(choices=choices, required=False, widget=widget)
            elif q.qtype == Question.QType.EMOJI:
                choices = [(i, str(i)) for i in range(q.min_value or 1, (q.max_value or 5) + 1)]
                field = forms.ChoiceField(choices=choices, required=False, widget=EmojiRadioSelect)
            elif q.qtype == Question.QType.NUMBER:
                field = forms.IntegerField(required=False)
            elif q.qtype == Question.QType.BOOL:
                field = forms.BooleanField(required=False)
            elif q.qtype == Question.QType.SELECT:
                choices = [(c.value, c.label) for c in q.choices.all()]
                field = forms.ChoiceField(choices=choices, required=False)
            elif q.qtype == Question.QType.LONG:
                field = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 4}))
            else:
                field = forms.CharField(required=False, widget=forms.TextInput())

            if q.help_text:
                field.help_text = q.help_text
            field.widget.attrs["disabled"] = True
            if getattr(field.widget, "input_type", "") not in ("radio", "checkbox"):
                field.widget.attrs.setdefault(
                    "class",
                    "w-full px-3 py-2 rounded bg-[#1e1e1e] border border-gray-700 text-white"
                )
            self.fields[name] = field
            self.fields[name].label = q.text
