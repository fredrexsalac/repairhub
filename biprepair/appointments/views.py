from __future__ import annotations

import json
from functools import wraps

from django.contrib import messages
from django.db.models import Count, Sum, Max, Q
from django.db.models.functions import TruncMonth
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.templatetags.static import static

from .constants import POLICIES_VERSION, SESSION_ADMIN_KEY, SESSION_CLIENT_KEY
from .forms import (
    AdminLoginForm,
    AdminRegisterForm,
    AppointmentForm,
    CheckStatusForm,
    ClientAcademicForm,
    ClientLoginForm,
    ClientRegisterForm,
    ContactAdminForm,
    AdminMessageReplyForm,
    StatusUpdateForm,
)
from .models import AdminUser, Appointment, ClientAccount, ContactMessage

SESSION_ADMIN_KEY = 'admin_user_id'
SESSION_CLIENT_KEY = 'client_user_id'


def _service_map():
    return {
        key: [{'value': value, 'label': label} for value, label in choices]
        for key, choices in Appointment.SERVICE_CHOICES.items()
    }


def _brand_map():
    return {
        key: [{'value': value, 'label': label} for value, label in choices]
        for key, choices in Appointment.BRAND_CHOICES.items()
    }


def _model_map():
    return Appointment.MODEL_SUGGESTIONS


