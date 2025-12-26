# # organizer/forms.py (CREATE THIS FILE)

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit,Row, Column, Div
from django.forms import inlineformset_factory # Import this utility
from .models import Event,Match, TicketType # Ensure TicketType is imported


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

# Add this at the bottom of your forms.py
MatchFormset = inlineformset_factory(
    Event,
    Match,
    fields=('game_type', 'team_a', 'team_b', 'match_time', 'venue'),
    extra=1,  # Show 1 empty row by default
    can_delete=True,
    widgets={
        'match_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
    }
)