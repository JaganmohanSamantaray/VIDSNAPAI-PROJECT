
import os
import time
import subprocess

from text_to_audio import text_to_speech_file


UPLOAD_FOLDER = "user_uploads"
DONE_FILE = "done.txt"


def text_to_audio(folder):
    desc_path = os.path.join(UPLOAD_FOLDER, folder, "desc.txt")

    if not os.path.isfile(desc_path):
        raise FileNotFoundError(f"Missing description: {desc_path}")

    with open(desc_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        raise ValueError(f"Description is empty: {desc_path}")

    text_to_speech_file(text, folder)


def create_reel(folder):
    folder_path = os.path.join(UPLOAD_FOLDER, folder)
    output_path = os.path.join("static", "reels", f"{folder}.mp4")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    command = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", os.path.join(folder_path, "input.txt"),
        "-i", os.path.join(folder_path, "audio.mp3"),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
               "pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-shortest",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        output_path
    ]

    subprocess.run(command, check=True)
    print("Reel created:", output_path)


def process_once():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join("static", "reels"), exist_ok=True)

    if os.path.exists(DONE_FILE):
        with open(DONE_FILE, "r", encoding="utf-8") as f:
            done_folders = {line.strip() for line in f if line.strip()}
    else:
        done_folders = set()

    for folder in os.listdir(UPLOAD_FOLDER):
        folder_path = os.path.join(UPLOAD_FOLDER, folder)

        if not os.path.isdir(folder_path):
            continue

        if folder in done_folders:
            continue

        desc_path = os.path.join(folder_path, "desc.txt")
        input_path = os.path.join(folder_path, "input.txt")

        if not os.path.isfile(desc_path) or not os.path.isfile(input_path):
            continue

        try:
            print("Processing:", folder)
            text_to_audio(folder)
            create_reel(folder)

            with open(DONE_FILE, "a", encoding="utf-8") as f:
                f.write(folder + "\n")

        except Exception as e:
            print(f"Failed to process {folder}: {e}")


if __name__ == "__main__":
    while True:
        process_once()
        time.sleep(4)
