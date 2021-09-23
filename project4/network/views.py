from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json

from .models import User, Post


def index(request):
    posts_per_page = 10
    post_list = Post.objects.all()

    paginator = Paginator(post_list, posts_per_page)
    get_page = request.GET.get('p')
    page_number = get_page if get_page is not None else 1
    current_page = paginator.get_page(page_number)

    context = {
        "current_page": current_page,
        "pagination_needed": paginator.num_pages > 1
    }

    if request.method == "POST":
        # attempt to send new post
        post_body = request.POST["post-text"]

        if len(post_body) > 0:
            post = Post(user=request.user, content=post_body)
            post.save()

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


def following(request):
    followed_users = User.objects.filter(followers=request.user)
    posts_by_followed = Post.objects.filter(user__in=followed_users)

    context = {
        "posts": posts_by_followed
    }

    return render(request, "network/following.html", context)


def post_edit(request, post_id):
    if request.method == "POST":
        # get post with that id
        post = Post.objects.filter(id=post_id)

        # check if that post exist
        if len(post) == 1:
            post_to_edit = post[0]
            read_json = json.loads(request.body)
            post_to_edit.content = read_json['edited_text']
            post_to_edit.save()
            return HttpResponse(200)

    return HttpResponse(404)


def like_post(request, post_id):
    if request.method == "POST":
        # get post with that id
        post = Post.objects.filter(id=post_id)

        # check if that post exist
        if len(post) == 1:
            post_to_edit = post[0]
            read_json = json.loads(request.body)
            # determine if post is to be liked or unlike
            action = read_json['action']

            # check if post is liked by requesting user
            post_is_liked = request.user in post_to_edit.liked_by.all()

            if action == "like" and not post_is_liked:
                post_to_edit.liked_by.add(request.user)
                post_to_edit.save()
            elif post_is_liked:
                post_to_edit.liked_by.remove(request.user)
                post_to_edit.save()

            like_count = post_to_edit.count_likes()
            like_status = request.user in post_to_edit.liked_by.all()

            response = {'like_count': like_count,
                        'like_status': like_status}

            return JsonResponse(response)

    return HttpResponse(404)
