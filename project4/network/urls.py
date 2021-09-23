
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("following", views.following, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<str:user_name>", views.user_view, name="user_page"),
    path("post/<int:post_id>/edit", views.post_edit, name="post_edit"),
    path("post/<int:post_id>/like", views.like_post, name="like_post")
]
