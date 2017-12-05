from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
import requests
import json
from easypr_ng.models import PayDetails, Purchase
from easypr_general.custom_functions import get_random_code
from easypr.settings import PAYSTACK_SECRET_KEY
from easypr_ng.models import KeyVault
import random


class Paystack():
    secret_key  = 'Bearer ' + PAYSTACK_SECRET_KEY

    def ___init__(self):
       pass
    
    @classmethod
    def initiate_transaction(self, request, reference, amount, email, callback_url):
        url      =   'https://api.paystack.co/transaction/initialize'
        headers  =   {'Authorization': self.secret_key, 'Content-Type': 'application/json'}
        data     =   {'reference': reference, 'amount': amount, 'email': email, 'callback_url':callback_url }
        j_data   =   json.dumps(data)
        r        =   requests.post(url, data = j_data, headers = headers, verify = True)
        r_json   =   r.json()
        if r_json['status']  == True:
            r_json_data = r_json['data']
            authorization_url = r_json_data['authorization_url']
            return {'response':'True', 'auth_url':authorization_url}
        else:
            return {'response':'False','error_response':r_json['message']}
           

    def verify_transaction(self, request, txn_ref):
        url = 'https://api.paystack.co/transaction/verify/%s' %txn_ref
        headers = {'Authorization': self.secret_key, 'Content-Type': 'application/json'}
        r = requests.get(url, headers = headers, verify = True)
        r_json = r.json()
        rjson_data = r_json['data']
        if rjson_data['status'] == 'success':
            return 'success'
        return 'failed'

