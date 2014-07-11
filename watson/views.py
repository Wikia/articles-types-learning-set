import json
import urllib
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from watson.status import Status
from watson.forms.login import WatsonLoginForm
from watson.models import Session, Type, Quality, Kind, MobileQuality
from watson.watson_exceptions import WatsonException
from watson.exporter import Exporter


# Create your views here.
def login(request):
    if request.method == 'POST':
        form = WatsonLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['user'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    return redirect('main')
    else:
        form = WatsonLoginForm()

    return render(request, 'login.html', {'form': form})


def main(request, session, number):
    if request.user.is_authenticated():
        status = Status(user=request.user)
        try:
            status.set(session, number)
        except WatsonException as e:
            return HttpResponse(e.__unicode__(), status=400)

        if request.method == 'POST':
            res = status.set_metric(request.POST['metric'], request.POST['type'])
            return HttpResponse(res, status=200)
        return render(request, 'main.html',
                      {
                          'state': {'session': status.get_current_session_name(), 'number': status.get_current_number()},
                          'url': status.get_url(),
                          'categories': Type.get_in_categories(),
                          'quality_levels': Quality.objects.all(),
                          'kinds': Kind.objects.all(),
                          'mobile_quality_levels': MobileQuality.objects.all(),
                          'set': status.get_current()
                      }
                      )
    else:
        return redirect('login')


def sessions(request):
    if request.user.is_authenticated():
        result = []
        data = Session.objects.all()
        for item in data:
            result.append({'name': item.name})
        output = json.dumps(result)
        return HttpResponse(output, content_type="application/json")
    else:
        raise HttpResponse(status=401)


def next(request):
    if request.user.is_authenticated():
        status = Status(request.user)
        output = json.dumps({"path": '/watson/%s/%d' % (urllib.quote(status.get_current_session_name()), status.get_next())})
        return HttpResponse(output, content_type="application/json")
    else:
        raise HttpResponse(status=401)


def export(request, session):
    if request.user.is_authenticated():
        exporter = Exporter(session)
        exporter.run()

        file = open(Exporter.file_name, 'r')

        response = HttpResponse(file, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % Exporter.file_name
        return response
    else:
        raise HttpResponse(status=401)
