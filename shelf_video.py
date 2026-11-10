# import cv2
# import numpy as np
# import os
# import time

# LOW_THRESHOLD = 0.12
# EMPTY_THRESHOLD = 0.05

# WIN_NAME = "Draw ROIs"
# current_frame = None
# rois = []
# current_points = []


# class ROI:
#     def __init__(self, shelf_id, shelf_name, row_id, box_id, points):
#         self.shelf_id = shelf_id
#         self.shelf_name = shelf_name
#         self.row_id = row_id
#         self.box_id = box_id
#         self.points = np.array(points, dtype=np.int32).reshape((-1, 1, 2))

#     def get_bbox(self):
#         x, y, w, h = cv2.boundingRect(self.points)
#         return x, y, x + w, y + h


# class ShelfMonitor:
#     def __init__(self, roi_list):
#         self.rois = roi_list
#         self.last_alert_time = {}
#         self.alert_interval = 10
#         self.state_history = {}

#     def calculate_occupancy(self, frame, roi_obj):
#         x1, y1, x2, y2 = roi_obj.get_bbox()

#         if x1 >= x2 or y1 >= y2:
#             return 0.0

#         mask = np.zeros(frame.shape[:2], dtype=np.uint8)
#         cv2.fillPoly(mask, [roi_obj.points], 255)

#         roi = frame[y1:y2, x1:x2]
#         mask_roi = mask[y1:y2, x1:x2]

#         if roi.size == 0 or mask_roi.size == 0:
#             return 0.0

#         gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
#         blur = cv2.GaussianBlur(gray, (5, 5), 0)
#         edges = cv2.Canny(blur, 50, 150)

#         masked_edges = cv2.bitwise_and(edges, edges, mask=mask_roi)
#         valid_pixels = np.count_nonzero(mask_roi)

#         if valid_pixels == 0:
#             return 0.0

#         return np.count_nonzero(masked_edges) / valid_pixels

#     def decision_making(self, occupancy):
#         if occupancy >= LOW_THRESHOLD:
#             return "OK"
#         elif occupancy >= EMPTY_THRESHOLD:
#             return "LOW"
#         else:
#             return "EMPTY"

#     def should_alert(self, roi_key, state):
#         now = time.time()
#         last_time = self.last_alert_time.get(roi_key, 0)
#         last_state = self.state_history.get(roi_key)

#         if state == "OK":
#             self.state_history[roi_key] = state
#             return False

#         if last_state != state:
#             self.last_alert_time[roi_key] = now
#             self.state_history[roi_key] = state
#             return True

#         if now - last_time >= self.alert_interval:
#             self.last_alert_time[roi_key] = now
#             self.state_history[roi_key] = state
#             return True

#         self.state_history[roi_key] = state
#         return False

#     def process_frame(self, frame):
#         display_frame = frame.copy()
#         alerts = []

#         for roi_obj in self.rois:
#             occupancy = self.calculate_occupancy(frame, roi_obj)
#             state = self.decision_making(occupancy)

#             x1, y1, x2, y2 = roi_obj.get_bbox()
#             roi_key = f"{roi_obj.shelf_name}_R{roi_obj.row_id}_B{roi_obj.box_id}"

#             if state == "OK":
#                 color = (0, 255, 0)
#             elif state == "LOW":
#                 color = (0, 255, 255)
#                 alerts.append((roi_key, state))
#             else:
#                 color = (0, 0, 255)
#                 alerts.append((roi_key, state))

#             label = f"{roi_key}: {state} ({occupancy:.2f})"
#             cv2.polylines(display_frame, [roi_obj.points], True, color, 2)
#             cv2.putText(
#                 display_frame,
#                 label,
#                 (x1, max(20, y1 - 10)),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.55,
#                 color,
#                 2
#             )

#         return display_frame, alerts


# def redraw():
#     global current_frame, rois, current_points

#     img = current_frame.copy()

#     for roi_obj in rois:
#         cv2.polylines(img, [roi_obj.points], True, (255, 0, 0), 2)

#     if current_points:
#         for i, p in enumerate(current_points):
#             cv2.circle(img, p, 5, (0, 255, 0), -1)
#             if i > 0:
#                 cv2.line(img, current_points[i - 1], p, (0, 255, 0), 1)

#     cv2.putText(
#         img,
#         "Click 4 corners per ROI | q=finish | c=undo last ROI | r=clear all",
#         (10, 25),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         0.6,
#         (0, 255, 255),
#         2
#     )

