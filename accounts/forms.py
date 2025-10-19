from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field,Layout,HTML,Submit
from django.contrib.auth import get_user_model


User = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):
    role = forms.ChoiceField(
        choices=[('user','Athlete/User'), ('organizer', 'Organizer')],
        widget=forms.RadioSelect,
        initial='user',
        label="Login As"
    )
#login form
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username', css_class='form-control form-control-lg', placeholder='Enter your username'),
            Field('password', css_class='form-control form-control-lg', placeholder='Enter your password'),
            Field('role', css_class=''),
            Submit('submit', 'Login', css_class= 'btn btn-primary btn-primary btn-lg w-100'),
        )
        # self.fields['email'].required = True  # Make email required
        self.fields['username'].help_text = None
        self.fields['password'].help_text = None
#signup form
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter your email'}),
        required=True
    )
    role = forms.ChoiceField(
        choices=[('user', 'Athlete/User'), ('organizer', 'Organizer')],
        widget=forms.RadioSelect,
        initial='user',
        label="Signup As"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'role',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username', css_class='form-control form-control-lg', placeholder='Choose a username'),
            Field('email', css_class='form-control form-control-lg', placeholder='Enter your email'),
            Field('password1', css_class='form-control form-control-lg', placeholder='Enter a strong password'),
            Field('password2', css_class='form-control form-control-lg', placeholder='Confirm your password'),
            HTML('<div class="role-selection mt-3 mb-4">'),
            Field('role', css_class=''),
            HTML('</div>'),
            Submit('submit', 'Sign Up', css_class='btn btn-success btn-lg w-100')
        )
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None



