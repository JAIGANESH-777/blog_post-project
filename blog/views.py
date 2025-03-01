from django.shortcuts import render,redirect,get_object_or_404
import logging
from blog.models import Post,Category,About_user
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
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group

def index(request):
    all_post= Post.objects.filter(is_published=True)
    paginator= Paginator(all_post,24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title= "latest posts"
    return render(request,"blog/index.html",{"title":title,"page_obj":page_obj})
     
def detail(request,slug):
    if not request.user.is_authenticated:
        messages.error(request, 'You are not logged in. Please log in to view the post.')
        return redirect('blog:login')
    if not request.user.has_perm('blog.view_post'):
        messages.error(request, 'You have no permission to view any posts')
        return redirect('blog:index')
    try:
        post= Post.objects.get(slug=slug)
        related_posts=Post.objects.filter(category=post.category).exclude(pk=post.id)
        title= post.title
    except Post.DoesNotExist:
        raise Http404("Post not found")
    return render(request,"blog/detail.html",{"post":post,"related_posts":related_posts,"title":title})

def contact(request):
    title= "Contact"
    form=ContactForm()
    if request.method=="POST":
        form=ContactForm(request.POST)
        if form.is_valid():
            feedback=form.save(commit=False)
            feedback.user=request.user
            feedback.save()
            messages.success(request,"Feedback saved successfully")
            return redirect('blog:contact')
    return render(request,"blog/contact.html",{"title":title, "form":form})

def about(request):
    title= "About"
    about_user_content=About_user.objects.first()
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
            authors_group=Group.objects.get_or_create(name="Authors")
            editors_group=Group.objects.get_or_create(name="Editors")
            user.groups.add(readers_group[0])
            user.groups.add(authors_group[0])
            user.groups.add(editors_group[0])
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
    blog_title= "Your Posts"
    all_posts=Post.objects.filter(user=request.user)
    paginator= Paginator(all_posts,9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"blog/dashboard.html",{"title":title,"blog_title":blog_title,"page_obj":page_obj})

def logout(request):
    auth_logout(request)
    return redirect('blog:index')


def forgot_password(request):
    title= "Forgot Password"
    form = ForgotPasswordForm()
    logger= logging.getLogger('TestForgotPassword')
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            print(email)
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            logger.info(f"Generated Token: {token}, User: {user}, Token: {token}")
            print("Generated Token:", token)
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


    return render(request,'blog/forgot_password.html', {'title':title,'form': form})
 
def reset_password(request, uidb64, token):
    title= "Reset Password"
    form = ResetPasswordForm()
    if request.method == 'POST':
        #form
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            print(new_password)
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
        else:
            print('not valid')
    return render(request,'blog/reset_password.html', {'form': form,'title':title})


@login_required
@permission_required('blog.add_post', raise_exception=True)
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
@permission_required('blog.change_post', raise_exception=True)
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
    return render(request,"blog/edit_post.html",{"categories":categories,"title":title,"post":post,"form":form})

@login_required
@permission_required('blog.delete_post', raise_exception=True)
def delete_post(request,post_id):
    post=get_object_or_404(Post,id=post_id)
    post.delete()
    messages.success(request, "Post deleted successfully")
    return redirect('blog:dashboard')

@login_required
@permission_required('blog.can_publish', raise_exception=True)
def publish_post(request,post_id):
    post=get_object_or_404(Post,id=post_id)
    post.is_published=True
    post.save()
    messages.success(request, "Post published successfully")
    return redirect('blog:dashboard')
