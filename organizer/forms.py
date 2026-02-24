
import re
from django import forms
from crispy_forms.helper import FormHelper
from django.utils import timezone

from .models import Event,Match, TicketType # Ensure TicketType is imported
from crispy_forms.layout import Layout, Submit,Row, Column, Div,Fieldset,HTML
from django.forms import inlineformset_factory # Import this utility
from .models import PlayerSelectionForm, OrganizerProfile
from crispy_forms.bootstrap import InlineRadios, PrependedText
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.safestring import mark_safe


class EventCreationForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'game_type', 'game_type_other', 'date_time', 'location', 'description', 'status', 'photo']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Critical: We are handling the <form> in HTML
        self.helper.layout = Layout(
            # STEP 1: Identity (Will be wrapped in a div in HTML)
            Div(
                Row(
                    Column('name', css_class='col-md-6'),
                    Column('game_type', css_class='col-md-6'),
                ),
                'game_type_other',
                'description',
                'photo',
                css_id='step-1-fields'
            ),
            # STEP 2: Logistics (Will be wrapped in a div in HTML)
            Div(
                Row(
                    Column('date_time', css_class='col-md-6'),
                    Column('location', css_class='col-md-6'),
                ),
                'status',
                css_id='step-2-fields',
                css_class='d-none' # Hidden by default
            )
        )

    def clean_date_time(self):
        date_time = self.cleaned_data.get('date_time')
        if date_time and date_time < timezone.now():
            raise forms.ValidationError("You cannot select a date and time in the past.")
        return date_time


TicketTypeFormset = inlineformset_factory(
        Event,
        TicketType,
        fields=('name', 'price', 'available_quantity'),
        extra=1,  # Start with one empty form
        can_delete=True
    )