#     cv2.imshow(WIN_NAME, img)


# def mouse_callback(event, x, y, flags, param):
#     global current_points, rois

#     if event == cv2.EVENT_LBUTTONDOWN:
#         current_points.append((x, y))
#         print(f"Point {len(current_points)}: ({x}, {y})")

#         if len(current_points) == 4:
#             roi_id = len(rois) + 1
#             rois.append(ROI(1, "Shelf_A", roi_id, roi_id, current_points))
#             print(f"ROI saved: {current_points}")
#             current_points = []

#         redraw()


# def draw_rois(frame):
#     global current_frame, rois, current_points

#     rois = []
#     current_points = []
#     current_frame = frame.copy()

#     cv2.namedWindow(WIN_NAME, cv2.WINDOW_NORMAL)
#     cv2.setMouseCallback(WIN_NAME, mouse_callback)
#     redraw()

#     while True:
#         key = cv2.waitKey(1) & 0xFF

#         if key == ord('q'):
#             break
#         elif key == ord('c') and rois:
#             rois.pop()
#             redraw()
#         elif key == ord('r'):
#             rois.clear()
#             current_points = []
#             redraw()

#     cv2.destroyWindow(WIN_NAME)
#     return rois


# def save_alert_snapshot(frame, alert_text):
#     folder = "alerts"
#     os.makedirs(folder, exist_ok=True)

#     timestamp = time.strftime("%Y%m%d_%H%M%S")
#     filename = os.path.join(folder, f"alert_{timestamp}.jpg")

#     cv2.putText(
#         frame,
#         alert_text,
#         (20, 40),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         1.0,
#         (0, 0, 255),
#         3
#     )

#     cv2.imwrite(filename, frame)
#     print(f"Alert snapshot saved: {filename}")


# def open_stream(rtsp_url):
#     cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
#     return cap


# def main():
#     rtsp_url = "rtsp://admin:Pugenix%402026@192.168.31.245:554/cam/realmonitor?channel=5&subtype=0"

#     cap = open_stream(rtsp_url)

#     if not cap.isOpened():
#         print("Error: Unable to open RTSP stream")
#         return

#     ret, first_frame = cap.read()
#     if not ret or first_frame is None:
#         print("Error: Unable to read first frame from stream")
#         cap.release()
#         return

#     selected_rois = draw_rois(first_frame)

#     if not selected_rois:
#         print("No ROI selected. Exiting.")
#         cap.release()
#         return

#     monitor = ShelfMonitor(selected_rois)

#     max_failed_frames = 50
#     failed_frames = 0

#     while True:
#         ret, frame = cap.read()

#         if not ret or frame is None:
#             failed_frames += 1
#             print(f"Warning: Frame not received from stream ({failed_frames}/{max_failed_frames})")
#             time.sleep(0.1)

#             if failed_frames >= max_failed_frames:
#                 print("Trying to reconnect RTSP stream...")
#                 cap.release()
#                 time.sleep(2)
#                 cap = open_stream(rtsp_url)

#                 if not cap.isOpened():
#                     print("Reconnect failed. Retrying...")
#                     time.sleep(2)
#                     continue

#                 failed_frames = 0

#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#             continue

#         failed_frames = 0

#         processed_frame, alerts = monitor.process_frame(frame)

#         if alerts:
#             y0 = 30
#             for i, (roi_key, state) in enumerate(alerts):
#                 color = (0, 0, 255) if state == "EMPTY" else (0, 255, 255)
#                 text = f"{roi_key}: {state}"

#                 cv2.putText(
#                     processed_frame,
#                     text,
#                     (20, y0 + i * 30),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.8,
#                     color,
#                     2
#                 )

#                 if monitor.should_alert(roi_key, state):
#                     print(f"ALERT -> {roi_key} is {state}")
#                     save_alert_snapshot(processed_frame.copy(), f"ALERT: {roi_key} {state}")

#         cv2.imshow("Live Shelf Monitoring", processed_frame)

#         key = cv2.waitKey(1) & 0xFF
#         if key == ord('q'):
#             print("Stopped by user.")
#             break

#     cap.release()
#     cv2.destroyAllWindows()


# if __name__ == "__main__":
#     main()

import cv2
import numpy as np
import os
import time
from ultralytics import YOLO

LOW_THRESHOLD = 0.12
EMPTY_THRESHOLD = 0.03

WIN_NAME = "Draw Shelf ROIs"
PERSON_ZONE_WIN = "Draw Person Zone"
LIVE_WIN = "Live Shelf Monitoring"

DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

OUTPUT_DIR = "evidence_videos"
ALERT_DIR = "alerts"

current_frame = None
rois = []
current_points = []
person_zone_points = []


class ROI:
    def __init__(self, shelf_id, shelf_name, row_id, box_id, points):
        self.shelf_id = shelf_id
        self.shelf_name = shelf_name
        self.row_id = row_id
        self.box_id = box_id
        self.points = np.array(points, dtype=np.int32).reshape((-1, 1, 2))

    def get_bbox(self):
        x, y, w, h = cv2.boundingRect(self.points)
        return x, y, x + w, y + h


class ShelfMonitor:
    def __init__(self, roi_list):
        self.rois = roi_list
        self.last_alert_time = {}
        self.alert_interval = 10
        self.state_history = {}

    def calculate_occupancy(self, frame, roi_obj):
        x1, y1, x2, y2 = roi_obj.get_bbox()

        if x1 >= x2 or y1 >= y2:
            return 0.0

        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [roi_obj.points], 255)

        roi = frame[y1:y2, x1:x2]
        mask_roi = mask[y1:y2, x1:x2]

        if roi.size == 0 or mask_roi.size == 0:
            return 0.0

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)

        masked_edges = cv2.bitwise_and(edges, edges, mask=mask_roi)
        valid_pixels = np.count_nonzero(mask_roi)

        if valid_pixels == 0:
            return 0.0

        return np.count_nonzero(masked_edges) / valid_pixels

    def decision_making(self, occupancy):
        if occupancy >= LOW_THRESHOLD:
            return "OK"
        elif occupancy >= EMPTY_THRESHOLD:
            return "LOW"
        return "EMPTY"

    def should_alert(self, roi_key, state):
        now = time.time()
        last_time = self.last_alert_time.get(roi_key, 0)
        last_state = self.state_history.get(roi_key)

        if state == "OK":
            self.state_history[roi_key] = state
            return False

        if last_state != state:
            self.last_alert_time[roi_key] = now
            self.state_history[roi_key] = state
            return True

        if now - last_time >= self.alert_interval:
            self.last_alert_time[roi_key] = now
            self.state_history[roi_key] = state
            return True

        self.state_history[roi_key] = state
        return False

    def process_frame(self, frame):
        display_frame = frame.copy()
        alerts = []

        for roi_obj in self.rois:
            occupancy = self.calculate_occupancy(frame, roi_obj)
            print(occupancy)
            state = self.decision_making(occupancy)

            x1, y1, x2, y2 = roi_obj.get_bbox()
            roi_key = f"{roi_obj.shelf_name}_R{roi_obj.row_id}_B{roi_obj.box_id}"

            if state == "OK":
                color = (0, 255, 0)
            elif state == "LOW":
                color = (0, 255, 255)
                alerts.append((roi_key, state))
            else:
                color = (0, 0, 255)
                alerts.append((roi_key, state))

            label = "" #f"{roi_key}: {state} ({occupancy:.2f})"
            cv2.polylines(display_frame, [roi_obj.points], True, color, 2)
            cv2.putText(
                display_frame,
                label,
                (x1, max(20, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                color,
                2,
            )

        return display_frame, alerts


def save_alert_snapshot(frame, alert_text):
    os.makedirs(ALERT_DIR, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(ALERT_DIR, f"alert_{timestamp}.jpg")

    cv2.putText(
        frame,
        alert_text,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 0, 255),
        3,
    )
    cv2.imwrite(filename, frame)
    print(f"Alert snapshot saved: {filename}")


def open_stream(rtsp_url):
    return cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)


def create_video_writer(width, height, fps):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f"evidence_{timestamp}.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not writer.isOpened():
        raise RuntimeError("Could not create evidence video writer")

    print(f"Evidence video will be saved to: {output_path}")
    return writer, output_path


def get_stream_fps(cap):
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps is None or fps <= 1 or fps > 120:
        fps = 20.0
    return fps


def prepare_display_frame(frame):
    return cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))


def redraw_shelf_rois():
    global current_frame, rois, current_points

    img = current_frame.copy()

    for roi_obj in rois:
        cv2.polylines(img, [roi_obj.points], True, (255, 0, 0), 2)

    if current_points:
        for i, p in enumerate(current_points):
            cv2.circle(img, p, 5, (0, 255, 0), -1)
            if i > 0:
                cv2.line(img, current_points[i - 1], p, (0, 255, 0), 1)

    cv2.putText(
        img,
        "Click 4 corners per shelf ROI | q=finish | c=undo | r=clear",
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 255),
        2,
    )
    cv2.imshow(WIN_NAME, img)


