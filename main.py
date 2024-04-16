from flask import Flask, request, render_template
from multiprocessing import Process, Value
from ultralytics import YOLO
from ultralytics.solutions import object_counter
import cv2

app = Flask(__name__)

model = YOLO("yolov8n.pt")
classes_to_count = [0, 2]  # person and car classes for count
count = Value('i', 0)


def run_object_detection(ip, count):
    cap = cv2.VideoCapture(f"http://{ip}:81/stream")
    assert cap.isOpened(), "Error reading video file"
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    line_points = [(w * 3 / 4, h), (w * 3 / 4, 0)]
    # Video writer
    video_writer = cv2.VideoWriter("object_counting_output.avi",
                                   cv2.VideoWriter_fourcc(*'mp4v'),
                                   fps,
                                   (w, h))

    # Init Object Counter
    counter = object_counter.ObjectCounter()
    counter.set_args(view_img=True,
                     reg_pts=line_points,
                     classes_names=model.names,
                     draw_tracks=True,
                     line_thickness=2)

    while cap.isOpened():
        success, im0 = cap.read()
        if not success:
            print("Video frame is empty or video processing has been successfully completed.")
            break
        tracks = model.track(im0, persist=True, show=False,
                             classes=classes_to_count)

        im0 = counter.start_counting(im0, tracks)
        video_writer.write(im0)
        if 'perso' in counter.class_wise_count:
            if counter.class_wise_count['perso']['in'] >= 1 or counter.class_wise_count['perso']['out'] >= 1:
                count.value += counter.class_wise_count['perso']['in']
                count.value -= counter.class_wise_count['perso']['out']
                counter.class_wise_count['perso']['in'] = 0
                counter.class_wise_count['perso']['out'] = 0

    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()


@app.route('/', methods=['POST'])
def run_object_detection_on_request():
    data = request.get_json()
    ip_address = data.get('ip')
    print(ip_address)
    # Run object detection in a separate process
    p = Process(target=run_object_detection, args=(ip_address, count))
    p.start()
    print("Object detection process started")
    return 'Object detection process started.'

@app.route('/update')
def current():
    current = count.value
    return str(current)

@app.route('/total')
def total():
    return render_template('index.html')

@app.route('/update/<num>')
def update(num):
    count.value += int(num)
    return "Done"

if __name__ == '__main__':
    app.run()

