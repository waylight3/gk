from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.db.models import Q
from datetime import datetime, date, timezone
from ipware.ip import get_ip
import html, difflib, json
from django.core.mail import send_mail
from django.http import JsonResponse

def index(request):
	data = {
		'name':'hi',
	}
	return render(request, 'all/index.html', data)