def mouse_callback_shelf(event, x, y, flags, param):
    global current_points, rois

    if event == cv2.EVENT_LBUTTONDOWN:
        current_points.append((x, y))
        print(f"Shelf ROI Point {len(current_points)}: ({x}, {y})")

        if len(current_points) == 4:
            roi_id = len(rois) + 1
            rois.append(ROI(1, "Shelf_A", roi_id, roi_id, current_points.copy()))
            print(f"Shelf ROI saved: {current_points}")
            current_points = []

        redraw_shelf_rois()


def draw_shelf_rois(frame):
    global current_frame, rois, current_points

    rois = []
    current_points = []
    current_frame = frame.copy()

    cv2.namedWindow(WIN_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WIN_NAME, DISPLAY_WIDTH, DISPLAY_HEIGHT)
    cv2.setMouseCallback(WIN_NAME, mouse_callback_shelf)
    redraw_shelf_rois()

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("c") and rois:
            rois.pop()
            redraw_shelf_rois()
        elif key == ord("r"):
            rois.clear()
            current_points = []
            redraw_shelf_rois()

    cv2.destroyWindow(WIN_NAME)
    return rois


def redraw_person_zone():
    global current_frame, person_zone_points

    img = current_frame.copy()

    for i, p in enumerate(person_zone_points):
        cv2.circle(img, p, 5, (0, 0, 255), -1)
        if i > 0:
            cv2.line(img, person_zone_points[i - 1], p, (0, 0, 255), 2)

    if len(person_zone_points) == 4:
        pts = np.array(person_zone_points, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(img, [pts], True, (0, 0, 255), 2)

    cv2.putText(
        img,
        "Click 4 corners for PERSON ZONE | q=finish | r=clear",
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 255),
        2,
    )
    cv2.imshow(PERSON_ZONE_WIN, img)


def mouse_callback_person_zone(event, x, y, flags, param):
    global person_zone_points

    if event == cv2.EVENT_LBUTTONDOWN and len(person_zone_points) < 4:
        person_zone_points.append((x, y))
        print(f"Person Zone Point {len(person_zone_points)}: ({x}, {y})")
        redraw_person_zone()


