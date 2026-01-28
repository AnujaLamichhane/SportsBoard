
import re
from django import forms
from crispy_forms.helper import FormHelper
from .models import Event,Match, TicketType # Ensure TicketType is imported
from crispy_forms.layout import Layout, Submit,Row, Column, Div,Fieldset,HTML
from django.forms import inlineformset_factory # Import this utility
from .models import PlayerSelectionForm
from crispy_forms.bootstrap import InlineRadios, PrependedText
from django.core.exceptions import ValidationError
from django.core.validators import validate_email



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


# class EventCreationForm(forms.ModelForm):
#     class Meta:
#         model = Event
#         # Only include fields the organizer should edit directly
#         fields = ['name',
#                   'game_type',  # NEW
#                   'game_type_other',
#                   'date_time', 'location', 'description',
#                   'status',
#                   'photo',
#                   ]
#         widgets = {
#             'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#             'description': forms.Textarea(attrs={'rows': 4}),
#         }
#
#
#
#
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             # Arrange fields nicely using Crispy Forms layout
#         #     'name',
#         #     'date_time',
#         #     'location',
#         #     'description',
#         #     'status',
#         #     # Add the submit button at the end
#         #     Submit('submit', 'Create Event', css_class='btn-warning mt-3')
#         # )
#             Row(
#                 Column('name', css_class='form-group col-md-6 mb-0'),
#                 Column('game_type', css_class='form-group col-md-6 mb-0'),
#                 css_class='form-row'
#             ),
#             'game_type_other',  # Added separately
#
#             Row(
#                 Column(Div('date_time', css_class='time-section'), css_class='form-group col-md-6 mb-0'),
#                 Column('location', css_class='form-group col-md-6 mb-0'),
#                 css_class='form-row'
#             ),
#
#             'description',
#
#             Row(
#                 Column('photo', css_class='form-group col-md-6 mb-0'),
#                 Column('status', css_class='form-group col-md-6 mb-0'),
#                 css_class='form-row'
#             ),
#             # The submit button is now explicitly styled and positioned
#             Submit('submit', 'Create Event', css_class='btn btn-warning mt-4 float-end')
#             # The 'float-end' class (Bootstrap 5) pushes the button to the right.
#         )
#
#         # Optionally hide 'Specify Other Game' until 'Others' is selected via JS
#         self.fields['game_type_other'].label = "Specify Other Game (if applicable)"
#         self.fields['game_type_other'].widget.attrs['style'] = 'display: none;'  # Hide by default

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
        required=True
    )
    class Meta:
        model = PlayerSelectionForm
        exclude = ['organizer', 'is_published', 'status','applicant','event']
        # fields='__all__'
        widgets = {
            # 'gender': forms.RadioSelect(choices=[('male', 'Male'), ('female', 'Female'), ('others', 'Others')]),
            'dob': forms.DateInput(attrs={'type': 'date','id': 'id_dob'}),
            'email': forms.EmailInput(attrs={'id': 'id_email'}),
        }

    def __init__(self, *args, is_player=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        event_fields = ['event_name', 'sports', 'level', 'address']
        player_mandatory = [
            'full_name', 'dob','age', 'gender', 'phone', 'email', 
            'temporary_address', 'permanent_address', 'guardian_name',
            'guardian_relation', 'guardian_phone', 'citizenship'
        ]
        # LOCK organizer-filled fields
        if is_player:
            for field in event_fields:
                self.fields[field].disabled = True
                # self.fields[field].required = False
                for field_name, field in self.fields.items():
                    if field_name not in event_fields:
                        field.required = True
            # Make player fields mandatory for the player
            # player_mandatory = ['full_name', 'dob','age','gender', 'phone','email', 
            #                    'temporary_address', 'permanent_address', 'guardian_name','guardian_relation',
            #                    'guardian_phone','citizenship']
            for field in player_mandatory:
                self.fields[field].required = True
                # if organizer_data:
                #     self.fields[field].initial = organizer_data.get(field)
        else:
            # If it IS an organizer, only event_fields are mandatory
            for field_name, field in self.fields.items():
                if field_name in event_fields:
                    field.required = True
                else:
                    field.required = False

        # self.helper = FormHelper()
        # self.helper.form_method = 'post'
        # self.helper.form_tag = False 
        self.helper.layout = Layout(

            Fieldset(
                " Event Details",
                Row(
                    Column('event_name', css_class='col-md-7 mb-1 '),
                    Column('sports', css_class='col-md-5 mb-1 '),
                ),
                Row(
                    Column('level', css_class='col-md-4 mb-2'),
                    Column('address', css_class='col-md-8 mb-2'),
                ),
            ),

            Fieldset(
                "Personal Information",
                Row(
                    Column('full_name', css_class='col-md-6 mb-2'),
                    Column('dob', css_class='col-md-3 mb-2'),
                    Column(HTML('''
                        <label>Age*</label>
                        <input type="text" id="age_field" class="form-control" placeholder="" readonly>
                    '''), css_class='col-md-3 mb-2'),
                    
                ),
                Row(
                    Column(PrependedText('phone', '🇳🇵 +977'), css_class='col-md-6 mb-2' ),
                    Column('email', css_class='col-md-6 mb-2'),
                    
                ),
                Row(
                    Column(InlineRadios('gender'), css_class='col-md-12 custom-gender-row'),
                ),
            ),
            Fieldset(
                "Address Information",
                Row(
                    Column('temporary_address', css_class='col-md-5 mb-2'),
                    Column(
                        HTML('<div class="d-flex align-items-center justify-content-center h-100 mt-4 pt-4"><input type="checkbox" id="sameAddress" class="me-2">'' '
                        '<span style="fw-bold text-dark color-black">Same as Temp</span></div>'), 
                        css_class='col-md-2 mb-0 text-center'
                    ),
                    Column('permanent_address', css_class='col-md-5 mb-0'),
                ),
            ),
            Fieldset(
                "Gurdian Details",
                Row(
                    Column('guardian_name', css_class='col-md-4 mb-2'),
                    Column('guardian_relation', css_class='col-md-4 mb-2'),
                    Column('guardian_phone', css_class='col-md-4 mb-2'),
                   
                ),
            ),
            Fieldset(
                "Documents",
                Row(

                        Column('citizenship', css_class='col-md-6 mb-2'),
                        Column('certificates', css_class='col-md-6 mb-2'), # Stays optional
                    ),
                    css_class='fillout-section'
                ),
        )
        

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^9[678]\d{8}$', phone):
            raise forms.ValidationError("Enter a valid 10 digit Nepal mobile number")
        return phone
    def clean_guardian_phone(self):
        phone = self.cleaned_data.get('guardian_phone')
        if phone and not re.match(r'^9[678]\d{8}$', phone):
            raise forms.ValidationError("Enter a valid 10 digit Nepal mobile number")
        return phone
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
         return email
        try:
            validate_email(email) # This triggers Django's deep email check
        except ValidationError:
            raise ValidationError("Please enter a valid email address (e.g., name@domain.com).")
        
        # IMPORTANT: You MUST return the email, or it will be saved as 'None'
        return email


# Add this at the bottom of your forms.py

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
