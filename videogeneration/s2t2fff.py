from flask import Flask, request, jsonify, render_template
import os
import shutil
from moviepy.editor import AudioFileClip, concatenate_videoclips, ImageClip, VideoFileClip
from gtts import gTTS
from PIL import Image

app = Flask(__name__)

def generate_audio_from_text(text, output_file):
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)

def resize_image_keep_aspect(image_path, target_width=640):
    img = Image.open(image_path)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    width_percent = (target_width / float(img.size[0]))
    target_height = int((float(img.size[1]) * float(width_percent)))
    img_resized = img.resize((target_width, target_height), Image.ANTIALIAS)
    img_resized_path = image_path.rsplit(".", 1)[0] + "_resized.jpg"
    img_resized.save(img_resized_path, format='JPEG')
    return img_resized_path

def create_slideshow(audio_file, image_folder, output_file):
    audio_clip = AudioFileClip(audio_file)
    audio_duration = audio_clip.duration
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    image_paths.sort()

    clips = []
    if image_paths:
        duration_per_image = audio_duration / len(image_paths)  # Calculate duration per image
        for image_path in image_paths:
            img_resized_path = resize_image_keep_aspect(image_path)
            clip = ImageClip(img_resized_path).set_duration(duration_per_image)  # Set each clip's duration to match the audio
            clips.append(clip)
    
    if clips:
        video = concatenate_videoclips(clips, method="compose")
        video = video.set_audio(audio_clip)
        video.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24)

@app.route('/')
def index():
    return render_template('plswork.html')

@app.route('/submit-data', methods=['POST'])
def handle_data():
    uploads_dir = 'uploads'
    if os.path.exists(uploads_dir):
        shutil.rmtree(uploads_dir)
    os.makedirs(uploads_dir, exist_ok=True)

    text_parts = [value for key, value in request.form.items() if key.startswith('textPart')]
    video_parts = []

    for i, part in enumerate(text_parts, start=1):
        part_dir = os.path.join(uploads_dir, f'Part{i}')
        os.makedirs(part_dir, exist_ok=True)

        audio_dir = os.path.join(part_dir, 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        images_dir = os.path.join(part_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)

        audio_file_name = f'audio_part_{i}.mp3'
        audio_file_path = os.path.join(audio_dir, audio_file_name)
        generate_audio_from_text(part, audio_file_path)

        if f'imagesPart{i}' in request.files:
            files = request.files.getlist(f'imagesPart{i}')
            for file in files:
                if file.filename:
                    filename = file.filename
                    file_path = os.path.join(images_dir, filename)
                    file.save(file_path)

        output_file = os.path.join(part_dir, f'video_part_{i}.mp4')
        create_slideshow(audio_file_path, images_dir, output_file)
        video_parts.append(output_file)

    # Combine all video parts into one video
    if video_parts:
        combined_clips = [VideoFileClip(vp) for vp in video_parts]
        final_clip = concatenate_videoclips(combined_clips, method="compose")
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'final_video.mp4')
        final_clip.write_videofile(desktop_path, codec="libx264", audio_codec="aac", fps=24)

    return jsonify({"message": "Data, audio, and final combined video processed successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
