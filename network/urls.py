
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("profile", views.profile, name="profile"),
    path("profile<int:id>", views.users_profile, name="users_profile"),
    path("following", views.following, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    

    # API Routes
    path("follow/<int:user_id>", views.follow, name="follow"),
    path("like/<int:post_id>", views.like, name="like"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post")
]
