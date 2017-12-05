# easypr_ng.views.py
import datetime
import os
from django.core import serializers
from django.contrib.sites.shortcuts import get_current_site
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
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test


from easypr_ng.models import *
from easypr_general.custom_functions import transaction_ref, get_random_code, paginate_list, get_category_packages_dicts_list, easypr_send_mail
from easypr_general.models import ServiceCategory
# from easypr_ng.models import MediaHouse, MediaContact, PressMaterial, Redirect_url, Publication, PublicationImage, \
# Purchase, PayDetails, PurchaseInvoice, Bouquet, Sector, MediaPlatform, Comment, CommentReply
from easypr_ng.forms import ContentUploadForm, BizInfoForm, TargetAudienceForm,ServiceRequestForm
from easypr_general.forms import LoginForm
from easypr_general.models_field_choices import PR_FREQUENCY, BLOG_CATEGORIES, NEWSPAPER_ADV_SIZES, AUDIO_ADV_DURATION
from easypr.settings import NAIRA_DOLLAR_RATE as exchange_rate
from easypr.settings import IMAGE_FEE_N
from easypr_ng.paystack  import Paystack
from easypr_admin.permissions import is_admin



# collect all economic sectors for a post
def get_sectors():
    post_sectors = Sector.objects.filter(active = True)
    return post_sectors


def get_recent_posts(post_count, order_by):
    recent_posts  =  Publication.objects.fetch_published_articles().order_by('-date_posted').order_by(order_by)[:post_count]
    return recent_posts


def save_uploaded_images(request, image_model_object, model_field_name, related_model_instance):
    for image in request.FILES.keys():
        if model_field_name == "post": # images are from publication submission process
            image_model_object.objects.create(image = request.FILES[image], caption = request.POST["cap_" + image], post = related_model_instance)
        else: # images are from service request action
            image_model_object.objects.create(image = request.FILES[image], caption = request.POST["cap_" + image], request = related_model_instance)
           

def  indexView(request):
    context = {}
    context['recent_posts'] = get_recent_posts(50,"?")
    # request.marketing_bundles  =  Media_Marketing_Bundles.objects.filter(active = True)
    # context['marketing_bundles']   =    Media_Marketing_Bundles.objects.filter(active = True)
    return render(request, 'easypr_general/index.html', context)
    

def ourWorksView(request):
    return render(request, 'easypr_ng/our-works.html', {})


def create_post(request, press_material):
    transaction_id  =  transaction_ref("publication", Publication, 10)
    rp              =  request.POST
    title           =  rp['post_title']
    posted_by       =  request.user
    content         =  rp['post_body']
    person          =  rp['person_to_quote']
    position        =  rp['persons_position']
    platform        =  MediaPlatform.objects.get(pk = rp['platform'])
    sector          =  Sector.objects.get(pk = rp['sector'])
    press_material  =  PressMaterial.objects.get(name_slug = press_material)
    online          =  rp.get('publish_online', False)
    new_post = Publication.objects.create(transaction_id = transaction_id, post_title = title, post_body = content,person_to_quote = person, persons_position = position,
        posted_by = posted_by, platform = platform, sector = sector, publish_online = online, press_material = press_material, status = "pending")
    
    # selected_media_houses = [ media for media in MediaHouse.objects.filter(pk__in = rp.getlist('media_house[]'))]

    for media_pk    in  rp.getlist('media_house[]'):
        media_house =   MediaHouse.objects.get(pk = media_pk )
        new_post.media_houses.add(media_house)

    new_post.save()
    save_uploaded_images(request, PublicationImage, "post", new_post) #saves uploaded image files
    new_post.save()
    return new_post


# def create_purchase_record(request, package,publication):
#     tr_id       =  transaction_ref("purchase", Purchase, 10)
#     pay_id      =  transaction_ref("payment",  PayDetails, 10)
#     pay_details =  PayDetails.objects.create(user = request.user, transaction_id = pay_id)
#     new_purchase = Purchase.objects.create(user = request.user, transaction_id = tr_id, package = package,
#         publication = publication, payment_details = pay_details)
#     return new_purchase


def create_purchase_record(request, package = None, bundle = None, publication = None):
    tr_id                   =   transaction_ref("purchase", Purchase, 10)
    pay_id                  =   transaction_ref("payment",  PayDetails, 10)
    pay_details, status     =   PayDetails.objects.get_or_create(user = request.user, transaction_id = pay_id)
    new_purchase,status     =   Purchase.objects.get_or_create(user = request.user, transaction_id = tr_id, package = package,
        publication =   publication, payment_details = pay_details, bundle = bundle)
    return new_purchase