def draw_person_zone(frame):
    global current_frame, person_zone_points

    person_zone_points = []
    current_frame = frame.copy()

    cv2.namedWindow(PERSON_ZONE_WIN, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(PERSON_ZONE_WIN, DISPLAY_WIDTH, DISPLAY_HEIGHT)
    cv2.setMouseCallback(PERSON_ZONE_WIN, mouse_callback_person_zone)
    redraw_person_zone()

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") and len(person_zone_points) == 4:
            break
        elif key == ord("r"):
            person_zone_points = []
            redraw_person_zone()

    cv2.destroyWindow(PERSON_ZONE_WIN)
    return np.array(person_zone_points, dtype=np.int32).reshape((-1, 1, 2))


def point_inside_polygon(point, polygon):
    px, py = point
    return cv2.pointPolygonTest(
        np.array(polygon, dtype=np.int32),
        (float(px), float(py)),
        False
    ) >= 0


def detect_people_yolo(frame, model, conf=0.4):
    results = model.predict(frame, conf=conf, verbose=False)
    persons = []

    if not results:
        return persons

    result = results[0]
    if result.boxes is None:
        return persons

    boxes = result.boxes
    xyxy = boxes.xyxy.cpu().numpy() if boxes.xyxy is not None else []
    cls = boxes.cls.cpu().numpy().astype(int) if boxes.cls is not None else []
    confs = boxes.conf.cpu().numpy() if boxes.conf is not None else []

    for box, class_id, score in zip(xyxy, cls, confs):
        if class_id != 0:
            continue

        x1, y1, x2, y2 = box.astype(int)
        persons.append((x1, y1, x2, y2, float(score)))

    return persons


def person_in_zone(frame, person_zone, model, conf=0.4):
    persons = detect_people_yolo(frame, model, conf=conf)
    detected = False
    person_boxes = []

    for x1, y1, x2, y2, score in persons:
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        in_zone = point_inside_polygon((cx, cy), person_zone)
        person_boxes.append((x1, y1, x2, y2, score, in_zone))

        if in_zone:
            detected = True

    return detected, person_boxes


def main():
    rtsp_url = "rtsp://admin:Pugenix%402026@127.0.0.1:8554/cam/realmonitor?channel=4&subtype=0"
    yolo_model_path = "yolov8n.pt"

    cap = open_stream(rtsp_url)
    if not cap.isOpened():
        print("Error: Unable to open RTSP stream")
        return

    ret, first_frame = cap.read()
    if not ret or first_frame is None:
        print("Error: Unable to read first frame from stream")
        cap.release()
        return

    selected_rois = draw_shelf_rois(first_frame)
    if not selected_rois:
        print("No shelf ROI selected. Exiting.")
        cap.release()
        return

    person_zone = draw_person_zone(first_frame)
    if person_zone is None or len(person_zone) != 4:
        print("No person zone selected. Exiting.")
        cap.release()
        return

    print("Loading YOLO model...")
    model = YOLO(yolo_model_path)
    monitor = ShelfMonitor(selected_rois)

    cv2.namedWindow(LIVE_WIN, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(LIVE_WIN, DISPLAY_WIDTH, DISPLAY_HEIGHT)

    fps = get_stream_fps(cap)
    video_writer, video_path = create_video_writer(DISPLAY_WIDTH, DISPLAY_HEIGHT, fps)

    max_failed_frames = 50
    failed_frames = 0

    try:
        while True:
            ret, frame = cap.read()

            if not ret or frame is None:
                failed_frames += 1
                print(f"Warning: Frame not received from stream ({failed_frames}/{max_failed_frames})")
                time.sleep(0.1)

                if failed_frames >= max_failed_frames:
                    print("Trying to reconnect RTSP stream...")
                    cap.release()
                    time.sleep(2)
                    cap = open_stream(rtsp_url)

                    if not cap.isOpened():
                        print("Reconnect failed. Retrying...")
                        time.sleep(2)
                        continue

                    failed_frames = 0

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("Stopped by user.")
                    break

                continue

            failed_frames = 0
            base_frame = frame.copy()

            cv2.polylines(base_frame, [person_zone], True, (255, 0, 255), 2)
            cv2.putText(
                base_frame,
                "PERSON BLOCK ZONE",
                tuple(person_zone[0][0]),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 255),
                2,
            )

            person_present, persons = person_in_zone(frame, person_zone, model, conf=0.4)

            for x1, y1, x2, y2, score, in_zone in persons:
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                color = (0, 0, 255) if in_zone else (255, 255, 0)

                cv2.rectangle(base_frame, (x1, y1), (x2, y2), color, 2)
                cv2.circle(base_frame, (cx, cy), 4, color, -1)
                cv2.putText(
                    base_frame,
                    f"person {score:.2f}",
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    color,
                    2,
                )

            if person_present:
                cv2.putText(
                    base_frame,
                    "PERSON DETECTED IN ZONE - SHELF MONITORING PAUSED",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                )

                for roi_obj in selected_rois:
                    cv2.polylines(base_frame, [roi_obj.points], True, (128, 128, 128), 2)

                final_frame = prepare_display_frame(base_frame)
                video_writer.write(final_frame)
                cv2.imshow(LIVE_WIN, final_frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    print("Stopped by user.")
                    break

                continue

            processed_frame, alerts = monitor.process_frame(frame)
            cv2.polylines(processed_frame, [person_zone], True, (255, 0, 255), 2)

            for x1, y1, x2, y2, score, in_zone in persons:
                color = (0, 0, 255) if in_zone else (255, 255, 0)
                cv2.rectangle(processed_frame, (x1, y1), (x2, y2), color, 2)

            if alerts:
                y0 = 30
                for i, (roi_key, state) in enumerate(alerts):
                    color = (0, 0, 255) if state == "EMPTY" else (0, 255, 255)
                    text = f"{roi_key}: {state}"

                    cv2.putText(
                        processed_frame,
                        text,
                        (20, y0 + i * 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        color,
                        2,
                    )

                    if monitor.should_alert(roi_key, state):
                        print(f"ALERT -> {roi_key} is {state}")
                        save_alert_snapshot(processed_frame.copy(), f"ALERT: {roi_key} {state}")

            final_frame = prepare_display_frame(processed_frame)
            video_writer.write(final_frame)
            cv2.imshow(LIVE_WIN, final_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                print("Stopped by user.")
                break

    finally:
        video_writer.release()
        cap.release()
        cv2.destroyAllWindows()
        print(f"Evidence video saved: {video_path}")


if __name__ == "__main__":
    main()