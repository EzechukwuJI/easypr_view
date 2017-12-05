from django.contrib.sites.models import Site
from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User 
from easypr_general.models_field_choices import *
from easypr_general.models import UserAccount
from django.db.models import Q, Sum
import random
# from django.contrib.auth.models import User 
from easypr.settings import VAT
from easypr.settings import NAIRA_DOLLAR_RATE as exchange_rate
from easypr_general.custom_classes import Hasher
# from Crypto.Cipher import AES


class MediaPlatform(models.Model):
  name        =   models.CharField(max_length = 60)
  name_slug   =   models.CharField(max_length = 75)
  active      =   models.BooleanField(default = True)
 
  def __unicode__(self):
    return '%s' %(self.name)

  def save(self, *args, **kwargs):
    self.name_slug = slugify(self.name)
    super(MediaPlatform, self).save(*args, **kwargs)
    return True


class Sector(models.Model):
  name           =      models.CharField(max_length = 60)
  name_slug      =      models.CharField(max_length = 75)
  active         =      models.BooleanField(default = True)
 
  def __unicode__(self):
    return '%s' %(self.name)

  def save(self, *args, **kwargs):
    self.name_slug   =   slugify(self.name)
    super(Sector, self).save(*args, **kwargs)


class MediaContact(models.Model):
  media_house              =           models.ForeignKey('MediaHouse')
  first_name               =           models.CharField(max_length = 125)
  last_name                =           models.CharField(max_length = 125)
  date_added               =           models.DateTimeField(auto_now_add = True)
  email                    =           models.CharField(max_length = 225)
  phone_number             =           models.CharField(max_length = 15, null = True, blank = True)

  def __unicode__(self):
    return '%s,%s,%s' %(self.media_house.name, self.first_name + self.last_name, self.email)

  def get_media_house(self):
    return self.media_house.name

  def get_full_name(self):
    return '%s %s' %(self.first_name, self.last_name)

class MediaHouse(models.Model):
  name                =           models.CharField(max_length = 200)
  name_slug           =           models.CharField(max_length = 200)
  date_added          =           models.DateTimeField(auto_now_add = True)
  platform            =           models.ManyToManyField('MediaPlatform')
  active              =           models.BooleanField(default = True)



  def save(self, *args, **kwargs):
    self.name_slug  = slugify(self.name)
    super(MediaHouse, self).save(*args, **kwargs)


  def __unicode__(self):
    return '%s' %(self.name)


  def get_contacts(self):
  	return self.mediacontact_set.all()


class PressMaterial(models.Model):
  name_slug                =         models.CharField(max_length = 150)
  media_type               =         models.CharField(max_length = 150)
  price_per                =         models.FloatField(default = 0.0)
  date_added               =         models.DateTimeField(auto_now_add = True)
  caption                  =         models.CharField(max_length = 125)

  def __unicode__(self):
    return '%s' %(self.media_type)

  def save(self, *args, **kwargs):
    self.name_slug  = slugify(self.media_type)
    super(PressMaterial, self).save(*args, **kwargs)


class PublicationManager(models.Manager):

  def fetch_published_articles(self):
    return self.get_queryset().filter(Q(status = "Published"), Q(deleted = False, completed = True))

  def fetch_new_articles(self):
      return self.get_queryset().filter(status = "New", deleted = False, completed = True)

  def fetch_status_articles(self, status):
    return self.get_queryset().filter(Q(status = status), Q(deleted = False, completed = True))

  def fetch_all_articles(self):
    return self.get_queryset().filter(deleted = False, completed = True)

  def fetch_pub_for_user(self, user, status):
    if not status == 'all':
      response =  self.get_queryset().filter(Q(posted_by = user), Q(status = status),Q(deleted = False)) 
    # elif status == "pending":
    #   response =  self.get_queryset().filter(Q(posted_by = user), Q(deleted = False), Q(status = status))
    else:
      response =  self.get_queryset().filter(Q(posted_by = user, deleted = False))
    print "query response ", response
    return response