@login_required()
def buy_packageView(request, press_material, package):
    form                   =   ContentUploadForm()
    context                =   {}
    package                =   get_object_or_404(Package, name = package, category = PressMaterial.objects.get(name_slug = press_material))
    template               =  'easypr_ng/content-upload.html'
    context['sectors']     =   Sector.objects.filter(active = True)
    exclude_list           =   ['blog', 'radio','television']
    context['platforms']   =   MediaPlatform.objects.filter(active = True).exclude(name__in = exclude_list)
    context['package']     =   package
    if request.method      ==  "POST":
        form = ContentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_post       =    create_post(request, press_material)
            new_purchase   =    create_purchase_record(request, package, None, new_post) # bundle is none when purchase is for a package
            # new_purchase   =    create_purchase_record(request, package, new_post)
            new_purchase.service_purchased  =  "pr_package"
            new_purchase.save()
            previous_page_url                 =   request.POST.get('previous_page', "")
            request.session['previous_page']  =   previous_page_url
            return redirect(reverse('easypr_ng:preview-content', kwargs={'transaction_id':new_post.transaction_id}))
        else:
            print form.errors
            context['form'] = ContentUploadForm(data = request.POST)
            context.update({'press_material':press_material, 'package':package})
            return render(request, template, context)
    context['form'] = ContentUploadForm()
    category_and_item_dict   =   request.session.get('category_item_dict', {})
    context.update(category_and_item_dict)
    return render(request, template, context)



@login_required()
def previewPublicationView(request, **kwargs):
    context = {}
    post = get_object_or_404(Publication, transaction_id = kwargs['transaction_id'])
    previous_page  = request.session.get('previous_page',"/") # save previous page
    if request.session.has_key('previous_page'):
        del request.session['previous_page'] # clear previous page url session
    # previous_page = request.META['HTTP_REFERER']
    return render(request, 'easypr_ng/content-preview.html', {'post':post, 'previous_page':previous_page})



@login_required()
def Payment(request, **kwargs):
    ''' calculate amount payable and purchase record to populate payment page '''
    template = 'easypr_ng/payment.html'
    image_fee_N    = IMAGE_FEE_N
    image_fee_D    = image_fee_N/exchange_rate
    previous_page  = request.META.get('HTTP_REFERER', "")
    publication    = get_object_or_404(Publication, transaction_id = kwargs['transaction_id'])
    purchase       = get_object_or_404(Purchase, publication = publication)
    context        = {'post':publication, 'purchase':purchase, 'previous_page':previous_page}
    total_amount_payable_N = 0.0
    total_amount_payable_D = 0.0
    request.session['service_purchased']   =    purchase.service_purchased # save purchase type
    if not publication.completed:
        if publication.has_image():
            total_amount_payable_N = purchase.package.amount_payable_N() + image_fee_N
            total_amount_payable_D = purchase.package.amount_payable_D() + image_fee_D
            context.update({'image_fee_N':image_fee_N, 'image_fee_D':image_fee_D})
            request.session['total_payable_N'] = total_amount_payable_N
            request.session['total_payable_D'] = total_amount_payable_D
        else:
            total_amount_payable_N = purchase.package.amount_payable_N() 
            total_amount_payable_D = purchase.package.amount_payable_D()
        context.update({'total_amount_N': total_amount_payable_N, 'total_amount_D':total_amount_payable_D})
        return render(request, template, context)
    else:
        request.session['post_id']       =   publication.pk
        request.session['purchase_id']   =   purchase.pk
        request.session['pay_info_id']   =   purchase.payment_details.pk
        return redirect(reverse('easypr_ng:confirmation'))
    context.update({'total_amount_N': total_amount_payable_N, 'total_amount_D':total_amount_payable_D})  
    return render(request, template, context)


@login_required()
def savePayInfo(request):
    #  manual payment processing, called with ajax
    if request.method == "POST":
        rp = request.POST
        transaction_id                         =    rp['purchase_id']
        purchase                               =    get_object_or_404(Purchase, transaction_id = transaction_id)
        pay_details                            =    purchase.payment_details
        request.session['service_purchased']   =    purchase.service_purchased
        request.session['purchase_id']         =    purchase.pk
        request.session['pay_info_id']         =    pay_details.pk

        PayDetails.objects.filter(pk = pay_details.pk).update(payment_method = rp['method'].replace("_"," ").title(), 
            amount_paid = rp['amount'], date_paid = rp['date'], bank_name = rp['bank'], currency = rp['currency'], teller_number = rp['teller'])
        # if not purchase.publication  == None: 
        # print "updating publication details ..."
        # update publication details
        Publication.objects.filter(pk = purchase.publication.pk).update(completed = True)   # Evaluate this
        purchase.ordered = True
        purchase.save()
        return JsonResponse({'response': 'success', 'trans_ref':purchase.transaction_id})
    else:
        return JsonResponse({'response': 'Failed'})
   

