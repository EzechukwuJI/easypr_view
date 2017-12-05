from zinnia.sitemaps import TagSitemap
from zinnia.sitemaps import EntrySitemap
from zinnia.sitemaps import CategorySitemap
from zinnia.sitemaps import AuthorSitemap


from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^easypr_admin/', include(admin.site.urls)),
    url('^',      include('easypr_ng.urls',      namespace  = "easypr_ng")),
    url('^admin/', include('easypr_admin.urls',   namespace  = "easypr_admin")),
    url('^',      include('easypr_general.urls', namespace  = "general")),
    url(r'^blog/', include('zinnia.urls')),
    url(r'^comments/', include('django_comments.urls'))
]

# sitemaps = {'tags': TagSitemap,
#             'blog': EntrySitemap,
#             'authors': AuthorSitemap,
#             'categories': CategorySitemap,}

# urlpatterns += [
#     'django.contrib.sitemaps.views',
#     url(r'^sitemap.xml$', 'index',
#         {'sitemaps': sitemaps}),
#     url(r'^sitemap-(?P<section>.+)\.xml$', 'sitemap',
#         {'sitemaps': sitemaps})]