def service_worker(_request: HttpRequest) -> HttpResponse:
    shell_urls = json.dumps(
        [
            '/',
            '/admin',
            static('css/styles.css'),
            static('js/app.js'),
            static('image/Birepair.png'),
        ]
    )
    payload = f"""
const CACHE_NAME = 'biprepair-cache-v1';
const APP_SHELL = {shell_urls};

self.addEventListener('install', (event) => {{
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())
  );
}});

self.addEventListener('activate', (event) => {{
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
}});

self.addEventListener('fetch', (event) => {{
  const request = event.request;
  if (request.method !== 'GET') return;
  event.respondWith(
    caches.match(request).then((cached) => {{
      if (cached) {{
        return cached;
      }}
      return fetch(request)
        .then((response) => {{
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          return response;
        }})
        .catch(() => cached);
    }})
  );
}});
"""
    response = HttpResponse(payload.strip(), content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    return response


def _earning_queryset():
    return Appointment.objects.filter(
        Q(status=Appointment.STATUS_COMPLETED) | Q(status=Appointment.STATUS_APPROVED)
    )


def _get_logged_admin(request: HttpRequest) -> AdminUser | None:
    admin_id = request.session.get(SESSION_ADMIN_KEY)
    if not admin_id:
        return None
    try:
        return AdminUser.objects.get(id=admin_id)
    except AdminUser.DoesNotExist:
        return None


def _get_logged_client(request: HttpRequest) -> ClientAccount | None:
    client_id = request.session.get(SESSION_CLIENT_KEY)
    if not client_id:
        return None
    try:
        return ClientAccount.objects.get(id=client_id)
    except ClientAccount.DoesNotExist:
        return None


def _style_contact_admin_form(form: ContactAdminForm) -> None:
    form.fields['subject'].widget.attrs['placeholder'] = 'Subject or topic'
    form.fields['body'].widget.attrs['placeholder'] = 'Write your message…'
    form.fields['body'].widget.attrs.setdefault('rows', 3)
    form.fields['preferred_contact'].widget.attrs.setdefault('class', 'composer-select')


def _admin_profiles_with_primary():
    admin_profiles = []
    status_palette = [
        {'label': 'Online now', 'tone': 'online'},
        {'label': 'Replying soon', 'tone': 'soon'},
        {'label': 'Away · leave a note', 'tone': 'away'},
    ]
    for idx, admin in enumerate(AdminUser.objects.all().order_by('full_name')):
        initials = ''.join(part[0] for part in admin.full_name.split()[:2]).upper() or admin.full_name[:2].upper()
        status = status_palette[idx % len(status_palette)]
        admin_profiles.append(
            {
                'name': admin.full_name,
                'handle': admin.username,
                'initials': initials,
                'status_label': status['label'],
                'status_tone': status['tone'],
            }
        )
    primary_admin = admin_profiles[0] if admin_profiles else None
    return admin_profiles, primary_admin


def home(request: HttpRequest) -> HttpResponse:
    context = {
        'service_map': _service_map(),
        'brand_map': _brand_map(),
        'model_map': _model_map(),
        'device_choices': Appointment.DEVICE_CHOICES,
        'blocked_notice': 'iPhone battery issues are NOT accepted. No soldering / board-level repairs.',
    }
    return render(request, 'home.html', context)


def _client_guard(view_func):
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        client = _get_logged_client(request)
        if not client:
            return redirect(f"{reverse('client_login')}?next={request.path}")
        request.client_user = client  # type: ignore[attr-defined]
        return view_func(request, *args, **kwargs)

    return wrapper


@_client_guard
def book_appointment(request: HttpRequest) -> HttpResponse:
    client = request.client_user  # type: ignore[attr-defined]
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = client
            appointment.full_name = client.full_name
            appointment.contact_number = client.contact_number
            if not appointment.notification_email:
                appointment.notification_email = client.email
            if not appointment.quoted_price:
                appointment.quoted_price = appointment.service_price
            appointment.policies_accepted_at = timezone.now()
            appointment.policies_version = POLICIES_VERSION
            appointment.save()
            messages.success(
                request,
                f'Appointment submitted! Your ID is {appointment.appointment_id}. '
                'Expect confirmation via SMS.',
            )
            return redirect('check_status')
    else:
        form = AppointmentForm(
            initial={
                'full_name': client.full_name,
                'contact_number': client.contact_number,
                'notification_email': client.email,
                'payment_method': Appointment.PAYMENT_PERSONAL,
            }
        )
    context = {
        'form': form,
        'service_map_json': json.dumps(_service_map()),
        'brand_map_json': json.dumps(_brand_map()),
        'model_map_json': json.dumps(_model_map()),
        'service_pricing_json': json.dumps(Appointment.SERVICE_PRICING),
        'blocked_notice': 'No iPhone battery fixes. No board-level / soldering requests.',
        'client_user': client,
    }
    return render(request, 'book.html', context)


def check_status(request: HttpRequest) -> HttpResponse:
    results = None
    client = _get_logged_client(request)
    client_appointments = None
    mask_tracking = False
    if client:
        client_appointments = client.appointments.order_by('-created_at')
    if request.method == 'POST':
        form = CheckStatusForm(request.POST)
        if form.is_valid():
            mask_tracking = not bool(form.cleaned_data['appointment_id'])
            filters = {}
            if form.cleaned_data['appointment_id']:
                filters['appointment_id__iexact'] = form.cleaned_data['appointment_id']
            if form.cleaned_data['contact_number']:
                filters['contact_number__iexact'] = form.cleaned_data['contact_number']
            if form.cleaned_data.get('email'):
                filters['notification_email__iexact'] = form.cleaned_data['email']
            results = Appointment.objects.filter(**filters)
            if not results.exists():
                messages.warning(request, 'No appointments found. Please double-check your details.')
    else:
        form = CheckStatusForm()
    return render(
        request,
        'status.html',
        {
            'form': form,
            'results': results,
            'client_appointments': client_appointments,
            'client_user': client,
            'mask_tracking': mask_tracking,
        },
    )


def admin_login(request: HttpRequest) -> HttpResponse:
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('admin_dashboard')
    if _get_logged_admin(request):
        return redirect(next_url)

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            admin_user = form.cleaned_data['admin_user']
            request.session[SESSION_ADMIN_KEY] = admin_user.id
            messages.success(request, 'Welcome back!')
            return redirect(next_url)
    else:
        form = AdminLoginForm()
    return render(request, 'admin_login.html', {'form': form, 'next_url': next_url})


def admin_logout(request: HttpRequest) -> HttpResponse:
    request.session.pop(SESSION_ADMIN_KEY, None)
    messages.info(request, 'You have been logged out.')
    return redirect('admin_login')


def admin_register(request: HttpRequest) -> HttpResponse:
    if _get_logged_admin(request):
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AdminRegisterForm(request.POST)
        if form.is_valid():
            admin = AdminUser(
                username=form.cleaned_data['username'],
                full_name=form.cleaned_data['full_name'],
            )
            admin.set_password(form.cleaned_data['password'])
            admin.save()
            messages.success(request, 'Technician account created. You can now sign in.')
            return redirect('admin_login')
    else:
        form = AdminRegisterForm()
    return render(request, 'admin_register.html', {'form': form})


def admin_guard(view_func):
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        admin_user = _get_logged_admin(request)
        if not admin_user:
            return redirect(f"{reverse('admin_login')}?next={request.path}")
        request.admin_user = admin_user  # type: ignore[attr-defined]
        return view_func(request, *args, **kwargs)

    return wrapper


def _monthly_series(queryset, value_field: str | None = None):
    if value_field:
        data = (
            queryset.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum(value_field))
            .order_by('month')
        )
        return [
            {'label': item['month'].strftime('%b %Y'), 'value': float(item['total'] or 0)}
            for item in data
        ]
    data = (
        queryset.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )
    return [
        {'label': item['month'].strftime('%b %Y'), 'value': item['total']}
        for item in data
    ]