# Buy marketing bundle
def createBundlePurchase(request):
    bundle              =   Media_Marketing_Bundles.objects.get(pk = request.GET.get('bundle_id'))
    pending_purchase    =   Purchase.objects.filter(user = request.user, ordered = False, bundle = bundle)
    purchase_record     =   None
    if not pending_purchase.exists():
        purchase_record = create_purchase_record(request, None, bundle, None)
        purchase_record.service_purchased = "marketing_bundle"
        purchase_record.save()
    else:
        purchase_record = pending_purchase[0]
    return JsonResponse({'purchase_id':purchase_record.transaction_id, 'bundle_id':bundle.pk, 'bundle_name':bundle.name, 'bundle_price':bundle.price_N})


# def makeCardPayment(request):
#     txn_ref                             =   request.POST.get('purchase_txn_ref')
#     purchase_amount                     =   request.POST.get('txn_amount')
#     callback_url                        =   ""
#     kwargs                              =   {'ref':txn_ref,'amount':purchase_amount,'email':request.user.email}
#     request.session['purchase_amount']  =   purchase_amount
#     reference                           =   ""
#     response_dict                       =   {}
#     if request.method ==  "POST":
#         rp = request.POST
#         reference                       =   rp.get('purchase_txn_ref')
#         amount                          =   rp.get('txn_amount')
#         email                           =   request.user.email
#         if os.environ['DB_NAME']:
#             callback_url                =  get_current_site(request).domain +  reverse('easypr_ng:verify-card-payment', kwargs={'txn_ref':reference})
#         else:
#             callback_url                =   str('127.0.0.1:8000') +  reverse('easypr_ng:verify-card-payment', kwargs={'txn_ref':reference})  #for test purposes only
#         ps = Paystack()
#         response_dict  =   ps.initiate_transaction(request, reference, amount, email, callback_url)
#     return JsonResponse(response_dict)


def makeCardPayment(request):
    attempts                            =   1 # first attempt
    txn_ref                             =   request.POST.get('purchase_txn_ref')
    purchase_amount                     =   request.POST.get('txn_amount')
    kwargs                              =   {'ref':txn_ref,'amount':purchase_amount,'email':request.user.email}
    request.session['purchase_amount']  =   purchase_amount
    reference                           =   ""
    response_dict                       =   {}

    if request.method ==  "POST":
        rp = request.POST
        reference              =  rp.get('purchase_txn_ref')
        amount                 =  rp.get('txn_amount')
        email                  =  request.user.email
        # callback_url           =  str('127.0.0.1:8000') +  reverse('easypr_ng:verify-card-payment', kwargs={'txn_ref':reference})  #for test purposes only
        callback_url           =  get_current_site(request).domain +  reverse('easypr_ng:verify-card-payment', kwargs={'txn_ref':reference})
        ps = Paystack()
        response_dict  =   ps.initiate_transaction(request, reference, amount, email, callback_url)
        try:
            if response_dict['error_response']  ==  "Duplicate Transaction Reference":
                append_random   =  get_random_code(4)
                new_ref         =  str(reference) + str(append_random)
                print "re-attempting payment with reference number %s" %(new_ref)
                # callback_url       =  str('127.0.0.1:8000') +  reverse('easypr_ng:verify-card-payment', kwargs={'txn_ref':new_ref})  #for test purposes only
                callback_url       =  get_current_site(request).domain +  reverse('easypr_ng:verify-card-payment', kwargs={'txn_ref':new_ref})
                response_dict      =   ps.initiate_transaction(request, new_ref, amount, email, callback_url)
        except Exception as e:
            print "error: %s" %(e)
    return JsonResponse(response_dict)



def verifyCardPayment(request, txn_ref):
    ps = Paystack()
    response       =   ps.verify_transaction(request, txn_ref) # Verify card transaction from paystack

    if response    ==   "success":
        # check paystack's augmented transaction reference and slice to normal transaction reference
        if len(txn_ref) > 12:
            txn_ref = txn_ref[:12]

        purchase   =   Purchase.objects.filter(transaction_id = txn_ref)
        request.session['purchase_id'] = purchase[0].pk
        request.session['pay_info_id'] = purchase[0].payment_details.pk
        if purchase[0].service_purchased == "pr_package":
            request.session['post_id'] = purchase[0].publication.pk
            Publication.objects.filter(pk = purchase[0].publication.pk).update(completed = True)
        # update purchase details
        purchase.update(ordered = True)
        pay_details = purchase[0].payment_details
        # update pay details
        pay_details.pay_status      =  'verified'
        pay_details.verified_by     =  'Paystack'
        pay_details.date_paid       =   str(datetime.datetime.now().strftime('%c'))
        pay_details.date_verified   =   datetime.datetime.now()
        pay_details.payment_method  =   "Card Payment"
        pay_details.amount_paid     =   float(request.session.get('purchase_amount'))/100
        pay_details.save()
        return redirect(reverse('easypr_ng:confirmation'))
    else:
        message.error(request, "Sorry we could not verify your card payment, please try again.")
    return redirect(request.META['HTTP_REFERER'])



