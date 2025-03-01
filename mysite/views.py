from django.shortcuts import render
from django.http import HttpResponseNotFound
def custom_page_not_found(request,exception=None):
    return render(request, '404.html',status=404)

def custom_forbidden(request,exception):
    return render(request, '403.html', status=403)

