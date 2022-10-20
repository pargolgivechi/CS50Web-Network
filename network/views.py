import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.db.models import OuterRef, Count
from django.core.paginator import Paginator

from .forms import *
from .models import *


def index(request):
    if request.user.is_authenticated:
        user = request.user
        likes = Like.objects.filter(post=OuterRef('id'), user=user)
        posts = Post.objects.all().order_by('date').annotate(user_likes=Count(likes.values('id'))).reverse()

        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        pages = paginator.get_page(page_number)
    
        if request.method == "POST":

            if 'post' in request.POST:
                form = PostForm(request.POST)
                if form.is_valid():
                    newPost = form.save(commit=False)
                    newPost.user = request.user
                    newPost.save()
                return HttpResponseRedirect(reverse("index"))

    else:

        posts = Post.objects.all().order_by('date').reverse()

        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        pages = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "form": PostForm,
        "posts": pages
    })


def profile(request):
    user = request.user
    likes = Like.objects.filter(post=OuterRef('id'), user=user)
    posts = Post.objects.filter(user=user).order_by('date').annotate(user_likes=Count(likes.values('id'))).reverse()

    total_followers = Follow.objects.filter(following=user).count()
    total_followings = Follow.objects.filter(follower=user).count()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    pages = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
      "user": user,
      "posts": pages,
      "total_followers": total_followers,
      "total_followings": total_followings
    }) 


def users_profile(request, id):
    if request.user.is_authenticated:
        user = request.user
        user_name = User.objects.get(id=id)
        likes = Like.objects.filter(post=OuterRef('id'), user=user)
        posts = Post.objects.filter(user=user_name).order_by('date').annotate(user_likes=Count(likes.values('id'))).reverse()

        is_followed = Follow.objects.filter(follower=request.user, following=user_name)
        total_followers = Follow.objects.filter(following=user_name).count()
        total_followings = Follow.objects.filter(follower=user_name).count()

        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        pages = paginator.get_page(page_number)
  
        if id == user.id:
   
            return render(request, "network/profile.html", {
                "user": user,
                "posts": pages,
                "total_followers": total_followers,
                "total_followings": total_followings
            })

        else:

            return render(request, "network/users_profile.html", {    
                "user_id": id,
                "user_name": user_name,
                "posts": pages,
                "total_followers": total_followers,
                "total_followings": total_followings,
                "is_followed": is_followed
            })


def following(request):
    if request.user.is_authenticated:
        user = request.user
        following_users = Follow.objects.filter(follower=user)
        likes = Like.objects.filter(post=OuterRef('id'), user=user)
        all_posts = Post.objects.all().order_by('date').annotate(user_likes=Count(likes.values('id'))).reverse()

        following_posts = []

        for post in all_posts:
            for following_user in following_users:
                if following_user.following == post.user:
                    following_posts.append(post) 

                    paginator = Paginator(following_posts, 10)
                    page_number = request.GET.get('page')
                    pages = paginator.get_page(page_number)

        if not following_users: 
            return render(request, "network/following.html", {
            "message": "Opps! You don't follow anybody."
        })     


    return render(request, "network/following.html", {
        "following_posts": following_posts
    })


def follow(request, user_id):
    try:
        user_following = User.objects.get(id=user_id)
        follow = Follow.objects.filter(follower=request.user, following=user_following)
        follow_btn = 'Unfollow'

        if follow: 
            Follow.objects.filter(follower=request.user, following=user_following).delete()
            follow_btn = 'Follow'

        else:
            Follow.objects.create(follower=request.user, following=user_following)

    except KeyError:
        return HttpResponseBadRequest("Bad Request")

    return JsonResponse({
        "user_follower": request.user.id, "user_following": user_id, "follow_btn": follow_btn
    })


def like(request, post_id):
    try:
        user = request.user
        post = Post.objects.get(id=post_id)
        like = Like.objects.filter(user=user, post=post)
        class_name = 'far fa-heart align-self-end' 

        if like:
            Like.objects.filter(user=user, post=post).delete()   

        else:
            Like.objects.create(user=user, post=post)
            class_name = 'fas fa-heart align-self-end'
        
        post.like_num = Like.objects.filter(post=post).count()
        post.save()

    except KeyError:
        return HttpResponseBadRequest("Bad Request")

    return JsonResponse({
        "post_id": post_id, "post_text": post.text, "total_likes": post.like_num, "class_name": class_name
    })


@csrf_exempt
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("text") is not None:
            post.text = data["text"]
        post.save()
    return HttpResponse(status=204)


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
