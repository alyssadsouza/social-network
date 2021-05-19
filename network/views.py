import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, UserFollow, Like



def index(request):
    if request.method == "POST" and request.POST["new-post-content"] != '':
        post = Post(poster=request.user, content=request.POST["new-post-content"])
        post.save()
    
    # Find number of pages of posts
    posts = Post.objects.all().order_by("-timestamp").all()
    p = Paginator(posts, 10)
    pages = p.num_pages

    return render(request, "network/index.html",{
        "page":1,
        "pages":pages
        })

def all_posts(request, page):
    posts = Post.objects.all().order_by("-timestamp").all()

    # Display 10 posts on each page
    p = Paginator(posts, 10)
    posts = p.get_page(page)

    return JsonResponse([post.serialize() for post in posts], safe=False)

def user_posts(request, user, page):
    posts = Post.objects.filter(poster=User.objects.get(username=user)).order_by("-timestamp").all()
    
    p = Paginator(posts, 10)
    posts = p.get_page(page)

    return JsonResponse([post.serialize() for post in posts], safe=False)

@login_required
def following(request, page):
    my_following = [user.following for user in UserFollow.objects.filter(user=request.user)]
    posts = []
    for user in my_following:
        posts += Post.objects.filter(poster=User.objects.get(username=user)).order_by("-timestamp").all()
    
    p = Paginator(posts, 10)
    posts = p.get_page(page)

    return JsonResponse([post.serialize() for post in posts], safe=False)

@csrf_exempt
@login_required
def new_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    post = Post(poster=request.user, content=data.get("content", ""))
    post.save()

    return JsonResponse({"message": "Post saved."}, status=201)



@csrf_exempt
@login_required
def edit(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    post = Post.objects.get(pk=int(post_id))

    # Get contents of post
    content = data.get("content", "")
    edited = data.get("edited", "")

    post.content = content
    post.edited = edited
    post.save()

    return JsonResponse({"message": "Post saved."}, status=201)

@login_required
def follow_page(request):
    my_following = [user.following for user in UserFollow.objects.filter(user=request.user)]
    posts = []
    for user in my_following:
        posts += Post.objects.filter(poster=User.objects.get(username=user)).order_by("-timestamp").all()
    
    # Find number of pages of posts
    p = Paginator(posts, 10)
    pages = p.num_pages

    return render(request, "network/following.html",{
        "page":1,
        "pages":pages
    })


def profile(request, profile_user):

    profile_user = User.objects.get(username=profile_user)
    following = list(UserFollow.objects.filter(user=profile_user))
    followers = list(UserFollow.objects.filter(following=profile_user))

    # Find number of pages of posts
    posts = Post.objects.filter(poster=profile_user).order_by("-timestamp").all()
    p = Paginator(posts, 10)
    pages = p.num_pages

    if request.user.is_anonymous:
        can_follow, can_unfollow = False, False
    else:
        # Get list of accounts current user is following
        my_following = [user.following for user in UserFollow.objects.filter(user=request.user)]

        can_follow = request.user != profile_user and profile_user not in my_following
        can_unfollow = request.user != profile_user and profile_user in my_following

    return render(request, "network/profile.html", {
        "profile_user":profile_user.username,
        "following":len(following),
        "followers":len(followers),
        "can_follow":can_follow,
        "can_unfollow":can_unfollow,
        "page":1,
        "pages":pages
    })

@login_required
def like(request, post_id):
    post = Post.objects.get(pk=int(post_id))

    try:
        like = Like.objects.get(post=post, user=request.user)
    except Like.DoesNotExist:
        like = Like(post=post, user=request.user)
        like.save()
        post.likes += 1
        post.save()
    else:
        like.delete()
        post.likes -= 1
        post.save()

    return JsonResponse(post.serialize(), safe=False)

@login_required
def follow(request, user):
    follow = UserFollow(user=request.user, following=User.objects.get(username=user))
    follow.save()
    return redirect("profile",user)

@login_required
def unfollow(request, user):
    follow = UserFollow.objects.get(user=request.user, following=User.objects.get(username=user))
    follow.delete()
    return redirect("profile",user)

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