@admin_guard
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    earning_qs = _earning_queryset()
    total_earnings = earning_qs.aggregate(total=Sum('quoted_price'))['total'] or 0
    total_clients = ClientAccount.objects.filter(is_active=True).count()
    total_appointments = Appointment.objects.count()
    monthly_earnings = _monthly_series(earning_qs, 'quoted_price')
    monthly_appointments = _monthly_series(Appointment.objects.all())
    return render(
        request,
        'admin_home.html',
        {
            'admin_user': request.admin_user,
            'total_earnings': total_earnings,
            'total_clients': total_clients,
            'total_appointments': total_appointments,
            'monthly_earnings': json.dumps(monthly_earnings),
            'monthly_appointments': json.dumps(monthly_appointments),
        },
    )


@admin_guard
def admin_appointments(request: HttpRequest) -> HttpResponse:
    appointments = Appointment.objects.all()
    status_filter = request.GET.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    contact_messages = ContactMessage.objects.select_related('client').all()[:10]
    return render(
        request,
        'admin_dashboard.html',
        {
            'appointments': appointments,
            'status_choices': Appointment.STATUS_CHOICES,
            'admin_user': request.admin_user,
            'contact_messages': contact_messages,
        },
    )


@admin_guard
def admin_messages(request: HttpRequest) -> HttpResponse:
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    message_qs = ContactMessage.objects.select_related('client').order_by('-updated_at')
    if search_query:
        message_qs = message_qs.filter(
            Q(client__full_name__icontains=search_query)
            | Q(client__email__icontains=search_query)
            | Q(subject__icontains=search_query)
        )
    if status_filter:
        message_qs = message_qs.filter(status=status_filter)

    status_counts = (
        ContactMessage.objects.values('status')
        .annotate(total=Count('id'))
        .order_by()
    )
    status_totals = {item['status']: item['total'] for item in status_counts}
    statuses = [
        {
            'value': value,
            'label': label,
            'count': status_totals.get(value, 0),
        }
        for value, label in ContactMessage.STATUS_CHOICES
    ]

    conversation_list = []
    seen_clients: set[int] = set()
    for message in message_qs:
        client_id = message.client_id
        if client_id in seen_clients:
            continue
        seen_clients.add(client_id)
        conversation_list.append(message)

    return render(
        request,
        'admin_messages.html',
        {
            'admin_user': request.admin_user,
            'conversation_list': conversation_list,
            'status_choices': ContactMessage.STATUS_CHOICES,
            'status_filter': status_filter,
            'search_query': search_query,
            'statuses': statuses,
        },
    )
