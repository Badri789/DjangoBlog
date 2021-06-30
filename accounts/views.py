from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import RegistrationForm, LoginForm, EditProfileForm
from .models import Account


def register(request):
    if request.user.is_authenticated:
        return redirect('blog-main')
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            email = form.cleaned_data['email']
            # password1 = form.cleaned_data['password1']

            # Account Activation
            current_site = get_current_site(request)
            mail_subject = "Please verify your Badri's Blog account"
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # account = authenticate(request, email=email, password=password1)
            # login(request, account)
            messages.warning(request, f'Verification link was sent on email {to_email}! Please verify to proceed!',
                             extra_tags='bi bi-exclamation-circle-fill')
            return redirect('blog-main')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('blog-main')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            account = authenticate(request, email=email, password=password)
            if account is not None:
                login(request, account)
                messages.success(request, 'You logged in successfully!', extra_tags='bi bi-check-circle-fill')
                return redirect('blog-main')
            else:
                messages.error(request, 'Invalid login credentials!', extra_tags='bi bi-x-circle-fill')
                return redirect('login')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {
        'form': form
    })


def logout_view(request):
    logout(request)
    return redirect('blog-main')


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations, your email is verified! Please Log in to proceed.',
                         extra_tags='bi bi-check-circle-fill')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link!', extra_tags='bi bi-x-circle-fill')
        return redirect('blog-main')


def user_profile(request, username):
    user = Account.objects.get(username=username)
    username = user.username
    profile_image = user.profile_image
    post_count = user.post_set.count()
    comment_count = user.comment_set.count()
    first_name = user.first_name if user.first_name is not None else 'Not set'
    last_name = user.last_name if user.last_name is not None else 'Not set'
    date_joined = user.date_joined
    gender = user.get_gender_display()
    user_info = user.user_info if user.user_info is not None else 'Not set'

    return render(request, 'accounts/user_profile.html', {
        'username': username,
        'profile_image': profile_image,
        'post_count': post_count,
        'comment_count': comment_count,
        'first_name': first_name,
        'last_name': last_name,
        'date_joined': date_joined,
        'gender': gender,
        'user_info': user_info
    })


@login_required(login_url='/login')
def edit_profile(request, username):
    user = Account.objects.get(username=username)
    if request.user != user and not request.user.is_superuser:
        return HttpResponse("You cannot edit other user's profile!")
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', username=username)
    else:
        form = EditProfileForm(instance=user, initial={'profile_image': user.profile_image})

    return render(request, 'accounts/edit_profile.html', {
        'form': form
    })