class Publication(models.Model):
    transaction_id                  =              models.CharField(max_length = 15)
    post_title                      =              models.CharField(max_length = 175)
    title_slug                      =              models.CharField(max_length = 200)
    status                          =              models.CharField(max_length = 50, choices = PUB_STATUS)
    post_body                       =              models.TextField(max_length = 3000, null = True, blank = True)
    person_to_quote                 =              models.CharField(max_length = 125, null = True, blank = True)
    persons_position                =              models.CharField(max_length = 125, null = True, blank = True)
    uploaded_text                   =              models.FileField(upload_to ='publication/text_file', null=True, blank = True)
    posted_by                       =              models.ForeignKey(User)
    platform                        =              models.ForeignKey('MediaPlatform', verbose_name = "Media platform", null = True, blank = True)
    sector                          =              models.ForeignKey('Sector', verbose_name = "Media sector", null = True, blank = True)
    press_material                  =              models.ForeignKey('PressMaterial', verbose_name = "Media category", null = True, blank = True)
    published_by                    =              models.ForeignKey(User, related_name="Edited_and_published_by", null = True, blank = True)
    assigned_to                     =              models.ForeignKey(User, related_name = "Third_party_Editor", null = True, blank = True)
    
    date_published                  =              models.DateTimeField(auto_now_add = False, null=True, blank=True)
    date_posted                     =              models.DateTimeField(auto_now_add = True)

    # media_urls                      =              models.ManyToManyField('Redirect_url', )
    site                            =              models.ManyToManyField(Site)
    # pictures                        =              models.ManyToManyField('PublicationImage')
    media_houses                    =              models.ManyToManyField('MediaHouse')
    
    deleted                         =              models.BooleanField(default = False)
    publish_online                  =              models.BooleanField("Do you also want online publication of the chosen media? ", default = False)
    completed                       =              models.BooleanField(default = False)
    objects                         =              PublicationManager()
    rejection_reason                =              models.CharField(max_length = 350, null = True, blank = True)
    is_edited                       =              models.BooleanField(default = False)
    edited_by                       =              models.CharField(max_length  =  125, null = True, blank = True)
    archived_original_post          =              models.TextField(max_length = 3000, null = True, blank = True)
    archived_post_title             =              models.CharField(max_length = 175, null = True, blank = True)

    def save(self, *args, **kwargs):
        self.title_slug  = slugify(self.post_title)
        super(Publication, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s' %(self.post_title)


    def get_media_urls(self):
    	return [link.url for link in self.redirect_url_set.all()]


    def get_media_houses(self):
      media = [media.name for media in self.media_houses.all()]
      return ", ".join(media)


    def get_media_contacts(self):
      contact_dict =  {}
      contact_list =  []
      for media in self.media_houses.all():
        for contact in media.mediacontact_set.all():
          contact_list.append(contact)
      return contact_list


    def get_images(self):
      return self.publicationimage_set.all()


    def featured_image(self):
      try:
        return self.get_images()[random.choice(range(0, self.get_images().count() -1))].image.url
      except:
        return None # return default avater

    def get_post_comments(self):
      return self.comment_set.all()

    def read_uploaded_document(self):
    	pass

    def has_image(self):
      return self.get_images().count() > 0


class PublicationImage(models.Model):
  post       =     models.ForeignKey('Publication', null = True, blank = True)
  image      =     models.ImageField(upload_to ='publication', null = True, blank = True)      
  caption    =     models.CharField(max_length = 200, null = True, blank =  True)

  def __unicode__(self):
    return '%s' %(self.post.post_title)


class RequestImage(models.Model):
  request     =     models.ForeignKey('ServiceRequest', null = True, blank = True)
  image       =     models.ImageField(upload_to ='service_request', null = True, blank = True)      
  caption     =     models.CharField(max_length = 200, null = True, blank =  True)


class Redirect_url(models.Model):
  url     =        models.CharField(max_length = 200, blank = True, null = True, default= None)
  post    =        models.ForeignKey('Publication', null=True, blank = True)

  def __unicode__(self):
    return '%s' %(self.url)


class Comment(models.Model):
  post            =     models.ForeignKey('Publication')
  posted_by       =     models.ForeignKey(User)
  date_posted     =     models.DateTimeField(auto_now_add = True)
  comment         =     models.TextField(max_length = 1000)
  website         =     models.CharField(max_length = 150, null = True, blank = True)


class CommentReply(models.Model):
  comment         =     models.ForeignKey('Comment')
  posted_by       =     models.ForeignKey(User)
  date_posted     =     models.DateTimeField(auto_now_add = True)
  reply           =     models.TextField(max_length = 1000)
  

class Purchase(models.Model):
  user              		=     models.ForeignKey(User, verbose_name = "Purchased By")
  transaction_id   		  =     models.CharField(max_length = 15)
  package               =     models.ForeignKey('Package', null = True, blank = True)
  bundle                =     models.ForeignKey('Media_Marketing_Bundles', null = True, blank = True)
  publication       		=     models.OneToOneField('Publication', null = True, blank = True)
  deleted           		=     models.BooleanField(default = False)
  ordered           		=     models.BooleanField(default = False) # set to true on order submission after payment is made
  status                =     models.CharField(max_length = 75, choices = PURCHASE_STATUS, default = "New")
  payment_details       =     models.ForeignKey('PayDetails', verbose_name = "Payment details", default = None)
  date_purchased        =     models.DateTimeField(auto_now_add = True)
  service_purchased     =     models.CharField(max_length = 75) #eg pr_package, marketing_bundle


  def  __unicode__(self):
    return "%s %s" %(self.transaction_id, self.status)

  def media_outreach_credit(self):
    return self.package.media_outreach_credit

  def  price_dollar(self):
    return self.package.price_dollar
    # return self.package.price_dollar


  def  price_naira(self):
    return self.package.price_naira
    # return self.package.price_naira

  def get_package_name(self):
    return '%s - %s' %(self.package.category.media_type, self.package.name)


class PayDetails(models.Model):
    user                    =     models.ForeignKey(User, verbose_name = "Payment By")
    transaction_id          =     models.CharField(max_length = 25, null = True)
    payment_method    		  =     models.CharField(max_length = 75, choices = PAYMENT_OPTIONS, default = "")
    amount_paid             =     models.FloatField(default   = 0.0)
    date_paid               =     models.CharField(max_length = 100, null = True, blank = True,)
    bank_name               =     models.CharField(max_length = 100, null = True, blank = True, choices = BANKS)
    currency                =     models.CharField(max_length = 100, null = True, blank = True)
    teller_number           =     models.CharField(max_length = 15, null = True,  blank = True)
    pay_status              =     models.CharField(max_length = 25, choices = PAYMENT_STATUS, default = "pending")
    verified_by             =     models.CharField(max_length = 125)
    date_verified           =     models.DateTimeField(auto_now_add = False, null =True, blank = True)

    def __unicode__(self):
      return "%s, %s, %s" %(self.transaction_id, self.amount_paid, self.pay_status)


class PurchaseInvoice(Purchase):
	receipt_no       =        models.CharField(max_length = 12)
	invoice          =        models.FileField(upload_to = 'Invoices/%Y-%M-%D', null = True, blank = True)

	def __unicode__(self):
		return self.receipt_no     

	def get_invoice(receipt_no):
		return self.invoice



class PRStrategy(models.Model):
  anon_userID                 =       models.CharField('Annonymous user ID', max_length = 75)
  # company info
  business_type               =       models.CharField(max_length = 25, choices = BUSINESS_TYPE, default = "Company")
  company_type                =       models.CharField(max_length = 75, choices = COMPANY_TYPE, default = "Private")
  is_pr_agent                 =       models.CharField(max_length = 75, choices = (('Yes', 'Yes',),('No','No',),), default = "No")
  size_of_pr_team             =       models.IntegerField(default = 0)
  #target
  target_audience             =      models.TextField(max_length = 1000, null = True) #models.ManyToManyField(Sector, null = True)
  pr_goals                    =      models.TextField(max_length = 1000, null = True)
  frequency_of_pr             =      models.CharField(max_length = 100, choices = PR_FREQUENCY, default = "monthly")
  target_audience_location    =      models.CharField(max_length = 250, null= True)
  
  currently_use_pr_db         =      models.BooleanField(default = False)
  social_media_used           =      models.TextField(max_length = 1000, null = True)
  pr_db_used                  =      models.TextField(max_length = 1000, null = True)
  
  require_pr_writing          =      models.BooleanField(default = False)
  require_media_pitching      =      models.BooleanField(default = False)
  do_you_have_newsroom        =      models.BooleanField(default = False)
  name_pr_newsroom_link       =      models.CharField(max_length = 200)

  date_submitted              =      models.DateTimeField(auto_now_add = True)
  action_status               =      models.CharField(max_length = 75, choices = ACTION_STATUS, default = "Contacted")
  # user details
  company_name                =      models.CharField(max_length = 200, null = True)
  contact_name                =      models.CharField(max_length = 125, null = True)
  email                       =      models.CharField(max_length = 125, null = True)
  phone_number                =      models.CharField(max_length = 25,  null = True)

  # tracking
  completed                  =       models.BooleanField(default = False)


  class Meta():
    ordering = ['date_submitted']
    verbose_name_plural = "PR Strategy"

  def __unicode__(self):
    return '%s | %s | %s' %(self.company_name, self.company_type, self.business_type)

  def get_target_audience(self):
    audience_list = "".join(self.target_audience.split(','))
    return audience_list

  def get_pr_goals(self):
    pr_goals = "".join(self.pr_goals.split(','))
    return pr_goals

class BaseRequest(models.Model):
  ticket_number                =     models.CharField(max_length = 14)
  date_requested               =     models.DateTimeField(auto_now_add = True)
  date_closed                  =     models.DateTimeField(null = True, blank = True)
  status                       =     models.CharField(max_length = 25, choices = ACTION_STATUS, default = "new")
  request_outcome              =     models.CharField(max_length = 25, choices = REQUEST_OUTCOME, default = "pending")
  contact_person               =     models.CharField(max_length = 125)
  contact_email                =     models.EmailField(max_length = 255)
  phone_number                 =     models.CharField(max_length = 15)

  class Meta:
    abstract = True


class  ServiceRequest(BaseRequest):
  service_type            =     models.CharField(max_length = 100)
  sector                  =     models.CharField(max_length = 100, choices = ECONOMY_SECTOR)
  brief_description       =     models.TextField(max_length = 500, null = True, blank = True)
  target_media            =     models.CharField(max_length = 125, choices = MEDIA_PLATFORM, null = True)
  time_service_needed     =     models.CharField(max_length = 75, null = True)  
  preferred_call_time     =     models.CharField(max_length = 50, null = True)
  allow_call              =     models.BooleanField(default = False)
  contacted_by            =     models.OneToOneField(User, related_name = "contacted_by", null = True, blank = True)
  closed_by               =     models.OneToOneField(User, related_name = "closed_by", null = True, blank = True)
  # for photo news
  name_of_event           =     models.CharField(max_length = 100, default = "Not Applicable")
  event_date              =     models.DateTimeField(null = True)
  event_time              =     models.CharField(max_length =  10, null = True)
  event_venue             =     models.CharField(max_length = 225, null = True)

  # for blogger distribution request
  blog_list              =     models.ManyToManyField('Blogs')
  total_price            =     models.FloatField(default = 0.0)
  post_content           =     models.TextField(max_length = 3000)
  uploaded_post_content  =     models.FileField(upload_to = "blogger_distribution", help_text = 'for blogger distibution submission')

  # Radio and TV advert request
  page_size              =     models.CharField(max_length = 125, null = True, blank = True)
  page_color             =     models.CharField(max_length = 125, null= True, blank = True, choices = (('black and white', 'black and white',),('color','color',)))
  media_house            =     models.CharField(max_length = 125, null = True)
  region                 =     models.CharField(max_length = 125, null = True)
  adv_duration           =     models.CharField(max_length = 125, null = True)
  adv_service_type       =     models.CharField(max_length = 125, null = True)
  audio_file             =     models.FileField(upload_to = "uploads/audio/", null = True, help_text = 'for Radio advert submission')
  video_file             =     models.FileField(upload_to = "uploads/video/", null = True,help_text = 'for TV advert submission')
  advert_image_file      =     models.FileField(upload_to = "uploads/newspaper/advert", null = True, help_text = 'for newpaper advert submission')
  adv_instructions       =     models.TextField(max_length = 250, null = True)
  # allow_content_editing  =     models.BooleanField(default = False, help_text = 'for newpaper advert submission')



  def __unicode__(self):
    return '%s - %s' %(self.ticket_number, self.service_type)


  class Meta:
    ordering = ('-date_requested',)
    verbose_name_plural = "Service request"



class  InterviewRequest(BaseRequest):
  preferred_interview_date     =     models.DateTimeField()
  preferred_media_house        =     models.ManyToManyField('MediaHouse')
  interview_venue              =     models.TextField(max_length =  300, null = True)
  interview_date               =     models.DateTimeField()
  interview_time               =     models.DateTimeField()
  person_to_be_interviewed     =     models.CharField(max_length = 125)
  contacted_by                 =     models.OneToOneField(User, related_name = "interview_contacted_by", null = True, blank = True)
  closed_by                    =     models.OneToOneField(User, related_name = "interview_closed_by", null = True, blank = True)
 
  def __unicode__(self):
    return '%s - %s' %(self.ticket_number, self.status)

  class Meta:
    ordering = ('-date_requested',)
    verbose_name_plural = "Interview request"


class Package(models.Model):
  category                 =         models.ForeignKey(PressMaterial)
  name                     =         models.CharField(max_length = 75, choices = PACKAGES )
  media_outreach_credit    =         models.CharField(max_length = 25, default = 1)
  online                   =         models.CharField("online_newspaper_publishing", max_length = 5, choices =  BOOLEAN_CHOICES)
  monitoring               =         models.CharField(max_length = 5, choices =  BOOLEAN_CHOICES)
  free_consulting          =         models.CharField(max_length = 5, choices =  BOOLEAN_CHOICES)
  newsroom                 =         models.CharField("Newsroom via EasyPR Media Desk", max_length = 5, choices =  BOOLEAN_CHOICES)
  google_news_inclusions   =         models.CharField(max_length = 5, choices =  BOOLEAN_CHOICES)
  reuters_news_network     =         models.CharField(max_length = 5, choices =  BOOLEAN_CHOICES)
  hyperlinks               =         models.CharField("hyperlinks in online press release", max_length = 5)
  notification             =         models.CharField("publication notification via email", max_length = 5, choices =  BOOLEAN_CHOICES)
  autopost                 =         models.CharField("autopost to social media account", max_length = 5, choices =  BOOLEAN_CHOICES)
  analytics                =         models.CharField("detailed analytics report", max_length = 5, choices =  BOOLEAN_CHOICES)
  expedited                =         models.CharField("expedited release processing", max_length = 5, choices =  BOOLEAN_CHOICES)
  available_on_homepage    =         models.CharField("news made available to journalists, bloggers and researchers via EasyPR homepage", max_length = 5, choices =  BOOLEAN_CHOICES)
  content_writing          =         models.CharField(max_length = 5, choices =  BOOLEAN_CHOICES)
  content_editing          =         models.CharField(max_length = 5, choices =  BOOLEAN_CHOICES)
  featured_package         =         models.CharField(max_length = 5, choices =  BOOLEAN_CHOICES)
  price_naira              =         models.FloatField(max_length = 25, default = 0.0)
  price_dollar             =         models.FloatField(max_length = 25, default = 0.0)
  active                   =         models.BooleanField(default = False)
  is_promo                 =         models.BooleanField(default = False)
  promo_starts             =         models.DateTimeField(auto_now_add = True)
  promo_ends               =         models.DateTimeField(auto_now_add = True)
  promo_price_dollar       =         models.FloatField(max_length = 25, default = 0.0)
  promo_price_naira        =         models.FloatField(max_length = 25, default = 0.0)
 
  def __unicode__(self):
    return '%s' %(self.name)


  # def save(self, *args, **kwargs):
  #   self.price_naira = self.price_dollar * exchange_rate
  #   super(Package, self).save(*args, **kwargs)


  def VAT_N(self):
    return  VAT * self.price_naira


  def VAT_D(self):
    return float(VAT * self.price_dollar)


  def   amount_payable_D(self):
    vat = float(VAT *  self.price_dollar)
    return vat + self.price_dollar

  def   amount_payable_N(self):
    vat = float(VAT * self.price_naira)
    return vat + self.price_naira


  def get_category_packages(self, category):
    pass

  class Meta:
    verbose_name_plural = "Packages"


class Testimonial(models.Model):
  comment           =   models.CharField(max_length = 165)
  date_posted       =   models.DateTimeField(auto_now_add = True)
  posted_by         =   models.CharField(max_length = 150)
  persons_position  =   models.CharField(max_length = 75)
  persons_company   =   models.CharField(max_length = 125)
  persons_image     =   models.FileField(upload_to = "testimonial")

  def __unicode__(self):
    return self.posted_by


class Blogs(models.Model):
  name        =  models.CharField(max_length = 200)
  blog_url    =  models.URLField()
  name_slug   =  models.CharField(max_length = 275)
  category    =  models.CharField(max_length = 125, choices = BLOG_CATEGORIES)
  price       =  models.FloatField(default = 0.0)
  active      =  models.BooleanField(default = True)

  def __unicode__(self):
    return self.name

  class Meta:
    verbose_name_plural = "Blogs"



class Media_Marketing_Bundles(models.Model):
  name        =  models.CharField(max_length = 200)
  name_slug   =  models.CharField(max_length = 275) 
  features    =  models.TextField(max_length = 2000, help_text = "list all features seperated by semi colon")
  price_N     =  models.FloatField(default = 0.0)
  price_D     =  models.FloatField(default = 0.0)
  caption     =  models.TextField(max_length = 150, default = "")
  image       =  models.ImageField(upload_to = 'bundle_tiles')
  thumbnail   =  models.ImageField(upload_to = 'bundle_thumbnails')
  active      =  models.BooleanField(default = True)
  is_request  =  models.BooleanField(default = False)

  def __unicode__(self):
    return '%s' %(self.name)

  class Meta:
    verbose_name_plural = "Marketing Bundles"


  def get_features(self):
    return self.features.split(";") # creates a list of features from textfield

    
class RequestBundleService(BaseRequest):
  bundle    =     models.ForeignKey('Media_Marketing_Bundles')

  def __unicode__(self):
    return '%s | %s' %(self.ticket_number, self.bundle.name)


class KeyVault(models.Model):
  point          =     models.CharField(max_length = 255)
  sc_key         =     models.TextField(max_length = 1000)

  # sc_key         =     models.CharField(max_length = 500)
  # def save(self, *args, **kwargs):
  #   obj  =    AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')

  #   hash_value  =  obj.encrypt(self.sc_key)
  #   self.sc_key  =  hash_value.encode('utf-8')
  #   print "hashed secret key", self.sc_key
  #   super(KeyVault, self).save(*args, **kwargs)

  # def fetch_sc_key(self):
  #   obj  =    AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
  #   # print "unhashed key ", obj.decrypt(self.sc_key)
  #   return self.sc_key
  #   # return obj.decrypt(self.sc_key)


  # def save(self, *args, **kwargs):
  #   hasher  =  Hasher()
  #   hash_key = hasher.encrypt(self.sc_key)
  #   self.sc_key  =  hash_key
  #   print "saved hash key ", hash_key
  #   super(KeyVault, self).save(*args, **kwargs)

  # def fetch_sc_key(self):
  #   hasher  =  Hasher()
  #   return  hasher.decrypt(self.sc_key)





  # def save(self, *args, **kwargs):
  #   hasher  =  Hasher()
  #   hash_key = hasher.encrypt(self.sc_key)
  #   self.sc_key  =  hash_key
  #   print "saved hash key ", hash_key
  #   super(KeyVault, self).save(*args, **kwargs)

  def fetch_sc_key(self):
    return  self.sc_key


