from django.core.paginator import Paginator
from django.shortcuts import render, redirect
import requests
from datetime import datetime
from requests.exceptions import ConnectTimeout

url = 'http://192.168.0.19:9000/question/'

urls = 'http://192.168.0.19:9000/answer/'

API_HOST = 'http://192.168.0.19:9000/SessionData/'


def qdata(question_number):
    try:
        req = requests.get(url)
        response = req.json()

        for x in range(len(response)):
            id = response[x]['question_number']
            if id == question_number:
                subject = response[x]['subject']
                content = response[x]['content']
                create_date = response[x]['create_datetime']
                if not is_date_format(create_date):
                    create_dates = datetime.fromisoformat(create_date)
                    create_date = create_dates.strftime("%Y년 %m월 %d일 %H시 %M분")
                creator = response[x]['creator']
                modify_date = response[x]['modify_datetime']
                if modify_date:
                    if not is_date_format(modify_date):
                        modify_dates = datetime.fromisoformat(modify_date)
                        modify_date = modify_dates.strftime("%Y년 %m월 %d일 %H시 %M분")
                return id, subject, content, create_date, creator, modify_date
    except ConnectTimeout:
        id = None
        subject = None
        content = None
        create_date = None
        creator = None
        modify_date = None
        return id, subject, content, create_date, creator, modify_date


def adata(question_id):
    try:
        reqs = requests.get(urls)
        responses = reqs.json()
        answer = []
        count = 0
        for x in range(len(responses)):
            setdata = {}
            if question_id == responses[x]['question_number']:
                count += 1
                setdata['answer_number'] = responses[x]['answer_number']
                setdata['content'] = responses[x]['content']
                setdata['create_date'] = responses[x]['create_date']
                setdata['question_number'] = responses[x]['question_number']
                if not is_date_format(setdata['create_date']):
                    create_dates = datetime.fromisoformat(setdata['create_date'])
                    create_date = create_dates.strftime("%Y년 %m월 %d일 %H시 %M분")
                    setdata['create_date'] = create_date
                setdata['creator'] = responses[x]['creator']
                setdata['modify_date'] = responses[x]['modify_date']
                if setdata['modify_date']:
                    if not is_date_format(setdata['modify_date']):
                        modify_dates = datetime.fromisoformat(setdata['modify_date'])
                        modify_date = modify_dates.strftime("%Y년 %m월 %d일 %H시 %M분")
                        setdata['modify_date'] = modify_date
                answer.append(setdata)
    except ConnectTimeout:
        answer = None
        count = None

    return answer, count


def count(question_id):
    try:
        reqs = requests.get(urls)
        responses = reqs.json()
        return sum(1 for data in responses if data['question_number'] == question_id)
    except ConnectTimeout:
        return None


def is_date_format(string):
    try:
        datetime.strptime(string, "%Y년 %m월 %d일 %H시 %M분")
        return True
    except ValueError:
        return False


def change_datetime_format(date_string):
    if date_string:
        try:
            date_obj = datetime.fromisoformat(date_string)
            return date_obj.strftime("%Y년 %m월 %d일 %H시 %M분")
        except ValueError:
            pass
    return date_string


def change():
    try:
        req = requests.get(url)
        responses = req.json()
        sorted_data = []
        for data in responses:
            data['create_datetime'] = change_datetime_format(data['create_datetime'])
            data['modify_datetime'] = change_datetime_format(data['modify_datetime'])
            data['count'] = count(data['question_number'])
            sorted_data.append(data)

        sorted_data = sorted(sorted_data, key=lambda x: x['question_number'], reverse=True)
        return sorted_data
    except ConnectTimeout:
        return []


def index(request):
    if request.method == 'GET':

        page = request.GET.get('page', '1')  # 페이지
        kw = request.GET.get('kw', '')  # 검색어
        repon = change()

        new_list = []
        results = []
        for x in repon:
            new_dict = {k: v for k, v in x.items() if
                        k not in ['question_number', 'create_datetime', 'modify_datetime']}
            new_list.append(new_dict)
            for key in new_dict:
                value = new_dict[key]
                if kw in str(value):
                    results.append(x)
                    break
        if kw:
            repon = results
        else:
            repon = [new_list[i] | repon[i] for i in range(len(repon))]

        paginator = Paginator(repon, 10)
        page_obj = paginator.get_page(page)

        if 'session' in request.COOKIES:
            session = {}
            session['session'] = request.COOKIES['session']
            responses = requests.post(API_HOST, data=session)
            data = responses.json()

            context = {'question_list': page_obj,
                       'page': page,
                       'kw': kw,
                       'username': data['username']
                       }
            return render(request, 'pybo/question_list.html', context)
        else:
            return redirect('common:login')


def detail(request, question_number):
    if request.method == 'GET':

        answer, count = adata(question_number)
        id, subject, content, create_date, creator, modify_date = qdata(question_number)
        print(creator)
        if 'session' in request.COOKIES:
            body = {}
            body['session'] = request.COOKIES['session']
            responses = requests.post(API_HOST, data=body)
            data = responses.json()
            context = {'question_number': id,
                       'question_subject': subject,
                       'question_content': content,
                       'question_modify_date': modify_date,
                       'question_creator': creator,
                       'question_create_date': create_date,
                       'AnswerAll': answer,
                       'Answer_count': count,
                       'username': data['username']
                       }
            return render(request, 'pybo/question_detail.html', context)
        else:
            return redirect('common:login')
