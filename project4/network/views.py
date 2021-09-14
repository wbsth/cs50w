from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post


def index(request):

    context = {
        "posts": Post.objects.all()
    }

    if request.method == "POST":
        # attempt to send new post
        post_body = request.POST["post-text"]

        if len(post_body) > 0:
            post = Post(user=request.user, content=post_body)
            post.save()

        return render(request, "network/index.html", context)

    else:
        return render(request, "network/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def user_view(request, user_name):
    user_profile = User.objects.get(username=user_name)
    current_user = request.user

    if request.method == "POST":
        # check the status
        status = request.POST['follow-button']
        if status == 'Unfollow':
            user_profile.followers.remove(current_user)
        elif status == 'Follow':
            user_profile.followers.add(current_user)
        pass

    # determine follow button visibility
    follow_button_visibility = request.user.is_authenticated and request.user.username != user_name

    # determine follow button text
    if current_user in user_profile.followers.all():
        follow_text = 'Unfollow'
    else:
        follow_text = 'Follow'

    # determine followers and follower count
    followers_count = user_profile.count_followers()
    following_count = user_profile.count_following()

    context = {
        'user_name': user_name,
        'following': following_count,
        'followers': followers_count,
        'posts': Post.objects.filter(user__username=user_name),
        'follow_button_visible': follow_button_visibility,
        'follow_text': follow_text
    }
    
    return render(request, 'network/user_view.html', context)
