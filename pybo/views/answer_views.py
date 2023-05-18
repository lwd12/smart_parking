from django.shortcuts import render, redirect, resolve_url
from datetime import datetime
from .SendApi import send_api
import requests

base_url = 'http://192.168.0.19:9000'

headers = {
    # "Authorization": "ToKen 750b311fec4b7c0a2a023bd557a149fb1f3a5085",  # 토큰값
    "Content-Type": "application/json",
    "charset": "UTF-8",
    "Accept": "*/*",
}
body = {}


def answer_create(request, question_number):  # 댓글 생성
    now = datetime.now()
    iso_time = now.isoformat()
    if request.method == 'POST':
        if 'session' in request.COOKIES:
            session = {}
            session['session'] = request.COOKIES['session']
            responses = requests.post(base_url + '/SessionData/', data=session)
            data = responses.json()

            body['content'] = request.POST.get('content')  # 내용
            body['create_date'] = iso_time  # 작성 시간
            body['creator'] = data['username']  # 작성자
            body['modify_date'] = None  # 수정 시간
            body['question_number'] = question_number  # 질문 번호
            send_api(base_url, "/answer/", "POST", headers, body)
            return redirect('pybo:detail', question_number=question_number)
        else:
            return redirect('common:login')


def answer_modify(request, answer_number):  # 댓글 수정
    now = datetime.now()
    iso_time = now.isoformat()
    req = requests.get(url)
    response = req.json()
    if request.method == 'GET':
        if 'session' in request.COOKIES:
            session = {'session': request.COOKIES['session']}
            responses = requests.post(base_url + '/SessionData/', data=session)
            data = responses.json()
            for x in range(len(response)):
                if answer_number == response[x]['answer_number']:  # 선택한 댓글 내용 불러오기
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
            send_api(base_url, f"/answer/{answer_number}", "PUT", headers, body)
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
        req = requests.get(base_url + '/answer/')
        response = req.json()
        for x in range(len(response)):
            if answer_number == response[x]['answer_number']:
                question_number = response[x]['question_number']
                send_api(base_url, f"/answer/{answer_number}", "DELETE", headers, body)
                return redirect('pybo:detail', question_number=question_number)

    else:
        return redirect('common:login')
