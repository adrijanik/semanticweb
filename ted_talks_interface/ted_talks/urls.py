from django.conf.urls import url
from ted_talks import views

urlpatterns = [
    url(r'^$', views.homepage, name="homepage"),
    url(r'^tag_related_talks$', views.tag_related_talks, name="tag_related_talks" ),
    url(r'^related_talks$', views.related_talks, name="related_talks" ),

]