@login_required()
def confirmationView(request):
    active_session_keys = ['post_id','purchase_id','pay_info_id', 'service_purchased', 'purchase_amount']
    service_purchased   = request.session.get('service_purchased', "")
    post = purchase =  pay_info = {}

    image_fee_N    = IMAGE_FEE_N
    image_fee_D    = image_fee_N/exchange_rate

    if request.session.has_key('post_id'):
        post           =    get_object_or_404(Publication, pk = request.session.get('post_id', ''))
        post.status    =    "new"
        post.completed =    True
        post.save()
    if request.session.has_key('purchase_id'):
        purchase     =   get_object_or_404(Purchase,    pk = request.session.get('purchase_id', ''))
    if request.session.has_key('pay_info_id'):
        pay_info     =   get_object_or_404(PayDetails,  pk = request.session.get('pay_info_id', ''))
    try:
        total_payable_N =  request.session.get('total_payable_N', purchase.package.amount_payable_N)
        total_payable_D =  request.session.get('total_payable_D', purchase.package.amount_payable_D)
    except Exception as e:
        print " this is the error ", e
        pass
    context = {'post':post,'purchase':purchase,'pay_info':pay_info, 'total_D':total_payable_D, 'total_N':total_payable_N, 'image_fee_D':image_fee_D, 'image_fee_N':image_fee_N}
    
    # send confirmation and purchase invoice mail
    mail_container = [ ["Purchase Invoice","emails/purchase-invoice.html",context]]
    try:
        if purchase.service_purchased == "pr_package":
            mail_container.append(["Publication submission confirmation","emails/publication-confirmation.html",{'post':post, 'total_D':total_payable_D, 'total_N':total_payable_N,'image_fee_D':image_fee_D, 'image_fee_N':image_fee_N}])
    except:
        pass
    for item in mail_container:
        subject      = item[0]
        template     = item[1]
        mail_context = item[2]
        # send mail to client
        easypr_send_mail(request, recipient = request.user.first_name, useremail= request.user.email, text=template,subject=subject, context = mail_context)
    
    # send notification mail to admin
    subject = "New request submission on easypr.ng"
    msg = "You have received a new service request on EasyPR "
    mail_context = {'message': msg, 'sender_email':request.user.email}
    easypr_send_mail(request, recipient = 'Admin', useremail= 'feedback@easypr.ng', text="emails/client-feedback.html",subject=subject, context = mail_context)

    # clear session variables
    for key in request.session.keys():
        if key in active_session_keys:
            del request.session[key]
    context = {'post':post,'purchase':purchase,'pay_info':pay_info, 'service_purchased':service_purchased}
    return render(request, 'easypr_ng/confirmation.html', context)



def ajax_get_media_houses(request):
    ''' ajax view fetches applicable media houses for selected platform '''
    media_platform_id  =   request.POST['media_platform']
    template        =  'snippets/media-options.html'
    platform        =   MediaPlatform.objects.filter(pk = media_platform_id)
    media_houses    =   MediaHouse.objects.filter(platform__in = platform)
    return render(request, template, {'available_media': media_houses})
   
   
def get_blog_list(request):
    ''' ajax view fetches applicable blogs for selected category '''
    selected_category  =   request.GET.get('blog_category', "all")
    template           =  'snippets/blog_list.html'
    blog_list          =   Blogs.objects.filter(category = selected_category)
    return render(request, template, {'active_blogs': blog_list})


def newsRoomView(request):
    context  = {}
    template = 'easypr_general/newsroom.html'
    context['show_news_list'] = True
    context['show_news_details']   =  False
    published_articles       =  paginate_list(request, Publication.objects.fetch_published_articles().order_by('-date_posted'), 10)
    context['articles']      =  published_articles
    context['sectors']       =  get_sectors()
    context['recent_posts']  =  get_recent_posts(5,"-date_posted")
    return render(request, template, context)


def newsRoomCatView(request, **kwargs):
    context  = {}
    template = 'easypr_general/newsroom.html'
    context['show_news_list'] = True
    context['show_news_details']   =  False
    context['sectors']   =  get_sectors()
    cat_article = paginate_list(request, Publication.objects.fetch_published_articles().filter(sector__name_slug = kwargs['category']).order_by('-date_posted'), 1)
    context['articles'] = cat_article
    context['recent_posts'] = get_recent_posts(5,"-date_posted")
    return render(request, template, context)


def  readnewsView(request, post_id, title_slug):
    context = {}
    context['post'] = get_object_or_404(Publication, title_slug = title_slug, pk = post_id)
    context['show_news_details']   =  True
    context['show_news_list'] = False
    context['sectors']   =  get_sectors()
    context['recent_posts'] = get_recent_posts(5,"-date_posted")
    return render(request, 'easypr_general/newsroom.html', context)


