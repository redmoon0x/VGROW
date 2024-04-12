from flask import Flask, render_template, request, send_file
from PIL import Image
import os
from urllib.parse import quote

app = Flask(__name__)

def process_image(file, cropped_file=None):
    if cropped_file:
        # If a cropped image file is provided, use it for processing
        uploaded_image = Image.open(cropped_file)
    else:
        # If no cropped image file is provided, use the original uploaded image
        uploaded_image = Image.open(file)

    # Correct the image orientation
    uploaded_image = correct_image_orientation(uploaded_image)

    # Convert the image to RGBA mode
    uploaded_image = uploaded_image.convert("RGBA")

    # Open the frame image
    frame = Image.open("frame.png").convert("RGBA")

    # Specify the target width and height
    target_width = 1000
    target_height = 826

    # Resize the uploaded image to fit the specified dimensions with Lanczos anti-aliasing
    uploaded_image = uploaded_image.resize((target_width, target_height), Image.LANCZOS)

    # Calculate the vertical offset for centering
    vertical_offset = 174

    # Create a new blank image with the same dimensions as the frame
    background = Image.new("RGBA", (target_width, target_height + vertical_offset), (255, 255, 255, 0))

    # Paste the uploaded image onto the background with the specified vertical offset
    background.paste(uploaded_image, (0, vertical_offset))

    # Paste the frame onto the uploaded image
    background.paste(frame, (0, 0), frame)

    # Save the combined image
    background.save("static/output.png")

    # Return the path to the combined image
    return "output.png"

def correct_image_orientation(image):
    try:
        # Check the EXIF data for the image orientation
        image_exif = image._getexif()
        if image_exif:
            orientation = image_exif.get(0x0112)
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # If there's an error accessing the EXIF data, do nothing
        pass
    return image

@app.route("/", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        if request.files:
            # Check if the request contains the cropped image data
            if "cropped_image" in request.files:
                cropped_image = request.files["cropped_image"]
                if cropped_image.filename != "":
                    # Save the cropped image
                    cropped_image_path = "static/cropped_image.png"
                    cropped_image.save(cropped_image_path)
                    # Process the cropped image and get the path to the combined image
                    processed_image = process_image(cropped_file=cropped_image_path)
                    return render_template("result.html", image=processed_image)
            # If the request does not contain cropped image data, fallback to handling the original uploaded image
            elif "image" in request.files:
                image = request.files["image"]
                if image.filename != "":
                    # Save the uploaded image
                    image_path = "static/original_image.png"
                    image.save(image_path)
                    # Process the image and get the path to the combined image
                    processed_image = process_image(file=image_path)
                    return render_template("result.html", image=processed_image)
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)