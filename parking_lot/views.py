from django.shortcuts import render
import numpy as np
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2
import threading


def parking(request):
    return render(request, 'parking_lot/parking_lot.html')
