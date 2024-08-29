import os
import cv2
import numpy as np
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    jsonify as JsonResponse,
)
from keras.models import load_model
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploaded_images"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg"}

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return redirect(request.url)

    file = request.files["file"]

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        results = detect_face(image_path=filepath)

        if not results:
            return JsonResponse({"error": "No face detected"})

        return JsonResponse({"results": results})

    return JsonResponse({"error": "Invalid file"})


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return f"<img src='/static/{filename}' alt='Processed Image'/>"


def detect_face(*, image_path: str):
    model = load_model("model_file_30epochs.h5")

    faceDetect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    labels_dict = {
        0: "Angry",
        1: "Disgust",
        2: "Fear",
        3: "Happy",
        4: "Neutral",
        5: "Sad",
        6: "Surprise",
    }

    # len(number_of_image), image_height, image_width, channel
    results = []
    frame = cv2.imread(image_path)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.3, 3)
    for x, y, w, h in faces:
        sub_face_img = gray[y : y + h, x : x + w]
        resized = cv2.resize(sub_face_img, (48, 48))
        normalize = resized / 255.0
        reshaped = np.reshape(normalize, (1, 48, 48, 1))
        result = model.predict(reshaped)
        label = np.argmax(result, axis=1)[0]
        print(label)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 2)
        cv2.rectangle(frame, (x, y - 40), (x + w, y), (50, 50, 255), -1)
        cv2.putText(
            frame,
            labels_dict[label],
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )
        results.append(labels_dict[label])

        print(f"Detected face: {labels_dict[label]}")

    # cv2.imshow("Frame", frame)
    # save the image
    cv2.imwrite("processed_faces-small.jpg", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return results


if __name__ == "__main__":

    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    app.run(debug=True, port=5000)
