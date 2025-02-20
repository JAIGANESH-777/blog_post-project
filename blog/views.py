from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.urls import reverse
import logging
from blog.models import Post,Category,about_user
from django.http import Http404
from django.core.paginator import Paginator
from .forms import contactform,RegisterForm

# Create your views here.

# posts = [
#         {'id':1, 'title': 'Post 1', 'content': 'Content of Post 1'},
#         {'id':2, 'title': 'Post 2', 'content': 'Content of Post 2'},
#         {'id':3, 'title': 'Post 3', 'content': 'Content of Post 3'},
#         {'id':4, 'title': 'Post 4', 'content': 'Content of Post 4'},   
#     ]
def index(request):
    all_post= Post.objects.all()
    paginator= Paginator(all_post,9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    blog_title= "latest posts"
    return render(request,"blog/index.html",{"blog_title":blog_title,"page_obj":page_obj})

def detail(request,slug):
    try:
        post= Post.objects.get(slug=slug)
        related_posts=Post.objects.filter(category=post.category).exclude(pk=post.id)
        blog_title= post.title
        # logger =logging.getLogger('testing')
        # logger.debug(f"Post variable: {related_post}")
    except Post.DoesNotExist:
        raise Http404("Post not found")
    return render(request,"blog/detail.html",{"post":post,"related_posts":related_posts,"blog_title":blog_title})

def old_url(request):
    return redirect(reverse('blog:new_page'))

def new_url(request):
    return HttpResponse("This is the new URL.")

def contact(request):
    blog_title= "Contact"
    if request.method=="POST":
        form=contactform(request.POST)
        name=request.POST.get('name')
        email=request.POST.get('email')
        message=request.POST.get('message')
        logger =logging.getLogger('testing')
        if form.is_valid():
            #logger.debug(f"Form data is valid: {form.cleaned_data}")
            success_message="Email sent Successfully"
            return render(request,"blog/contact.html",{"form":form,"success_message":success_message,"blog_title":blog_title})
        else:
            #logger.debug(f"Form data is not valid: {form}")
            return render(request,"blog/contact.html",{"form":form,"name":name,"email":email,"message":message,"blog_title":blog_title})
    return render(request,"blog/contact.html",{"blog_title":blog_title})

def about(request):
    blog_title= "About"
    about_user_content=about_user.objects.first()
    if not about_user_content:
        about_user_content="Welcome to blog – a space where ideas, insights, and inspiration come to life!At blog, we are passionate about sharing valuable content on your blogs niche, e.g., technology, health, personal growth, social impact]. Our goal is to provide well-researched, engaging, and thought-provoking articles that add value to your daily life."
    else:
        about_user_content=about_user_content.content
    return render(request,"blog/about.html",{"about_user_content":about_user_content,"blog_title":blog_title})

def register(request):
    blog_title= "Register"
    if request.method=="POST":
        form=RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            success_message="Registration Successful"
            return render(request,"blog/register.html",{"form":form,"success_message":success_message,"blog_title":blog_title})
        else:
            return render(request,"blog/register.html",{"form":form,"blog_title":blog_title})
    return render(request,"blog/register.html",{"blog_title":blog_title})