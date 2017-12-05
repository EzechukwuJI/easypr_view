from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from easypr_general import views


# Create your urls here.
urlpatterns  =  [

             
	url(r'^$',                         				   views.indexView,                 name='homepage'),
	url(r'^who-we-are/$',                			   views.aboutUsView,               name='about-us'),
	url(r'^contact_us/$',      		   				   views.contactView,               name='contact-us'),
	url(r'^user/sign-up/$',         		   	       views.createUserAccount,         name='sign-up'),
	
	# url(r'^user/(?P<section_title>[-\w]+)$',           views.userDashboard,             name='user-dashboard'),
	# url(r'^user/(?P<section_title>[-\w]+)$',           views.userDashboard,             name='admin-dashboard'),
	
	url(r'^login/$',           		   				   views.loginView,          		name='login'),
	url(r'^logout/$',          		   				   views.logOutView,         		name='logout'),
	url(r'^careers/$',          	                   views.careersView,        		name='careers'),
	# url(r'^blog/$',          	                       views.careersView,            name='blog'),
	url(r'^subscribe/$',          	                   views.mailListView,           name='mailing-list-subscription'),
	url(r'^forgot-password/$', 						   views.forgotPasswordView,     name='forgot-password'),
    url(r'^reset-password/token=(?P<code>[-\w]+)/$',   views.resetPasswordView,  	 name='reset-password'),
	url(r'^confirm-registration/(?P<code>[-\w]+)/$',   views.confirmEmail, 			 name = 'confirm-email'),
	url(r'^thank-you/$',      					       TemplateView.as_view(template_name = "easypr_general/thank-you.html"), name='registration_success'),
	url(r'^frequently-asked-questions/$',          	   TemplateView.as_view(template_name = "easypr_general/faq.html"),  name='faq'),
	url(r'^how-it-works/$',          	               TemplateView.as_view(template_name = "easypr_general/how-it-works.html"),  name='how-it-works'),
	url(r'^terms-and-conditions/$',          	       TemplateView.as_view(template_name = "easypr_general/terms-and-conditions.html"),  name='terms-and-conditions'),

] 

# if DEBUG:
#     urlpatterns += [
#         url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
#             {'document_root': MEDIA_ROOT}),

#         url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
#             {'document_root': STATIC_ROOT}),
# ]