from django.shortcuts import render,  redirect
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2
import threading
import requests

API_HOST2 = 'http://192.168.0.19:9000/SessionData/'
def home(request):
    if 'session' in request.COOKIES:
        session = {}
        session['session'] = request.COOKIES['session']
        responses = requests.post(API_HOST2, data=session)
        data = responses.json()
        context = {
            'username' : data['username'],
        }
        return render(request, 'camera/camera.html',context)
    else:
        return redirect('common:login')


# 카메라 관련 클래스
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

        self.recording = False
        self.scale = 1

    def __del__(self):
        self.video.release()
    def read(self):
        success, image = self.video.read()
        if success:
            return success, image
        else:
            raise ValueError("Failed to read video frame")

    def get_frame(self):
        frame = self.frame
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()


def gen(camera):
    while True:
        frame = camera.get_frame()

        yield (b'--frame\r\n'
               b'Content-Type: images/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# def gen(camera):
#     while True:
#         # 한 프레임씩 읽어오기
#         success, images = camera.read()
#         if not success:
#             continue
#
#         # 이미지를 JPEG로 압축
#         _, jpeg = cv2.imencode('.jpg', images)
#
#         # HTTP 응답에 JPEG 이미지 넣기
#         yield (b'--frame\r\n'
#                b'Content-Type: images/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')


@gzip.gzip_page
def detectme(request):
    try:
        cam = VideoCamera()  # 웹캠 호출
        # frame단위로 이미지를 계속 송출한다
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except cv2.error as e:
        print(e)
        for k in dir(e):
            if k[0:2] != "__":
                print("e.%s = %s" % (k, getattr(e, k)))

        # handle error: empty frame
        if e.err == "!_src.empty()":
            pass


def page_not_found(request, exception):
    return render(request, 'common/404.html', {})