def admin_message_detail(request: HttpRequest, message_id: int) -> HttpResponse:
    contact_message = get_object_or_404(
        ContactMessage.objects.select_related('client').prefetch_related('replies__admin'),
        pk=message_id,
    )
    client = contact_message.client
    thread_messages = (
        client.contact_messages.select_related('client')
        .prefetch_related('replies__admin')
        .order_by('created_at')
    )
    active_message = thread_messages.last() or contact_message

    form = AdminMessageReplyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        target_id = request.POST.get('message_id')
        target_message = None
        if target_id and target_id.isdigit():
            target_message = thread_messages.filter(pk=int(target_id)).first()
        if not target_message:
            target_message = active_message
        reply = form.save(commit=False)
        reply.message = target_message
        reply.admin = request.admin_user
        reply.save()
        target_message.admin_reply = reply.body
        target_message.save(update_fields=['admin_reply', 'updated_at'])
        messages.success(request, 'Reply sent.')
        return redirect('admin_message_detail', message_id=message_id)

    client_initials = (
        ''.join(part[0] for part in client.full_name.split()[:2]).upper()
        if client and client.full_name
        else 'CL'
    )
    admin_initials = (
        ''.join(part[0] for part in request.admin_user.full_name.split()[:2]).upper()
        if request.admin_user.full_name
        else 'AD'
    )

    return render(
        request,
        'admin_message_detail.html',
        {
            'admin_user': request.admin_user,
            'contact_message': contact_message,
            'form': form,
            'client_initials': client_initials,
            'admin_initials': admin_initials,
            'thread_messages': thread_messages,
            'active_message': active_message,
        },
    )


@admin_guard
def admin_message_detail(request: HttpRequest, message_id: int) -> HttpResponse:
    contact_message = get_object_or_404(
        ContactMessage.objects.select_related('client'),
        pk=message_id,
    )
    client = contact_message.client
    thread_messages = (
        client.contact_messages.select_related('client')
        .prefetch_related('replies__admin')
        .order_by('created_at')
    )
    active_message = thread_messages.last() or contact_message

    form = AdminMessageReplyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        target_id = request.POST.get('message_id')
        target_message = None
        if target_id and target_id.isdigit():
            target_message = thread_messages.filter(pk=int(target_id)).first()
        if not target_message:
            target_message = active_message
        reply = form.save(commit=False)
        reply.message = target_message
        reply.admin = request.admin_user
        reply.save()
        target_message.admin_reply = reply.body
        target_message.save(update_fields=['admin_reply', 'updated_at'])
        messages.success(request, 'Reply sent.')
        return redirect('admin_message_detail', message_id=message_id)

    client_initials = (
        ''.join(part[0] for part in client.full_name.split()[:2]).upper()
        if client and client.full_name
        else 'CL'
    )
    admin_initials = (
        ''.join(part[0] for part in request.admin_user.full_name.split()[:2]).upper()
        if request.admin_user.full_name
        else 'AD'
    )

    return render(
        request,
        'admin_message_detail.html',
        {
            'admin_user': request.admin_user,
            'contact_message': contact_message,
            'form': form,
            'client_initials': client_initials,
            'admin_initials': admin_initials,
            'thread_messages': thread_messages,
            'active_message': active_message,
        },
    )


@admin_guard
def admin_detail(request: HttpRequest, appointment_id: str) -> HttpResponse:
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
    is_locked = appointment.is_management_locked
    if request.method == 'POST':
        if is_locked:
            messages.warning(
                request,
                'This appointment is locked because it was marked completed, rejected, or already has parts ordered.',
            )
            return redirect('admin_detail', appointment_id=appointment_id)
        form = StatusUpdateForm(request.POST, instance=appointment)
        if form.is_valid():
            updated = form.save(commit=False)
            if updated.status == Appointment.STATUS_DECLINED and 'unsupported' not in updated.admin_notes.lower():
                updated.admin_notes = f'Unsupported: {updated.admin_notes}'
            updated.save()
            if updated.is_management_locked:
                messages.info(request, 'Appointment locked. Replacement parts ordered and approval recorded.')
            messages.success(request, 'Appointment updated successfully.')
            return redirect('admin_detail', appointment_id=appointment_id)
    else:
        form = StatusUpdateForm(instance=appointment)
        if appointment.service_price and not appointment.quoted_price:
            form.initial['quoted_price'] = appointment.service_price
    if is_locked:
        for field in form.fields.values():
            field.disabled = True
    return render(
        request,
        'admin_detail.html',
        {
            'appointment': appointment,
            'form': form,
            'admin_user': request.admin_user,
            'is_locked': is_locked,
        },
    )


