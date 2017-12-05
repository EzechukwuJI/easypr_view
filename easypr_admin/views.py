from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db.models import F
from django.contrib import messages
from easypr_ng.models import Publication, Redirect_url
from django.contrib.auth.decorators import user_passes_test
from easypr_admin.permissions import is_admin
import json
from easypr_general.custom_functions import easypr_send_mail


@login_required()
@user_passes_test(is_admin)
def dashboardView(request, section_title):
	# section_title  =   kwargs['section_title']
	inset_template = "snippets/" + section_title + ".html"
	base_template = "easypr_admin/dashboard.html"
	context = {}
	if section_title == "submissions":
		context['post_list']   =    Publication.objects.fetch_all_articles() #get all articles
	context['section_title']   =    section_title
	context['inset_template']  =    inset_template
	return render(request, base_template, context)


def ajaxLoadDashboard(request):
	# print request.GET
	rg = request.GET
	content_dict  =   {}
	context       =   {}
	template      =   "snippets/ajax-content.html"
	content_dict['submissions'] = {'all':'all','new':'New','published':'Published',
	'processing':'Processing','sent_to_ext_editor':'sent_to_external_editor','rejected':'Rejected','pending':'pending'}
	content_dict['users']  =   {'staff':'staff','clients':'client','media_contact':'media_contact'}
	search_query_dict      =   content_dict[rg['content']]
	post_status            =   search_query_dict[rg['option']]
	if rg['content'] == "submissions":
		if not post_status == "all":
			pub_list                 =   Publication.objects.fetch_status_articles(post_status)
		else:
			pub_list                 =   Publication.objects.fetch_all_articles()
		context['content_list']      =   pub_list
		context['status']            =   rg['option']
	context['content_type']          =   rg['content']
	return render(request, template, context)


def fetchSinglePost(request):
	# ajax call
	response = HttpResponse()
	action  = request.GET.get('action', '')
	post_id        =  request.GET.get('post_id')
	post           =  Publication.objects.filter(pk = post_id)
	if action      == "preview":
		response   =  JsonResponse({'pk':post[0].pk, 'post_title':post[0].post_title, 'post_body':post[0].post_body})
	elif action    == "send_to_media":
		template   =  template      =   "snippets/post-media-contacts.html"
		context    =  {'media_contacts': post[0].get_media_contacts()}
		response   =  render(request, template, context)
	return response


@login_required()
@user_passes_test(is_admin)
def updatePost(request):
	original_post_body   =   ""
	original_post_title  =   ""
	is_edited            =   False

	post_id =  request.POST['post_id']
	post    =  Publication.objects.filter(pk = post_id)
	if post[0].post_body  != request.POST['post_body'] or post[0].post_title != request.POST['post_title']:
		original_post_body   =   post[0].post_body
		original_post_title  =   post[0].post_title
		is_edited   =  True

	post.update(
		post_title  = request.POST['post_title'],
		post_body   = request.POST['post_body'],
		is_edited   = is_edited,
		edited_by   = "Admin: " + request.user.get_full_name(),
		archived_original_post = original_post_body,
		archived_post_title    = original_post_title
		)
	if is_edited:
		messages.success(request, "changes have been saved ...")
	else:
		messages.info(request, "No changes made.")
	return redirect(reverse('easypr_admin:admin-dashboard', kwargs={'section_title':'submissions'})) # fix redirect issue



@login_required()
@user_passes_test(is_admin)
def send_post_to_media(request):
	post                =   Publication.objects.filter(pk = request.POST.get('post_id'))
	selected_contacts   =   request.POST.getlist('media_contact')
	post_images         =   post[0].get_images()
	subject = "New Post for publication"
	mail_context = {'post':post[0], 'files_to_attach':post_images, 'mail_type':'send_post', 'bcc':selected_contacts}
	easypr_send_mail(request, recipient = "", useremail= "", text="emails/send_post.html",subject=subject, context = mail_context) #fix this
	post.update(status = "processing")
	messages.success(request, "Post sent successfully.")

	# Notify owner about progress
	owner_mail_context  =   {'post':post[0], 'owner':post[0].posted_by, 'mail_type':'processing'}
	owner_subject       =   "New update on your publication"
	template            =   'emails/send_post.html' 
	easypr_send_mail(request, recipient = post[0].posted_by.first_name, useremail= post[0].posted_by.email, text=template, subject=owner_subject, context = owner_mail_context)
	return redirect(reverse('easypr_admin:admin-dashboard', kwargs={'section_title':'submissions'}))




@login_required()
@user_passes_test(is_admin)
def rejectPost(request):
	rp = request.POST
	Publication.objects.filter(pk = rp['post_id']).update(status = "Rejected", rejection_reason = rp['rejection_reason'], deleted = True) #change status to deleted but keep in db for backup
	messages.success(request, "post has been deleted.")
	return redirect(reverse('easypr_admin:admin-dashboard', kwargs={'section_title':'submissions'}))



@login_required()
@user_passes_test(is_admin)
def publishPost(request):
	post 			= 	Publication.objects.filter(pk = request.POST['post_id'])
	posted_by  		= 	post[0].posted_by
	post_urls  		=   request.POST.getlist('post_url[]')

	for url in post_urls:
		Redirect_url.objects.create(url = url, post = post[0]) # create a redirect url for each link
	
	subject = "New update on your publication"
	mail_context = {'post':post[0], 'media_urls': post_urls, 'mail_type':'publish'}
	post.update(status = "published", published_by = request.user)

	easypr_send_mail(request, recipient = posted_by.first_name, useremail= posted_by.email, text="emails/send_post.html",subject=subject, context = mail_context)
	messages.success(request, "Post has been published successfully.")
	return redirect(reverse('easypr_admin:admin-dashboard', kwargs={'section_title':'submissions'}))
