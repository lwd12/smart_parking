from django.shortcuts import render, redirect, resolve_url
from .SendApi import send_api
from datetime import datetime
import requests

base_url = 'http://3.34.74.107:8000'
headers = {
    # "Authorization": "ToKen 750b311fec4b7c0a2a023bd557a149fb1f3a5085",  # 토큰값
    "Content-Type": "application/json",
    "charset": "UTF-8",
    "Accept": "*/*",
}


def question_create(request):  # 질문 작성
    session = {'session': request.COOKIES['session']}
    responses = requests.post(base_url + '/SessionData/', data=session)
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
            body = {'subject': request.POST.get('subject'),
                    'content': request.POST.get('content'),
                    'create_datetime': iso_time,
                    'modify_datetime': None,
                    'creator': data['username'],
                    'etc': '공지'}
            send_api(base_url, "/question/", "POST", headers, body)
            return redirect('pybo:index')
        else:
            return redirect('common:login')


def question_modify(request, question_number):  # 질문 수정
    now = datetime.now()
    iso_time = now.isoformat()
    req = requests.get(base_url + '/question/')
    response = req.json()
    if request.method == 'GET':
        if 'session' in request.COOKIES:
            session = {'session': request.COOKIES['session']}
            responses = requests.post(base_url + '/SessionData/', data=session)
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

            body = {'subject': request.POST.get('subject'),
                    'content': request.POST.get('content'),
                    'modify_datetime': iso_time}
            print(body)
            send_api(base_url, f"/question/{question_number}", "PUT", headers, body)

            return redirect('/pybo/{}/#question_{}'.format(question_number, question_number))
        else:
            return redirect('common:login')


def question_delete(request, question_number):  # 질문 삭제
    if 'session' in request.COOKIES:
        body = {}
        send_api(base_url, f"/question/{question_number}", "DELETE", headers, body)
        return redirect('pybo:index')
    else:
        return redirect('common:login')
