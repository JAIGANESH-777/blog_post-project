from django.urls import path
from . import views

app_name ='blog'

urlpatterns =[path("",views.index,name="index"),
              path("post/<str:slug>",views.detail,name="detail"),
              path("old_url",views.old_url,name="old_url"),
              path("new_url",views.new_url,name="new_page"),
              path("contact",views.contact,name="contact"),
              path("about",views.about,name="about"),
              path("register",views.register,name="regiter"),              
              ]