@login_required()
def postCommentView(request):
    context  =   {}
    if request.user.is_authenticated:
        if request.method == "POST" and not request.POST['msg'] == "":
            rp = request.POST
            post = get_object_or_404(Publication, pk = rp['post_id'])
            new_comment = Comment.objects.create(post= post, comment = rp['msg'], posted_by = request.user, website=rp['website'])
            context['comment'] = new_comment
        return render(request, 'snippets/post-comments.html', context)
    return JsonResponse({'error_msg': 'you have to be logged in to comment.'})


# @login_required()
@csrf_exempt
def postCommentReplyView(request):
    if request.user.is_authenticated:
        context = {}
        if request.method == "POST" and not request.POST['msg'] == "":
            comment = get_object_or_404(Comment, pk = request.POST['comment_id'])
            new_reply = CommentReply.objects.create(comment = comment, posted_by = request.user, reply = request.POST['msg'])
            context['reply'] = new_reply
        return render(request, 'snippets/comment-replies.html', context)
    return JsonResponse({'response':"<a href="" class= 'text-danger'><strong>Kindly login to post your comment</strong></a>"})


@csrf_exempt
def strategyPlannerIntroView(request):
    if request.POST.has_key('start-strategy'):
        anon_userID = get_random_code(35).lower()
        new_strategy = PRStrategy.objects.create(anon_userID = anon_userID)
        request.session['strategy_in_session']   =  new_strategy.pk
        return redirect(reverse('easypr_ng:strategy-planner', kwargs={'step':1, 'anon_userID':anon_userID}))
    return render(request,'easypr_ng/strategy-planner-info.html', {})


def get_current_strategy(request):
    pk = request.session.get('strategy_in_session', "")
    try:
        return PRStrategy.objects.filter(pk = pk)
    except:
        return None

def validate_post_keys(request, keys_dict):
    ''' validates form values and sets defaults '''
    rp = request.POST
    r_dict = {}
    for key in keys_dict.keys():
        if rp.has_key(key):
            if keys_dict[key][0] == "unit":
                r_dict[key]  = rp[key]
            else:
                r_dict[key] = rp.getlist(key)
        else:
            r_dict[key] = keys_dict[key][1]
    return r_dict



