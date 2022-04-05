from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation, forms as auth_forms
from accounts.models import MyUser
from django.utils.translation import gettext_lazy as _



class PasswordWidget(forms.PasswordInput):
    template_name = 'widgets/password.html'


def bootstrap_helptext():
    html = password_validation.password_validators_help_text_html()
    html = '<div class="alert alert-warning" role="alert">' + html + '</div>'
    return html


def add_class_to_widget(widget, name):
    if 'class' not in widget.attrs:
        widget.attrs.update({'class': ''})
    widget.attrs.update({'class': widget.attrs['class'] + ' ' + name})


def add_bootstrap_validation(form):
    for field in form.fields:
        print(field, form.has_error(field))
        if form.has_error(field):
            add_class_to_widget(form.fields[field].widget, 'is-invalid')
        else:
            add_class_to_widget(form.fields[field].widget, 'is-valid')


class SignupForm(auth_forms.UserCreationForm):
    class Meta:
        model = MyUser
        fields = ('username', 'email', 'password1', 'password2')

    username = auth_forms.UsernameField(
        label=_("Username"),
        strip=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    email = forms.EmailField(
        label=_("Email"),
        max_length=200,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=PasswordWidget(attrs={'class': 'form-control'}),
        help_text=bootstrap_helptext(),
    )

    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=PasswordWidget(attrs={'class': 'form-control'}),
        strip=False,
    )

    def clean(self):
        data = super().clean()
        return data

    def is_valid(self):
        valid = super(SignupForm, self).is_valid()
        add_bootstrap_validation(self)
        return valid
