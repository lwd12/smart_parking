
from django.shortcuts import render, redirect, resolve_url
from datetime import datetime
from .SendApi import send_api
import requests
API_HOST = "http://192.168.0.19:9000"
API_HOST2 = 'http://192.168.0.19:9000/SessionData/'
url = 'http://192.168.0.19:9000/answer/'
headers = {
    # "Authorization": "ToKen 750b311fec4b7c0a2a023bd557a149fb1f3a5085",  # 토큰값
    "Content-Type": "application/json",
    "charset": "UTF-8",
    "Accept": "*/*",
}
body = {}
def answer_create(request, question_number):
    now = datetime.now()
    iso_time = now.isoformat()
    if request.method == 'POST':
        if 'session' in request.COOKIES:
            session = {}
            session['session'] = request.COOKIES['session']
            responses = requests.post(API_HOST2, data=session)
            data = responses.json()

            body['content'] = request.POST.get('content')
            body['create_date'] = iso_time
            body['creator'] = data['username']
            body['modify_date'] = None
            body['question_number'] = question_number
            send_api(API_HOST, "/answer/", "POST", headers, body)
            return redirect('pybo:detail', question_number=question_number)
        else:
            return redirect('common:login')


def answer_modify(request, answer_number):

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
                if answer_number == response[x]['answer_number']:
                    content = response[x]['content']
                    context = {
                        'username': data['username'],
                        'login_status': request.COOKIES.get('login_status'),
                        'content': content
                    }
                    return render(request, 'pybo/answer_form.html', context)
        else:
            return redirect('common:login')
    if request.method == "POST":
        if 'session' in request.COOKIES:
            body['content'] = request.POST.get('content')
            body['modify_date'] = iso_time
            send_api(API_HOST, f"/answer/{answer_number}", "PUT", headers, body)
            question_number = ''
            for x in range(len(response)):
                if answer_number == response[x]['answer_number']:
                    question_number = response[x]['question_number']
            return redirect('{}#answer_{}'.format(
                        resolve_url('pybo:detail', question_number=question_number), answer_number))
        else:
            return redirect('common:login')




def answer_delete(request, answer_number):
    if 'session' in request.COOKIES:
        req = requests.get(url)
        response = req.json()
        for x in range(len(response)):
            if answer_number == response[x]['answer_number']:
                question_number = response[x]['question_number']
                send_api(API_HOST, f"/answer/{answer_number}", "DELETE", headers, body)
                return redirect('pybo:detail', question_number=question_number)

    else:
        return redirect('common:login')