def strategyPlannerView(request, step,  anon_userID):
    template = 'easypr_ng/strategy-planner.html'
    context = {}
    context['step'] = 1
    context['step_template'] = 'step_forms/step1.html'
    context['anon_userID'] = anon_userID
    context['form'] = BizInfoForm()
    context['caption'] = "This is the first step to your greatness - this is just a dummy string"
    current_strategy = get_current_strategy(request)

    step = int(step)
    total_steps = 7
   
    if step <= 0 or step > total_steps:
        message = "The page number your are trying to view does not exist"
        return render(request, '404.html', {'response': message})
    elif not PRStrategy.objects.filter(anon_userID = anon_userID).exists():
        message = "No strategy creation in progress for this ID, you can start a new strategy below."  
        messages.error(request, message)
        return redirect(reverse('easypr_ng:strategy-planner-intro'))

    if request.method == "POST":
        rp = request.POST  
        if step == 1:
            fields_dict_and_defaults = {'business_type':['unit', 'NA'],'company_type':['unit', 'NA'],'is_pr_agency':['unit','No'],'size_of_company':['unit',0]}
            valid_dict = validate_post_keys(request, fields_dict_and_defaults)
            current_strategy.update(business_type = valid_dict['business_type'], company_type = valid_dict['company_type'],
                is_pr_agent = valid_dict['is_pr_agency'], size_of_pr_team = valid_dict['size_of_company'])
            # context values for next step
            sectors = get_sectors()
            next_caption = "We are creating a unique experience for you!"
            next_form = TargetAudienceForm()
            next_step = 2
            context.update({'step':next_step,'caption':next_caption, 'form':next_form,'sectors':sectors, 'anon_userID':anon_userID, 'step_template':'step_forms/step2.html'}) #for next form page
             
        if step == 2:
            fields_dict_and_defaults = {'target_audience':['list', 'NA']}
            valid_dict = validate_post_keys(request, fields_dict_and_defaults)
        
            current_strategy.update(target_audience = ",".join(valid_dict['target_audience']))
            
            next_caption = "Your business is about to experience a great and phenomenal boost"
            next_step = 3
            pr_goals =  ['Lead generation','Traffic', 'Engagement', 'SEO', 'Sales', 'Social']
            context.update({'step':next_step, 'caption':next_caption, 'pr_goals':pr_goals, 'pr_frequency':PR_FREQUENCY, 'step_template':'step_forms/step3.html'})

        if step == 3:
            fields_dict_and_defaults = {'pr_goals':['list', 'NA'],'pr_frequency':['unit','NA']}
            valid_dict = validate_post_keys(request, fields_dict_and_defaults)
        
            current_strategy.update(pr_goals = ",".join(valid_dict['pr_goals']), frequency_of_pr = valid_dict['pr_frequency'])
            
            next_caption = "Simplified and targeted PR services for maximum productivity. "
            next_step = 4
            target_audience =  ['Local','Regional', 'State', 'National', 'International']

            context.update({'step':next_step, 'caption':next_caption, 'target_audience':target_audience, 'step_template':'step_forms/step4.html' })

        if step == 4:
            fields_dict_and_defaults = {'target_audience':['list', '[]'],'use_external_db':['unit','NA'],'current_db':['unit', 'NA']}
            valid_dict = validate_post_keys(request, fields_dict_and_defaults)
        
            current_strategy.update(target_audience_location = ",".join(valid_dict['target_audience']), currently_use_pr_db = valid_dict['use_external_db'], pr_db_used = valid_dict['current_db'])
            # save selections from step 3
            next_caption = "create any progressive content for this stage caption."
            next_step = 5
            social_media_platform =  ['Facebook','Twitter','Youtube','Instagram','Vimeo','Pinterest','LinkedIn','Google']
            context.update({'step':next_step, 'caption':next_caption, 'media_platform':social_media_platform, 'step_template':'step_forms/step5.html'})

        if step == 5:
            fields_dict_and_defaults = {'social_media_platform':['list', '[]']}
            valid_dict = validate_post_keys(request, fields_dict_and_defaults)
        
            current_strategy.update(social_media_used = ",".join(valid_dict['social_media_platform']))
            next_caption = "create any progressive content for this stage caption."
            next_step = 6
            context.update({'step':next_step, 'caption':next_caption, 'step_template':'step_forms/step6.html'})

        if step == 6:
            fields_dict_and_defaults = {'need_pr_writing':['unit', 'No'], 'need_media_pitching':['unit','No'],'has_newsroom':['unit','No']}
            valid_dict = validate_post_keys(request, fields_dict_and_defaults)
        
            current_strategy.update(require_pr_writing= valid_dict['need_pr_writing'],require_media_pitching = valid_dict['need_media_pitching'], do_you_have_newsroom = valid_dict['has_newsroom'])
            
            next_caption = "Hurray! you have successfully created a unique PR strategy for your brand."
            next_step = 7
            context.update({'step':next_step, 'caption':next_caption, 'step_template':'step_forms/step7.html'})
        if step == 7:
            fields_dict_and_defaults = {'company_name':['unit', 'NA'], 'contact_name':['unit','NA'],'email':['unit','NA'], 'phone_no':['unit','NA']}
            valid_dict = validate_post_keys(request, fields_dict_and_defaults)

            if valid_dict['company_name'] == "NA" or valid_dict['contact_name'] == "NA" or valid_dict['email']  == "NA":
                messages.info(request, "You have not made any entries yet, please refresh the page to continue.")
                return redirect(reverse('easypr_ng:strategy-planner', kwargs={'step':1, 'anon_userID':current_strategy[0].anon_userID}))
        
            current_strategy.update(company_name = valid_dict['company_name'],contact_name = valid_dict['contact_name'],email = valid_dict['email'], phone_number = valid_dict['phone_no'], completed = True)
            messages.success(request, "Thank you!. We have received your submission, A member of the EasyPR team will contact you shortly")
            return redirect(reverse('easypr_ng:strategy-planner-intro')) 
    return render(request, template, context)



def  servicesView(request, service_category):
    context = {}
    service   =   ServiceCategory.objects.filter(name_slug = service_category)
    if not service.exists():
        message = "service not found"
        messages.info(request, "No Services found")
        return render(request, 'easypr_general/services-details.html', {'response': message})
    context['service_list'] = service[0].serviceitem_set.all().exclude(active = False)
    context['service']      = service[0]
    return render(request, 'easypr_general/services-details.html', context)


def bundlePlanView(request):
    context = {}
    context['marketing_bundles']   =    Media_Marketing_Bundles.objects.filter(active = True)
    template = 'easypr_ng/package-plans.html'
    context['loginform'] = LoginForm()
    return render(request, template, context)


@login_required()
def buyBundleView(request, **kwargs):
    template  =  'easypr_ng/payment.html'
    return render(request, template, {'source':'buy-bundles'})


def get_startedView(request, category,item):
    ''' show price list '''
    template                                =   "easypr_ng/pricing.html"
    context                                 =   {}
    context['form']                         =   ServiceRequestForm
    pkg_details_dicts_list, press_material  =   get_category_packages_dicts_list(item)
    context['press_material']               =   press_material
    if pkg_details_dicts_list:
        context['plan_names']               =   pkg_details_dicts_list[0]['name']
        pkg_details_dicts_list.pop(0)
    context['pkg_dict']                     =   pkg_details_dicts_list
    request.session['category_item_dict']   =   {'category':category, 'item':item}
    return render(request, template, context)


def submitContentView(request, category, item):
    context = {}
    context['category']     =  category
    template = "easypr_ng/submit-content.html"
    return render(request, template, {})




