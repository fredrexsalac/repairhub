from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import AdminUser, Appointment, ClientAccount, ContactMessage, ContactMessageReply


class StyledFieldsMixin:
    css_class = 'input-control'

    def _apply_styles(self):
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing} {self.css_class}'.strip()


class StyledForm(StyledFieldsMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styles()


class StyledModelForm(StyledFieldsMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styles()


class AppointmentForm(StyledModelForm):
    AVAILABILITY_NOTE = (
        'Slots open Mon/Tue/Thu/Fri from 2:00 PM to 4:00 PM. '
        'Wednesdays and Saturdays are open the whole day. Sundays are closed.'
    )
    WEEKLY_AVAILABILITY = {
        0: [(14, 16)],  # Monday
        1: [(14, 16)],  # Tuesday
        2: [(0, 24)],  # Wednesday (whole day)
        3: [(14, 16)],  # Thursday
        4: [(14, 16)],  # Friday
        5: [(0, 24)],  # Saturday (whole day)
        6: [],  # Sunday (closed)
    }

    custom_brand_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
        label='Custom manufacturer (if not listed)',
    )
    proof_image = forms.ImageField(
        required=False,
        label='Photo proof (optional)',
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}),
    )
    device_brand = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
        label='Manufacturer',
    )
    preferred_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    service_type = forms.ChoiceField(choices=[], widget=forms.Select)
    notification_email = forms.EmailField(required=False, label='Email (optional)')
    payment_method = forms.ChoiceField(
        choices=Appointment.PAYMENT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-radio'}),
        initial=Appointment.PAYMENT_PERSONAL,
        label='Payment method',
    )
    accept_booking_policies = forms.BooleanField(
        required=True,
        label='I understand the Terms of Service and Privacy Policy.',
        widget=forms.CheckboxInput(attrs={'class': 'policy-checkbox-input'}),
    )

    class Meta:
        model = Appointment
        fields = [
            'full_name',
            'contact_number',
            'device_type',
            'device_brand',
            'brand_model',
            'service_type',
            'issue_description',
            'proof_image',
            'preferred_datetime',
            'location',
            'location_notes',
            'payment_method',
            'notification_email',
        ]
        widgets = {'issue_description': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['device_type'].choices = Appointment.DEVICE_CHOICES
        self.fields['brand_model'].widget.attrs.setdefault(
            'placeholder', 'e.g. Galaxy A54, Legion 5, etc.'
        )
        self.fields['device_brand'].widget.attrs.setdefault('list', 'brand-options')
        self.fields['device_brand'].widget.attrs.setdefault(
            'placeholder', 'e.g. Infinix, Samsung, Lenovo'
        )
        self.fields['custom_brand_name'].widget.attrs.setdefault(
            'placeholder', 'Type the manufacturer name'
        )
        self.fields['notification_email'].widget.attrs.setdefault(
            'placeholder', 'Optional email for updates'
        )
        self.fields['payment_method'].initial = (
            self.initial.get('payment_method')
            if self.initial
            else Appointment.PAYMENT_PERSONAL
        )
        self.fields['location_notes'].widget.attrs.setdefault(
            'placeholder', 'Optional pickup details if not in a hub'
        )
        device_type = (
            self.data.get('device_type')
            or self.initial.get('device_type')
            if self.initial
            else None
        )
        device_type = device_type or Appointment.DEVICE_ANDROID
        self.fields['service_type'].choices = Appointment.SERVICE_CHOICES.get(device_type, [])

    def clean_preferred_datetime(self):
        preferred = self.cleaned_data['preferred_datetime']
        current_tz = timezone.get_current_timezone()
        if timezone.is_naive(preferred):
            preferred_aware = timezone.make_aware(preferred, current_tz)
        else:
            preferred_aware = preferred

        local_preferred = timezone.localtime(preferred_aware, current_tz)
        if local_preferred < timezone.localtime(timezone.now(), current_tz):
            raise ValidationError('Preferred date and time must be in the future.')

        weekday = local_preferred.weekday()
        windows = self.WEEKLY_AVAILABILITY.get(weekday, [])
        if not windows:
            raise ValidationError('We are closed on Sundays. Please pick another day.')

        hour_value = local_preferred.hour + local_preferred.minute / 60
        is_allowed = any(start <= hour_value < end for start, end in windows)
        if not is_allowed:
            raise ValidationError(self.AVAILABILITY_NOTE)

        return preferred_aware

    def clean_service_type(self):
        service_type = self.cleaned_data['service_type']
        device_type = self.data.get('device_type') or self.cleaned_data.get('device_type')
        allowed_codes = {value for value, _ in Appointment.SERVICE_CHOICES.get(device_type, [])}
        if service_type not in allowed_codes:
            raise ValidationError('Select a service compatible with the chosen device.')
        return service_type

    def clean_device_brand(self):
        device_brand = (self.cleaned_data['device_brand'] or '').strip()
        device_type = self.data.get('device_type') or self.cleaned_data.get('device_type')
        if device_type == Appointment.DEVICE_IPHONE:
            return 'apple'
        choices = Appointment.BRAND_CHOICES.get(device_type, [])
        allowed_values = {value for value, _ in choices}
        normalized = device_brand.lower()
        label_to_value = {label.lower(): value for value, label in choices}
        if not device_brand:
            raise ValidationError('Please enter a manufacturer.')

        resolved_value = None
        if device_brand in allowed_values:
            resolved_value = device_brand
        elif normalized in label_to_value:
            resolved_value = label_to_value[normalized]
        elif normalized in allowed_values:
            resolved_value = normalized

        if resolved_value == 'other':
            custom = (self.cleaned_data.get('custom_brand_name') or '').strip()
            if not custom:
                custom = (self.data.get('custom_brand_name') or '').strip()
            if not custom:
                raise ValidationError('Please type the manufacturer name if it is not listed.')
            self.cleaned_data['custom_brand_name'] = custom
            return custom

        if resolved_value:
            return resolved_value

        return device_brand


class CheckStatusForm(StyledForm):
    appointment_id = forms.CharField(max_length=20, required=False)
    contact_number = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('appointment_id') and not cleaned.get('contact_number') and not cleaned.get('email'):
            raise ValidationError('Provide at least one identifier (tracking number, contact number, or email).')
        return cleaned


class AdminLoginForm(StyledForm):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get('username')
        password = cleaned.get('password')
        if username and password:
            try:
                admin_user = AdminUser.objects.get(username=username)
            except AdminUser.DoesNotExist:
                raise ValidationError('Invalid username or password.')
            if not admin_user.check_password(password):
                raise ValidationError('Invalid password.')
            cleaned['admin_user'] = admin_user
        return cleaned


class AdminRegisterForm(StyledForm):
    full_name = forms.CharField(max_length=150)
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if AdminUser.objects.filter(username__iexact=username).exists():
            raise ValidationError('Username already taken.')
        return username

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm = cleaned.get('confirm_password')
        if password and confirm and password != confirm:
            raise ValidationError('Passwords must match.')
        if password and len(password) < 8:
            raise ValidationError('Use at least 8 characters for the password.')
        return cleaned


class StatusUpdateForm(StyledModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'quoted_price', 'parts_ordered', 'admin_notes']
        widgets = {
            'admin_notes': forms.Textarea(attrs={'rows': 3}),
            'parts_ordered': forms.CheckboxInput(attrs={'class': 'toggle-input'}),
            'quoted_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }


class ClientRegisterForm(StyledForm):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    student_id = forms.CharField(max_length=50, required=False)
    contact_number = forms.CharField(max_length=30)
    school_program = forms.ChoiceField(
        choices=ClientAccount.SCHOOL_PROGRAM_CHOICES,
        label='School program',
    )
    student_type = forms.ChoiceField(
        choices=ClientAccount.STUDENT_TYPE_CHOICES,
        label='Student classification',
    )
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    accept_policies = forms.BooleanField(
        label='I agree to the Terms of Service, Privacy Policy, and Appointment Tracking Policy.',
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'policy-checkbox-input'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if ClientAccount.objects.filter(email__iexact=email).exists():
            raise ValidationError('Email already registered.')
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm = cleaned.get('confirm_password')
        if password and confirm and password != confirm:
            raise ValidationError('Passwords must match.')
        if password and len(password) < 8:
            raise ValidationError('Use at least 8 characters for the password.')
        return cleaned


class ClientLoginForm(StyledForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')
        if email and password:
            try:
                client = ClientAccount.objects.get(email__iexact=email)
            except ClientAccount.DoesNotExist:
                raise ValidationError('Invalid campus email or password.')
            if not client.check_password(password):
                raise ValidationError('Invalid password.')
            cleaned['client'] = client
        return cleaned


class ClientAcademicForm(StyledModelForm):
    class Meta:
        model = ClientAccount
        fields = ['school_program', 'student_type']


class ContactAdminForm(StyledModelForm):
    class Meta:
        model = ContactMessage
        fields = ['subject', 'body', 'preferred_contact']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4}),
        }


class AdminMessageReplyForm(StyledModelForm):
    class Meta:
        model = ContactMessageReply
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a reply…'}),
        }
