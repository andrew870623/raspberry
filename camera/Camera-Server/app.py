#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response, request

from camera_opencv import Camera

app = Flask(__name__)

def gen2(camera):
    """Returns a single image frame"""
    frame = camera.get_frame()
    yield frame

@app.route('/image')
def image():
    """Returns a single current image for the webcam"""
    cameraID = request.args.get('cid')
    return Response(gen2(Camera()), mimetype='image/jpeg')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/stream')
def stream():
    cameraID = request.args.get('cid')
    #return Response(gen(VideoCamera(cameraID)), mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(gen(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', threaded=True)
