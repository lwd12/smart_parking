from django.shortcuts import render, redirect, resolve_url
from .SendApi import send_api
from datetime import datetime
import requests

url = 'http://192.168.0.19:9000/question/'
API_HOST = "http://192.168.0.19:9000"
API_HOST2 = 'http://192.168.0.19:9000/SessionData/'
headers = {
    # "Authorization": "ToKen 750b311fec4b7c0a2a023bd557a149fb1f3a5085",  # 토큰값
    "Content-Type": "application/json",
    "charset": "UTF-8",
    "Accept": "*/*",
}
body = {}
test = {}
def question_create(request):
    session = {}
    session['session'] = request.COOKIES['session']
    responses = requests.post(API_HOST2, data=session)
    data = responses.json()
    now = datetime.now()
    iso_time = now.isoformat()
    if request.method == 'GET':
        if 'session' in request.COOKIES:
            context = {
                'username': data['username']
            }
            return render(request, 'pybo/question_form.html', context)
        else:
            return redirect('common:login')

    if request.method == 'POST':
        if 'session' in request.COOKIES:
            body['subject'] = request.POST.get('subject')
            body['content'] = request.POST.get('content')
            body['create_datetime'] = iso_time
            body['modify_datetime'] = None
            body['creator'] = data['username']
            body['etc'] = '공지'
            send_api(API_HOST, "/question/", "POST", headers, body)
            return redirect('pybo:index')
        else:
            return redirect('common:login')


def question_modify(request, question_number):

    now = datetime.now()
    iso_time = now.isoformat()
    req = requests.get(url)
    response = req.json()
    if request.method == 'GET':
        if 'session' in request.COOKIES:
            session = {}
            session['session'] = request.COOKIES['session']
            responses = requests.post(API_HOST2, data=session)
            data = responses.json()
            for x in range(len(response)):
                if question_number == response[x]['question_number']:
                    subject = response[x]['subject']
                    content = response[x]['content']
                    context = {
                        'username': data['username'],
                        'form_subject': subject,
                        'form_content': content,

                    }
                    return render(request, 'pybo/question_form.html', context)
        else:
            return redirect('common:login')
    if request.method == "POST":
        if 'session' in request.COOKIES:
            body['subject'] = request.POST.get('subject')
            body['content'] = request.POST.get('content')
            body['modify_datetime'] = iso_time
            print(body)
            send_api(API_HOST, f"/question/{question_number}", "PUT", headers, body)
            return redirect('/pybo/{}/#question_{}'.format(question_number, question_number))
        else:
            return redirect('common:login')


def question_delete(request, question_number):
    if 'session' in request.COOKIES:
        send_api(API_HOST, f"/question/{question_number}", "DELETE", headers, body)
        return redirect('pybo:index')
    else:
        return redirect('common:login')
