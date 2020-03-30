"""marketWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.views.static import serve

import xadmin
from marketWeb.settings import MEDIA_ROOT, NIGHTMARE_MEDIA_ROOT
from nightmare.views import nightmare_html, nightmare_css
from post.views import post_html, post_css, chart

urlpatterns = [
    url(r'^', xadmin.site.urls),
    url(r'^templates/(\d+)\.html', post_html, name='post_html'),
    url(r'^templates/images/(?P<path>.*)', serve, {'document_root': MEDIA_ROOT}),
    url(r'^templates/css.*', post_css, name='post_css'),
    url(r'^chart/(.*)', chart, name='chart'),

    url(r'^templates/nightmare/(.*?\.html)', nightmare_html, name='nightmare_html'),
    url(r'^templates/nightmare/images/(?P<path>.*)', serve, {'document_root': NIGHTMARE_MEDIA_ROOT}),
    url(r'^templates/nightmare/css/(.*\.css)', nightmare_css, name='nightmare_css'),
]
