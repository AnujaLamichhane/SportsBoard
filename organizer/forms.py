# # organizer/forms.py (CREATE THIS FILE)

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit,Row, Column, Div
from .models import Event # Import the Event model
from django.forms import inlineformset_factory # Import this utility
from .models import Event, TicketType # Ensure TicketType is imported


class EventCreationForm(forms.ModelForm):
    class Meta:
        model = Event
        # Only include fields the organizer should edit directly
        fields = ['name',
                  'game_type',  # NEW
                  'game_type_other',
                  'date_time', 'location', 'description',
                  'status',
                  'photo',
                  ]
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            # Arrange fields nicely using Crispy Forms layout
        #     'name',
        #     'date_time',
        #     'location',
        #     'description',
        #     'status',
        #     # Add the submit button at the end
        #     Submit('submit', 'Create Event', css_class='btn-warning mt-3')
        # )
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('game_type', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'game_type_other',  # Added separately

            Row(
                Column(Div('date_time', css_class='time-section'), css_class='form-group col-md-6 mb-0'),
                Column('location', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),

            'description',

            Row(
                Column('photo', css_class='form-group col-md-6 mb-0'),
                Column('status', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            # The submit button is now explicitly styled and positioned
            Submit('submit', 'Create Event', css_class='btn btn-warning mt-4 float-end')
            # The 'float-end' class (Bootstrap 5) pushes the button to the right.
        )

        # Optionally hide 'Specify Other Game' until 'Others' is selected via JS
        self.fields['game_type_other'].label = "Specify Other Game (if applicable)"
        self.fields['game_type_other'].widget.attrs['style'] = 'display: none;'  # Hide by default

TicketTypeFormset = inlineformset_factory(
        Event,
        TicketType,
        fields=('name', 'price', 'available_quantity'),
        extra=2,  # Start with one empty form
        can_delete=True
    )


# from django import forms
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field, HTML
# from django.forms import inlineformset_factory
# from .models import Event, TicketType, SelectionForm, FormField  # Import the new models
#
#
# # --------------------------------------------------------------------------
# # 1. Event Creation Form (Existing)
# # --------------------------------------------------------------------------
#
# class EventCreationForm(forms.ModelForm):
#     class Meta:
#         model = Event
#         fields = ['name',
#                   'game_type',
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
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             Row(
#                 Column('name', css_class='form-group col-md-6 mb-0'),
#                 Column('game_type', css_class='form-group col-md-6 mb-0'),
#                 css_class='form-row'
#             ),
#             'game_type_other',
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
#             Submit('submit', 'Create Event', css_class='btn btn-warning mt-4 float-end')
#         )
#
#         self.fields['game_type_other'].label = "Specify Other Game (if applicable)"
#         self.fields['game_type_other'].widget.attrs['style'] = 'display: none;'
#
#
# # --------------------------------------------------------------------------
# # 2. Ticket Type Formset (Existing)
# # --------------------------------------------------------------------------
#
# TicketTypeFormset = inlineformset_factory(
#     Event,
#     TicketType,
#     fields=('name', 'price', 'available_quantity'),
#     extra=2,
#     can_delete=True
# )
#
#
# # --------------------------------------------------------------------------
# # 3. Dynamic Form Builder Components (NEW)
# # --------------------------------------------------------------------------
#
# class FormFieldForm(forms.ModelForm):
#     """
#     A form for an individual field definition (Label, Type, Options).
#     """
#
#     class Meta:
#         model = FormField
#         fields = ['label', 'field_type', 'options', 'is_required', 'order']
#         widgets = {
#             # Hide the 'order' field as it will be managed by JavaScript on the frontend
#             'order': forms.HiddenInput(),
#             'options': forms.Textarea(
#                 attrs={'rows': 2, 'placeholder': 'Comma-separated options (e.g., Small, Medium, Large)'}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Use Crispy Forms for styling the individual form fields
#         self.helper = FormHelper()
#         self.helper.form_tag = False  # Don't render <form> tags for formset forms
#         self.helper.layout = Layout(
#             Row(
#                 # Label/Question
#                 Column('label', css_class='form-group col-md-4 mb-0'),
#                 # Field Type (Dropdown, Text, etc.)
#                 Column('field_type', css_class='form-group col-md-3 mb-0'),
#                 # Options Textarea
#                 Column('options', css_class='form-group col-md-3 mb-0'),
#                 # Is Required Checkbox
#                 Column(
#                     Field('is_required', css_class='mt-4'),  # Push checkbox down
#                     css_class='form-group col-md-1 mb-0'
#                 ),
#                 # Hidden Order Field
#                 'order',
#                 # Delete checkbox (added automatically by the formset)
#
#                 css_class='form-row field-form-row align-items-center'
#             )
#         )
#
#
# # Create the Formset Factory for FormField
# # This allows the organizer to define multiple fields simultaneously
# FormFieldFormset = inlineformset_factory(
#     SelectionForm,  # Parent Model
#     FormField,  # Child Model
#     form=FormFieldForm,
#     fields=['label', 'field_type', 'options', 'is_required', 'order'],
#     extra=1,  # Start with 1 empty form
#     can_delete=True
# )
#
#
# class SelectionFormForm(forms.ModelForm):
#     """
#     A simple form for the SelectionForm model (mostly just to link to the event).
#     """
#
#     class Meta:
#         model = SelectionForm
#         fields = ['event']  # Only need the event field if creating a new form
#         widgets = {
#             'event': forms.Select(attrs={'class': 'form-select'}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['event'].label = "Select Event to Configure"
