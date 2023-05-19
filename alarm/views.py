from django.shortcuts import render
import requests
import webbrowser
from rest_framework.response import Response
from rest_framework.views import APIView

base_url = 'http://3.34.74.107:8000/'

state_data = {'state': 'fire'}


class GetData(APIView):
    def post(self, request):
        data = request.POST.get('message')
        webbrowser.open('http://3.34.74.107/alarm/')

        state_data['state'] = data

        return Response(data=state_data)


def alarm(request):
    if request.method == "GET":
        if 'session' in request.COOKIES:
            body = {'session': request.COOKIES['session']}
            responses = requests.post(base_url + 'SessionData/', data=body)
            data = responses.json()

            context = {
                'username': data['username'],
                'alarm_data': state_data['state'],
            }
            return render(request, 'alarm/alarm.html', context)