@admin_guard
def admin_clients(request: HttpRequest) -> HttpResponse:
    clients = (
        ClientAccount.objects.annotate(appointment_count=Count('appointments'))
        .order_by('full_name')
        .all()
    )
    return render(
        request,
        'admin_clients.html',
        {
            'clients': clients,
            'admin_user': request.admin_user,
        },
    )


@admin_guard
def admin_client_detail(request: HttpRequest, client_id: int) -> HttpResponse:
    client = get_object_or_404(ClientAccount, pk=client_id)
    academic_form = ClientAcademicForm(instance=client)
    if request.method == 'POST' and request.POST.get('update_academic'):
        academic_form = ClientAcademicForm(request.POST, instance=client)
        if academic_form.is_valid():
            academic_form.save()
            messages.success(request, 'Academic information updated.')
            return redirect('admin_client_detail', client_id=client_id)
    if request.method == 'POST' and request.POST.get('toggle_status'):
        client.is_active = request.POST['toggle_status'] == 'activate'
        client.save(update_fields=['is_active'])
        messages.success(request, 'Client status updated.')
        return redirect('admin_client_detail', client_id=client_id)
    if request.method == 'POST' and request.POST.get('reset_password'):
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(new_password) < 8:
            messages.error(request, 'Use at least 8 characters for the password.')
        else:
            client.set_password(new_password)
            client.save(update_fields=['password'])
            messages.success(request, 'Client password updated.')
            return redirect('admin_client_detail', client_id=client_id)
    appointments = client.appointments.order_by('-created_at')
    return render(
        request,
        'admin_client_detail.html',
        {
            'client': client,
            'appointments': appointments,
            'academic_form': academic_form,
            'admin_user': request.admin_user,
        },
    )


@admin_guard
def admin_settings(request: HttpRequest) -> HttpResponse:
    admin_user = request.admin_user
    if request.method == 'POST' and request.POST.get('update_profile'):
        full_name = request.POST.get('full_name', '').strip()
        username = request.POST.get('username', '').strip()
        if not full_name or not username:
            messages.error(request, 'Full name and username are required.')
        elif AdminUser.objects.filter(username__iexact=username).exclude(id=admin_user.id).exists():
            messages.error(request, 'Username already taken.')
        else:
            admin_user.full_name = full_name
            admin_user.username = username
            admin_user.save(update_fields=['full_name', 'username'])
            messages.success(request, 'Profile updated.')
            return redirect('admin_settings')
    if request.method == 'POST' and request.POST.get('change_password'):
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        if not admin_user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password) < 8:
            messages.error(request, 'Use at least 8 characters for the password.')
        else:
            admin_user.set_password(new_password)
            admin_user.save(update_fields=['password'])
            messages.success(request, 'Password updated.')
            return redirect('admin_settings')
    return render(
        request,
        'admin_settings.html',
        {'admin_user': admin_user},
    )


def terms_of_service(request: HttpRequest) -> HttpResponse:
    return render(request, 'tos.html')


def privacy_policy(request: HttpRequest) -> HttpResponse:
    return render(request, 'privacy.html')


def tracking_policy(request: HttpRequest) -> HttpResponse:
    return render(request, 'tracking.html')


def client_login(request: HttpRequest) -> HttpResponse:
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('book_appointment')
    if _get_logged_client(request):
        return redirect(next_url)

    if request.method == 'POST':
        form = ClientLoginForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data['client']
            request.session[SESSION_CLIENT_KEY] = client.id
            messages.success(request, 'Signed in successfully.')
            return redirect(next_url)
    else:
        form = ClientLoginForm()
    return render(request, 'client_login.html', {'form': form, 'next_url': next_url})