class PlayerSelectionCrispyForm(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        widget=forms.RadioSelect,
        required=False  # Handled dynamically
    )

    medical_conditions = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect,
        initial=False,
        required=False,
        label="Do you have any pre-existing medical conditions?"
    )

    class Meta:
        model = PlayerSelectionForm
        exclude = ['organizer', 'is_published', 'status', 'applicant', 'event']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', 'id': 'id_dob'}),

            'deadline': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    # This helps browsers like Chrome/Safari trigger the native picker
                },
                format='%Y-%m-%dT%H:%M'  # Critical for the calendar to load existing data
            ),

            'email': forms.EmailInput(attrs={'id': 'id_email'}),
            'previous_experience_details': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'List major tournaments or clubs...'}),
            'medical_details': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Please specify if any...'}),
        }

    def __init__(self, *args, is_player=False, preview_mode=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        context_fields = ['event_name', 'sports', 'level', 'address']
        # Identify all fields that belong to the Athlete (anything not in context_fields)
        athlete_fields = [f for f in self.fields if f not in context_fields]

        if is_player or preview_mode:
            # --- ATHLETE MODE OR PREVIEW MODE ---
            # 1. Disable fields pre-filled by Organizer (Read-only trial info)
            for field in context_fields:
                self.fields[field].disabled = True
                self.fields[field].required = False

            # 2. Make athlete fields mandatory (Unless it's just a preview)
            for field in athlete_fields:
                self.fields[field].required = not preview_mode
                if preview_mode:
                    self.fields[field].disabled = True

            # 3. Modular Layout (The Wizard UI)
            self.helper.layout = Layout(
                # READ-ONLY HEADER
                Fieldset(
                    "📌 Trial Overview",
                    Row(Column('event_name', css_class='col-md-7 mb-1'), Column('sports', css_class='col-md-5 mb-1')),
                    Row(Column('level', css_class='col-md-4 mb-2'), Column('address', css_class='col-md-8 mb-2')),
                    css_class="mb-4 p-3 rounded border shadow-sm bg-light"
                ),
                # STEP 1
                Div(
                    HTML("<h4 class='mb-4 text-primary border-bottom pb-2'>Step 1: Identity & Health</h4>"),
                    Row(Column('full_name', css_class='col-md-6 mb-2'),
                        Column('citizenship_number', css_class='col-md-6 mb-2')),
                    Row(
                        Column('dob', css_class='col-md-4 mb-2'),
                        Column(HTML(
                            '<label class="form-label">Age*</label><input type="text" id="age_field" class="form-control bg-light" readonly>'),
                               css_class='col-md-4 mb-2'),
                        Column('blood_group', css_class='col-md-4 mb-2'),
                    ),
                    Row(Column(InlineRadios('gender'), css_class='col-md-12 mb-3')),
                    css_id="step-1", css_class="form-step"
                ),
                # STEP 2
                Div(
                    HTML("<h4 class='mb-4 text-primary border-bottom pb-2'>Step 2: Experience & Contact</h4>"),
                    Row(Column('experience_level', css_class='col-md-6 mb-2'),
                        Column(PrependedText('phone', '🇳🇵 +977'), css_class='col-md-6 mb-2')),
                    'email', 'previous_experience_details',
                    Row(Column('medical_conditions', css_class='col-md-4 mb-2'),
                        Column('medical_details', css_class='col-md-8 mb-2')),
                    css_id="step-2", css_class="form-step d-none"
                ),
                # STEP 3
                Div(
                    HTML("<h4 class='mb-4 text-primary border-bottom pb-2'>Step 3: Verification & Legal</h4>"),
                    Row(
                        Column('temporary_address', css_class='col-md-5 mb-2'),
                        Column(HTML(
                            '<div class="d-flex align-items-center justify-content-center h-100 mt-4"><input type="checkbox" id="sameAddress" class="me-2"><span>Same</span></div>'),
                               css_class='col-md-2 mb-2 text-center'),
                        Column('permanent_address', css_class='col-md-5 mb-2'),
                    ),
                    Row(Column('guardian_name', css_class='col-md-4 mb-2'),
                        Column('guardian_relation', css_class='col-md-4 mb-2'),
                        Column('guardian_phone', css_class='col-md-4 mb-2')),
                    Row(Column('citizenship', css_class='col-md-6 mb-2'),
                        Column('certificates', css_class='col-md-6 mb-2')),
                    css_id="step-3", css_class="form-step d-none"
                ),
            )
        else:
            # --- ORGANIZER MODE (Publishing Fix) ---
            # IMPORTANT: Disable validation for athlete fields so organizer can save just the header
            for field in athlete_fields:
                self.fields[field].required = False

            for field in context_fields:
                self.fields[field].required = True

            self.fields['deadline'].required = True

            self.helper.layout = Layout(
                Fieldset(
                    "🛠️ Setup Trial Form Template",
                    HTML(
                        "<p class='text-muted small'>Fill these details to define the trial context for athletes.</p>"),
                    Row(Column('event_name', css_class='col-md-7 mb-1'), Column('sports', css_class='col-md-5 mb-1')),
                    Row(Column('level', css_class='col-md-4 mb-2'), Column('address', css_class='col-md-8 mb-2')),

                    # Row(Column(PrependedText('deadline', '<i class="fas fa-clock"></i>'), css_class='col-md-4 mb-2')),

                    Row(Column(PrependedText('deadline', mark_safe('<i class="fas fa-calendar-alt"></i>')), css_class='col-md-4 mb-2')),
                ),
            )

        # ADD THIS INSIDE PlayerSelectionCrispyForm
    def clean_deadline(self):
            deadline = self.cleaned_data.get('deadline')
            if deadline and deadline < timezone.now():
                raise forms.ValidationError("The deadline cannot be in the past. Please select a future date/time.")
            return deadline

    # Validation Logic (Keep these as they are)
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^9[678]\d{8}$', phone):
            raise forms.ValidationError("Enter a valid 10-digit Nepal mobile number.")
        return phone

    def clean_guardian_phone(self):
        phone = self.cleaned_data.get('guardian_phone')
        if phone and not re.match(r'^9[678]\d{8}$', phone):
            raise forms.ValidationError("Enter a valid 10-digit Nepal mobile number.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError("Please enter a valid email address.")
        return email


MatchFormset = inlineformset_factory(
    Event,
    Match,
    fields=('game_type', 'team_a', 'team_b', 'match_time', 'venue'),
    extra=1,  # Show 1 empty row by default
    can_delete=True,
    widgets={
        'match_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        'game_type': forms.Select(attrs={'class': 'form-select'}),
        'team_a': forms.TextInput(attrs={'placeholder': 'Team A', 'class': 'form-control'}),
        'team_b': forms.TextInput(attrs={'placeholder': 'Team B', 'class': 'form-control'}),
        'venue': forms.TextInput(attrs={'placeholder': 'Stadium Name', 'class': 'form-control'}),
    }
)


class OrganizerSettingsForm(forms.ModelForm):
    class Meta:
        model = OrganizerProfile
        fields = [
            'organization_name', 'organization_logo', 'contact_email',
            'contact_phone', 'address', 'bio', 'certificate', # Added address & certificate
            'enable_scanner_sound', 'auto_submit_scan',
            'khalti_merchant_id', 'tax_percentage'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell athletes about your club...'}),
            'address': forms.TextInput(attrs={'placeholder': 'City, Street, Ward No.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We remove the complex Layout here because you are manually
        # placing fields in tabs in your HTML template.
        self.helper = FormHelper()
        self.helper.form_tag = False
        # self.helper.layout = Layout(
        #     # Tab 1: General Profile
        #     Div(
        #         HTML("<h4 class='text-primary border-bottom pb-2 mb-3'>Organization Profile</h4>"),
        #         Row(
        #             Column('organization_name', css_class='col-md-6'),
        #             Column('organization_logo', css_class='col-md-6'),
        #         ),
        #         Row(
        #             Column('contact_email', css_class='col-md-6'),
        #             Column('contact_phone', css_class='col-md-6'),
        #         ),
        #         'bio',
        #         css_id='settings-general'
        #     ),
        #     # Tab 2: Security & Finance
        #     Div(
        #         HTML("<h4 class='text-primary border-bottom pb-2 mb-3 mt-4'>Gate & Finance</h4>"),
        #         Row(
        #             Column(InlineRadios('enable_scanner_sound'), css_class='col-md-6'),
        #             Column(InlineRadios('auto_submit_scan'), css_class='col-md-6'),
        #         ),
        #         Row(
        #             Column('khalti_merchant_id', css_class='col-md-8'),
        #             Column('tax_percentage', css_class='col-md-4'),
        #         ),
        #         Row(
        #             Column('email_notifications', css_class='col-md-6'),
        #             Column('daily_summary_report', css_class='col-md-6'),
        #         ),
        #         css_id='settings-security'
        #     )
        # )