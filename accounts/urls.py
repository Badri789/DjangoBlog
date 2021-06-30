from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>', views.activate_account, name='activate-account'),
    path('profile/<str:username>', views.user_profile, name='user-profile'),
    path('profile/<str:username>/edit', views.edit_profile, name='edit-profile'),
]
