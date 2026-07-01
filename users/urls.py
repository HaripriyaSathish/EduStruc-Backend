from django.urls import path
from . import views
from .views import forgot_password, reset_password

urlpatterns = [
    path('register/',           views.register,          name='register'),
    path('login/',              views.login,             name='login'),
    path('profile/',            views.profile,           name='profile'),
    path('avatar/',             views.upload_avatar,     name='upload-avatar'),
    path('change-password/',    views.change_password,   name='change-password'),
    path('toggle-2fa/',         views.toggle_2fa,        name='toggle-2fa'),
    path('deactivate/',         views.deactivate_account,name='deactivate'),
    path('logout/',             views.logout,            name='logout'),
    path('users/<str:role>/',   views.users_by_role,     name='users-by-role'),
    path('forgot-password/',    forgot_password,         name='forgot-password'),
    path('reset-password/<str:uid>/<str:token>/', reset_password, name='reset-password'),
]