# def save_extra_fields(request, new_request, service_type):
#     print "transferred new request ", new_request
#     extra_field_dict = {'radio_extra_fields':['adv_service_type','adv_duration','region','audio_file'],
#     'television_extra_fields':['adv_service_type','adv_duration','region','video_file'],
#     'newspaper_extra_fields': ['page_size','media_house','page_color','advert_image_file',
#     'adv_instructions','allow_content_editing','allow_content_editing'] }   

#     extra_fields_to_use =    extra_field_dict[service_type + '_extra_fields'] # get the extra field list to use
#     for field_name in extra_fields_to_use:
#         model_field = ServiceRequest._meta.get_field(field_name)
#         if request.FILES:
#             new_request.model_field = request.FILES.get(field_name, None) #save files first
#         else:
#             new_request.model_field     = request.POST.get(field_name, None) # save other field contents
#     print "save status", new_request.save() # save changes to new request
#     return new_request
        

def get_media_houses(platform):
    return MediaHouse.objects.filter(platform__name = platform, active = True)


def requestServiceView(request, category, item):
    context = {}
    context['duration_list']     =  AUDIO_ADV_DURATION
    context['request_form']      =  ServiceRequestForm
    context['category']          =  category
    context['item']              =  item
    template                     =  "easypr_ng/request-service.html"
    short_media_name             =  item.split('-')[0]
    advert_media_categories      =  ['television','radio','newspaper'] # list media categories
    # advert_media_categories      =  ['television','radio','newspaper'] # list media categories

    if short_media_name  in advert_media_categories:
        context['active_media_house']         =   get_media_houses(short_media_name)
        # print "media houses >", context['active_media_house']

    if item == "blogger-distribution":
        context['active_blogs']               =   Blogs.objects.filter(active = True) # load all active blog houses
        context['blog_categories']            =   [name[1] for name in BLOG_CATEGORIES] # fetch list of blogs
    if item == "newspaper-advertising":
        context['advert_page_sizes']          =   NEWSPAPER_ADV_SIZES

    if request.method == "POST":
        rp =  request.POST
        service_type        =   rp['service_type']
        brief_description   =   rp.get('brief_description', None)  # collects brief description if available
        ticket_number = transaction_ref("request", ServiceRequest, 6) # generates six characters ticket number
        form = ServiceRequestForm(request.POST, request.FILES)
        if form.is_valid():
            form = ServiceRequestForm(request.POST, request.FILES)
            form.save(commit = False)
            new_request = form.save()
            new_request.ticket_number = ticket_number
            new_request.service_type = rp['service_type']
            if not rp['service_type']  == "blogger-distribution":
                new_request.brief_description = brief_description
            
            # if not service_type  == "photo-news":
            #     if not service_type == "blogger-distribution":
            #         new_request.preferred_call_time = rp['preferred_call_time']
            #         new_request.time_service_needed = rp['time_service_needed']
            # else:
            #     if rp['need_photographer']  ==  "No":
            #         if request.FILES:
            #             save_uploaded_files(request, RequestImage, "request", new_request) #saves uploaded image files to the appropriate model
            #     else:
            #         new_request.name_of_event = rp['name_of_event']
            #         new_request.event_date    = rp['event_date']
            #         new_request.event_time    = rp['event_time']
            #         new_request.event_venue   = rp['event_venue']

            non_timed_list = ['blogger-distribution','newspaper-advertising','radio-advertising','tv-advertising'] # decouple this - make list dynamic

            if service_type == "photo-news":
                if rp['need_photographer']  ==  "No":
                    if request.FILES:
                        print "saving images ..."
                        save_uploaded_images(request, RequestImage, "request", new_request) #saves uploaded image files to the appropriate model
                else:
                    new_request.name_of_event = rp['name_of_event']
                    new_request.event_date    = rp['event_date']
                    new_request.event_time    = rp['event_time']
                    new_request.event_venue   = rp['event_venue']
            else:
                if service_type not in non_timed_list:
                    new_request.preferred_call_time = rp['preferred_call_time']
                    new_request.time_service_needed = rp['time_service_needed']
                else:
                    # SAVE EXTRA FIELDS 
                    advert_services_list   =   ['radio_advertising','television_advertising','newspaper_advertising']
                    if service_type in advert_services_list:
                        extra_field_dict = {'radio-advertising_extra_fields':['adv_service_type','adv_duration','region','audio_file'],
                        'television-advertising_extra_fields':['adv_service_type','adv_duration','region','video_file'],
                        'newspaper-advertising_extra_fields': ['page_size','media_house','page_color','advert_image_file',
                        'adv_instructions'] }   

                        extra_fields_to_use =    extra_field_dict[service_type + '_extra_fields'] # get the extra field list to use
                        print "extra fields ", extra_fields_to_use
                        for field_name in extra_fields_to_use:
                            model_field = ServiceRequest._meta.get_field(field_name)
                            if request.FILES:
                                new_request.model_field = request.FILES.get(field_name, None) #save files first
                            else:
                                if field_name == 'media_house':
                                    new_request.model_field     = request.POST.getlist(field_name, None) # save other field contents
                                
                                new_request.model_field     = request.POST.get(field_name, None) # save other field contents
                            new_request.save()
                                
            #  FOR BLOGGER DISTRIBUTION SUBMISSION 
            if rp['service_type']  == "blogger-distribution":
                new_request.total_price   =   rp['total_price']
                selected_blogs    =   request.POST.getlist('selected_blog[]')
                blog_objects  =   Blogs.objects.filter(name_slug__in = selected_blogs)

                for blog in Blogs.objects.filter(name_slug__in = selected_blogs):
                    new_request.blog_list.add(blog)
                
                if rp['submission-type'] == "upload_file":
                    new_request.uploaded_post_content = request.FILES.get('uploaded_post_content',None)
                else:
                    new_request.post_content  =   rp['post_content']

                if rp['check_upload_images'] == True: # if images were uploaded
                        save_uploaded_files(request, RequestImage, "request", new_request)
            new_request.save()

            msg = "Your service request with ticket number #%s has been received. A member of the EasyPR team will contact you shortly. Kindly keep the ticket number for reference" %(new_request.ticket_number)
            messages.success(request, msg)

            # send mail to client and admin.
            mail_context = {'ticket_number':ticket_number,'service_type':rp['service_type']}
            if not brief_description == None:
                mail_context.update({'brief_desc':brief_description}) 

            subject = "Service Request Confirmation"
            easypr_send_mail(request, recipient = rp['contact_person'], useremail= rp['contact_email'], text="emails/service-request-confirmation.html",subject=subject, context = mail_context)
        else:
            msg = "Sorry, something went wrong while trying to save your request. Please reload the page and try again"
            messages.error(request, msg)
            context['request_form'] =  ServiceRequestForm(data = request.POST)
            print form.errors
            return render(request, template, context)
    return render(request, template, context)



