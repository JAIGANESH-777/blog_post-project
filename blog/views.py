from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
import logging
from blog.models import Post,Category,about_user
from django.http import Http404
from django.core.paginator import Paginator
from .forms import ForgotPasswordForm, LoginForm, ContactForm, NewPostForm,RegisterForm, ResetPasswordForm
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group


# Create your views here.

# posts = [
#         {'id':1, 'title': 'Post 1', 'content': 'Content of Post 1'},
#         {'id':2, 'title': 'Post 2', 'content': 'Content of Post 2'},
#         {'id':3, 'title': 'Post 3', 'content': 'Content of Post 3'},
#         {'id':4, 'title': 'Post 4', 'content': 'Content of Post 4'},   
#     ]
def index(request):
    all_post= Post.objects.filter(is_published=True)
    paginator= Paginator(all_post,9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title= "latest posts"
    return render(request,"blog/index.html",{"title":title,"page_obj":page_obj})
     
def detail(request,slug):
    try:
        post= Post.objects.get(slug=slug)
        related_posts=Post.objects.filter(category=post.category).exclude(pk=post.id)
        title= post.title
        # logger =logging.getLogger('testing')
        # logger.debug(f"Post variable: {related_post}")
    except Post.DoesNotExist:
        raise Http404("Post not found")
    return render(request,"blog/detail.html",{"post":post,"related_posts":related_posts,"title":title})

def old_url(request):
    return redirect(reverse('blog:new_page'))

def new_url(request):
    return HttpResponse("This is the new URL.")

def contact(request):
    title= "Contact"
    if request.method=="POST":
        form=ContactForm(request.POST)
        name=request.POST.get('name')
        email=request.POST.get('email')
        message=request.POST.get('message')
        logger =logging.getLogger('testing')
        if form.is_valid():
            #logger.debug(f"Form data is valid: {form.cleaned_data}")
            success_message="Email sent Successfully"
            return render(request,"blog/contact.html",{"form":form,"success_message":success_message,"title":title})
        else:
            #logger.debug(f"Form data is not valid: {form}")
            return render(request,"blog/contact.html",{"form":form,"name":name,"email":email,"message":message,"title":title})
    return render(request,"blog/contact.html",{"title":title})

def about(request):
    title= "About"
    about_user_content=about_user.objects.first()
    if not about_user_content:
        about_user_content="Welcome to blog – a space where ideas, insights, and inspiration come to life!At blog, we are passionate about sharing valuable content on your blogs niche, e.g., technology, health, personal growth, social impact]. Our goal is to provide well-researched, engaging, and thought-provoking articles that add value to your daily life."
    else:
        about_user_content=about_user_content.content
    return render(request,"blog/about.html",{"about_user_content":about_user_content,"title":title})

def register(request):
    title= "Register"
    form=RegisterForm()
    if request.method=="POST":
        form=RegisterForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            readers_group=Group.objects.get_or_create(name="Readers")
            user.groups.add(readers_group[0])
            #success_message="Registration Successful"
            messages.success(request, "Registration Successful")
            return redirect('blog:login')
    return render(request,"blog/register.html",{"form":form,"title":title})

def login(request):
    title= "Login"
    form=LoginForm()
    if request.method=="POST":  
        form=LoginForm(request.POST)
        print("Login successful")
        if form.is_valid():
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            user=authenticate(username=username,password=password)
            if user is not None:
                auth_login(request,user)
                print("Login successful")
                return redirect('blog:dashboard')
    return render(request,"blog/login.html",{"title":title,"form":form}) 

def dashboard(request):
    title= "Dashboard"
    blog_title= "My Posts"
    all_posts=Post.objects.filter(user=request.user)
    paginator= Paginator(all_posts,3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"blog/dashboard.html",{"title":title,"blog_title":blog_title,"page_obj":page_obj})

def logout(request):
    auth_logout(request)
    return redirect('blog:index')


def forgot_password(request):
    title= "Forgot Password"
    form = ForgotPasswordForm()
    if request.method == 'POST':
        #form
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            #send email to reset password
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            domain = current_site.domain
            subject = "Reset Password Requested"
            message = render_to_string('blog/reset_password_email.html', {
                'domain': domain,
                'uid': uid,
                'token': token
            })

            send_mail(subject, message, 'noreply@gmail.com', [email])
            messages.success(request, 'Email has been sent')


    return render(request,'blog/forgot_password.html', {'form': form})
 
def reset_password(request, uidb64, token):
    title= "Reset Password"
    form = ResetPasswordForm()
    if request.method == 'POST':
        #form
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            try:
                uid = urlsafe_base64_decode(uidb64)
                user = User.objects.get(pk=uid)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('blog:login')
            else :
                messages.error(request,'The password reset link is invalid')

    return render(request,'blog/reset_password.html', {'form': form,"title": title})


@login_required
def new_post(request):
    title= "New Post"
    form=NewPostForm()
    categories=Category.objects.all()
    if request.method=="POST":
        form=NewPostForm(request.POST,request.FILES)
        if form.is_valid():
            post=form.save(commit=False)
            post.user=request.user
            post.save()
            messages.success(request, "Post created successfully")
            return redirect('blog:dashboard')
    return render(request,"blog/new_post.html",{"title":title,"categories":categories,"form":form})

@login_required
def edit_post(request,post_id):
    title= "Edit Post"
    form=NewPostForm()
    categories=Category.objects.all()
    post=get_object_or_404(Post,id=post_id)
    if request.method=="POST":
        form=NewPostForm(request.POST,request.FILES,instance=post)
        if form.is_valid():
            post.save()
            messages.success(request, "Post updated successfully")
            return redirect('blog:dashboard')
    #selected_category_id = post.category.id
    return render(request,"blog/edit_post.html",{"categories":categories,"title":title,"post":post,"form":form})

@login_required
def delete_post(request,post_id):
    post=get_object_or_404(Post,id=post_id)
    post.delete()
    messages.success(request, "Post deleted successfully")
    return redirect('blog:dashboard')

@login_required
def publish_post(request,post_id):
    post=get_object_or_404(Post,id=post_id)
    post.is_published=True
    post.save()
    messages.success(request, "Post published successfully")
    return redirect('blog:dashboard')
