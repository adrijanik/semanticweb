from django.conf.urls import url
from ted_talks import views

urlpatterns = [
    url(r'^$', views.homepage, name="homepage"),
]
