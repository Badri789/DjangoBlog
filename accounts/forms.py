from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

from .models import Account


class RegistrationForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ['email', 'username', 'password1', 'password2', 'profile_image']

        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Enter Username...'
            }),

            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter Email...'
            }),

            'profile_image': forms.FileInput(attrs={
                'id': 'input-image'
            })
        }

        labels = {
            'username': 'Username',
            'email': 'Email Address',
            'profile_image': 'Upload Profile Image'
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        # password1 და password2 UserCreationForm-ში შექმნილი ველებია, რადგან ისინი არ ყოფილა
        # Custom User Model-ში. ამის გამო მათი გამოყენება Meta.widgets-ში ან Meta.labels-ში არ გამოვა.
        self.fields['password1'].widget = forms.PasswordInput(attrs={'placeholder': 'Enter Password...'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'placeholder': 'Confirm your Password...'})
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

        self.label_suffix = ''

        # ფორმის ინიციალიზაციისას მის ყველა input-ს ვუნიშნავთ form-control css კლასს
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

        # ვამოწმებთ არის თუ არა ფორმის რომელიმე ველისთვის ვალიდაციის შეცდომები და
        # ვუნიშნავთ is-invalid css კლასს
        if self.errors:
            for error in dict(self.errors):
                self.fields[error].widget.attrs['class'] += ' is-invalid'

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 is not None and password1 != password2:
            msg = "The two password fields didn’t match."
            self.add_error('password1', msg)
            # self.add_error('password2', msg)  ამას ავტომატურად აქვს

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        validate_password(password1)

        return password1

    def clean_profile_image(self):
        profile_image = self.cleaned_data.get('profile_image')
        print(type(profile_image))
        if type(profile_image) != str:
            limit_kb = 500
            min_width = 300
            min_height = 300

            image_size = profile_image.size
            width, height = get_image_dimensions(profile_image)

            if image_size > limit_kb * 1024:
                raise ValidationError(f'Maximum size of the profile image is {limit_kb} KB.')
            elif width < min_width or height < min_height:
                raise ValidationError(
                    f'Ensure that image width is at least {min_width}px and height is at least {min_height}px.'
                )

        return profile_image


class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Email...'
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Password...'
    }))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.label_suffix = ''

        if self.errors:
            for error in dict(self.errors):
                self.fields[error].widget.attrs['class'] += ' is-invalid'


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['profile_image', 'gender', 'first_name', 'last_name', 'user_info']

        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Enter your Last name...'
            }),

            'last_name': forms.TextInput(attrs={
                'placeholder': 'Enter your First name...'
            }),

            'user_info': forms.Textarea(attrs={
                'placeholder': 'Enter info about yourself...'
            }),

            'gender': forms.RadioSelect(
                choices=((False, 'Female'), (True, 'Male'), (None, 'Not set'))
            ),

            'profile_image': forms.FileInput(attrs={
                'id': 'input-image'
            })
        }

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)

        self.label_suffix = ''

        for field in self.fields:
            if field == 'gender':
                self.fields[field].widget.attrs['class'] = 'form-check-input'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'

        if self.errors:
            for error in dict(self.errors):
                self.fields[error].widget.attrs['class'] += ' is-invalid'

    def clean_profile_image(self):
        profile_image = self.cleaned_data.get('profile_image')
        print(type(profile_image))
        if type(profile_image) != str:
            limit_kb = 500
            min_width = 300
            min_height = 300

            image_size = profile_image.size
            width, height = get_image_dimensions(profile_image)

            if image_size > limit_kb * 1024:
                raise ValidationError(f'Maximum size of the profile image is {limit_kb} KB.')
            elif width < min_width or height < min_height:
                raise ValidationError(
                    f'Ensure that image width is at least {min_width}px and height is at least {min_height}px.'
                )

        return profile_image
