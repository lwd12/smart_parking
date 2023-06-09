from django.shortcuts import render, redirect
import requests

API_HOST = 'http://3.34.74.107:8000'


def parking(request):
    if request.method == 'GET':  # 세션 여부 확인
        session_id = request.COOKIES.get('session')
        if not session_id:
            return redirect('common:login')
        session_data = {'session': session_id}
        response = requests.post(API_HOST + '/SessionData/', data=session_data).json()
        username = response.get('username')

        parking_data = requests.get(API_HOST + '/insidetheparkinglot/').json()
        context = {'username': username, 'Parking_lot': parking_data}

        return render(request, 'parking_lot/parking_lot.html', context)
