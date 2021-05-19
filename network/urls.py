
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("all-posts/<int:page>", views.all_posts, name="all-posts"),
    path("user-posts/<str:user>/<int:page>", views.user_posts, name="user-posts"),
    path("following/<int:page>", views.following, name="following"),

    path("edit/<int:post_id>", views.edit, name="edit"),
    path("new-post", views.new_post, name="new-post"),

    path("following", views.follow_page, name="follow-page"),
    path("profile/<str:profile_user>", views.profile, name="profile"),

    path("follow/<str:user>", views.follow, name="follow"),
    path("unfollow/<str:user>", views.unfollow, name="unfollow"),
    path("like/<int:post_id>", views.like, name="like")
]