@login_required()
def userDashboard(request, **kwargs):
    template                 =  "useraccount/user-dashboard.html"
    context                  =  {}
    context['section_title'] =  kwargs['section_title']   
    context['posts']         =  Publication.objects.fetch_pub_for_user(request.user, 'new')
    return render(request, template, context)


def loadUserDashboard(request):
    rg = request.GET
    content_dict  =   {}
    context       =   {}
    template      =   "snippets/ajax-content.html"
    content_dict['submissions'] = {'all':'all','new':'New','published':'Published','in-progress':'Processing','rejected':'Rejected', 'pending':'pending'}
    search_query_dict      =   content_dict[rg['content']]
    post_status            =   search_query_dict[rg['option']]
    print "post status ", post_status
    if rg['content'] == "submissions":
        if not post_status == "all":
            pub_list                 =   Publication.objects.fetch_pub_for_user(request.user, post_status)
        else:
            pub_list                 =   Publication.objects.fetch_pub_for_user(request.user, 'all')
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
def updateUserPost(request):
    original_post_body   =   ""
    original_post_title  =   ""
    is_edited            =   False
    post_id =  request.POST['post_id']
    post    =  Publication.objects.filter(pk = post_id)
    if post[0].posted_by  ==  request.user:
        if post[0].post_body  != request.POST['post_body'] or post[0].post_title != request.POST['post_title']:
            original_post_body   =   post[0].post_body
            original_post_title  =   post[0].post_title
            is_edited   =  True
        post.update(
            post_title  = request.POST['post_title'],
            post_body   = request.POST['post_body'],
            is_edited   = is_edited,
            edited_by   = request.user.get_full_name(),
            archived_original_post = original_post_body,
            archived_post_title    = original_post_title
            )
        if is_edited:
            messages.success(request, "changes have been saved ...")
        else:
            messages.info(request, "No changes made.")
    else:
        messages.warning(request, "You do not have the permission to edit this post")
    return redirect(reverse('easypr_ng:user-dashboard', kwargs={'section_title':'my-submissions'})) # fix redirect issue



@login_required()
def rejectPost(request):
    rp = request.POST
    post = Publication.objects.filter(pk = rp['post_id'])
    if post[0].posted_by == request.user:
        post.update(status = "Rejected", rejection_reason = rp['rejection_reason'], deleted = True) #change status to deleted but keep in db for backup
        messages.success(request, "Post has been deleted. To recorver this post at any time, kindly contact the admin via helpdesk@easypr.ng")
    else:
        messages.warning(request, "You do not have the permission to delete this post")
    return redirect(reverse('easypr_ng:user-dashboard', kwargs={'section_title':'my-submissions'}))


def deletePost(request, post_pk):
    post = Publication.objects.filter(pk = post_pk)
    if post.exists():
        post[0].delete()
    messages.success(request, "post has been permanently deleted.")
    return redirect(request.META['HTTP_REFERER'])



