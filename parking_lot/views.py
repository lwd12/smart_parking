from django.shortcuts import render, redirect
import requests

url = 'http://192.168.0.19:9000/insidetheparkinglot/'
API_HOST2 = 'http://192.168.0.19:9000/SessionData/'


def parking(request):
    if request.method == 'GET':
        if 'session' in request.COOKIES:
            session = {}
            session['session'] = request.COOKIES['session']
            responses = requests.post(API_HOST2, data=session)
            data = responses.json()
            req = requests.get(url)
            response = req.json()
            context = {
                'username': data['username'],
                'Parking_lot': response,
            }
            return render(request, 'parking_lot/parking_lot.html', context)
        else:
            return redirect('common:login')
