"""gk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from all import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^spot$', views.spot),
    url(r'^spot_specific/(?P<spot_id>\d+)', views.spot_specific),
    url(r'^cctv_specific/(?P<cctv_id>\d+)/remove_spot/(?P<spot_id>\d+)$', views.cctv_remove_spot),
    url(r'^cctv_specific/(?P<cctv_id>\d+)/remove_spot/(?P<spot_id>\d+)$', views.cctv_remove_spot),
    url(r'^cctv_specific/(?P<cctv_id>\d+)/remove_meta/(?P<meta_id>\d+)$', views.cctv_remove_meta),
    url(r'^cctv_specific/(?P<cctv_id>\d+)$', views.cctv_specific),
    url(r'^cctv$', views.cctv),
    url(r'^neighbor$', views.neighbor),
    url(r'^neighbor_specific/(?P<neighbor_id>\d+)', views.neighbor_specific),
    url(r'^sequence$', views.sequence),
    url(r'^sequence_specific/(?P<sequence_id>\d+)$', views.sequence_specific),
    url(r'^sequence_specific/(?P<sequence_id>\d+)/remove_neighbor/(?P<neighbor_id>\d+)$', views.sequence_remove_neighbor),
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),
    url(r'^my$', views.my),
    url(r'^manage$', views.manage),
    url(r'^manage/edit/(?P<user_id>\d+)$', views.manage_edit),
    url(r'^manage/remove/(?P<user_id>\d+)$', views.manage_remove_user),
    url(r'^manage/(?P<user_id>\d+)/remove_cctv/(?P<cctv_id>\d+)$', views.manage_remove_cctv),
    url(r'^meta_specific/(?P<meta_id>\d+)$', views.meta_specific),
    url(r'^meta$', views.meta),
    url(r'^meta/remove_meta/(?P<meta_id>\d+)$', views.remove_meta),
    url(r'^download/meta/(?P<meta_id>\d+)$', views.download_meta),
    url(r'^download/video/(?P<meta_id>\d+)$', views.download_video),
    url(r'^download/meta_avg$', views.download_meta_avg),
    url(r'^api/(?P<query>.+)$', views.api),
    url(r'^$', views.index)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)