def client_logout(request: HttpRequest) -> HttpResponse:
    request.session.pop(SESSION_CLIENT_KEY, None)
    messages.info(request, 'Signed out.')
    return redirect('home')


def client_register(request: HttpRequest) -> HttpResponse:
    if _get_logged_client(request):
        return redirect('book_appointment')

    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            client = ClientAccount(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'].lower(),
                student_id=form.cleaned_data.get('student_id', ''),
                contact_number=form.cleaned_data['contact_number'],
                school_program=form.cleaned_data['school_program'],
                student_type=form.cleaned_data['student_type'],
            )
            client.set_password(form.cleaned_data['password'])
            client.policies_accepted_at = timezone.now()
            client.policies_version = POLICIES_VERSION
            client.save()
            request.session[SESSION_CLIENT_KEY] = client.id
            messages.success(request, 'Account created. You are now signed in.')
            return redirect('book_appointment')
    else:
        form = ClientRegisterForm()
    return render(request, 'client_register.html', {'form': form})


@_client_guard
def contact_admin(request: HttpRequest) -> HttpResponse:
    client = request.client_user  # type: ignore[attr-defined]
    default_subject = 'Messenger conversation'
    default_channel = ContactMessage.PREFERRED_CHOICES[0][0]
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data.setdefault('subject', default_subject)
        post_data.setdefault('preferred_contact', default_channel)
        form = ContactAdminForm(post_data, request.FILES)
        _style_contact_admin_form(form)
        if form.is_valid():
            message = form.save(commit=False)
            message.client = client
            message.save()
            messages.success(request, 'Message sent to the repair crew.')
            return redirect('contact_admin')
    else:
        form = ContactAdminForm(initial={'subject': default_subject, 'preferred_contact': default_channel})
        _style_contact_admin_form(form)
    history = client.contact_messages.order_by('created_at').prefetch_related('replies__admin')
    admin_profiles, primary_admin = _admin_profiles_with_primary()
    client_initials = ''.join(part[0] for part in client.full_name.split()[:2]).upper() or client.full_name[:2].upper()
    return render(
        request,
        'contact_admin.html',
        {
            'form': form,
            'messages_history': history,
            'client_user': client,
            'admin_profiles': admin_profiles,
            'primary_admin': primary_admin,
            'client_initials': client_initials,
        },
    )


@_client_guard
def contact_admin_history(request: HttpRequest) -> JsonResponse:
    client = request.client_user  # type: ignore[attr-defined]
    messages_qs = client.contact_messages.order_by('created_at').prefetch_related('replies__admin')
    admin_profiles, primary_admin = _admin_profiles_with_primary()
    payload = []
    for message in messages_qs:
        replies = []
        for reply in message.replies.select_related('admin').all():
            admin = reply.admin
            replies.append(
                {
                    'body': reply.body,
                    'created_display': reply.created_at.strftime('%b %d, %Y · %I:%M %p'),
                    'created_iso': reply.created_at.isoformat(),
                    'admin_initials': (
                        ''.join(part[0] for part in admin.full_name.split()[:2]).upper()
                        if admin and admin.full_name
                        else 'RC'
                    ),
                    'admin_name': admin.full_name if admin else 'Repair Crew',
                }
            )
        payload.append(
            {
                'id': message.id,
                'subject': message.subject,
                'body': message.body,
                'status': message.status,
                'status_display': message.get_status_display(),
                'preferred_contact_display': message.get_preferred_contact_display(),
                'created_display': message.created_at.strftime('%b %d, %Y · %I:%M %p'),
                'created_iso': message.created_at.isoformat(),
                'updated_display': message.updated_at.strftime('%b %d, %Y · %I:%M %p'),
                'updated_iso': message.updated_at.isoformat(),
                'admin_reply': message.admin_reply,
                'replies': replies,
            }
        )
    admin_meta = {
        'initials': primary_admin['initials'] if primary_admin else 'RC',
        'name': primary_admin['name'] if primary_admin else 'Repair Crew',
    }
    return JsonResponse({'messages': payload, 'admin': admin_meta})
