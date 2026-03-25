from chalice import Chalice
from chalicelib import storage_service
from chalicelib import recognition_service
from chalicelib import translation_service
from chalicelib import speech_service

import base64
import json
import os

app = Chalice(app_name="speaking-pictorial")
app.debug = True

# Set your bucket via environment variable for portability.
storage_location = os.environ.get("STORAGE_BUCKET", "my-unique-bucket-20250118-xyz")
storage = storage_service.StorageService(storage_location)
recognizer = recognition_service.RecognitionService(storage)
translator = translation_service.TranslationService()
speaker = speech_service.SpeechService(storage)


@app.route("/health", methods=["GET"])
def health():
    return {"ok": True, "bucket": storage_location}


@app.route("/images", methods=["POST"], cors=True)
def upload_image():
    request_data = json.loads(app.current_request.raw_body)
    file_name = request_data["filename"]
    file_bytes = base64.b64decode(request_data["filebytes"])
    return storage.upload_file(file_bytes, file_name)


@app.route("/images/{image_id}/translate-text", methods=["POST"], cors=True)
def translate_image_text(image_id):
    request_data = json.loads(app.current_request.raw_body)
    from_lang = request_data.get("fromLang", "auto")
    to_lang = request_data.get("toLang", "en")

    min_confidence = 80.0
    text_lines = recognizer.detect_text(image_id)

    translated_lines = []
    for line in text_lines:
        if float(line["confidence"]) >= min_confidence:
            translated_line = translator.translate_text(line["text"], from_lang, to_lang)
            translated_lines.append(
                {
                    "text": line["text"],
                    "translation": translated_line,
                    "boundingBox": line["boundingBox"],
                }
            )
    return translated_lines


@app.route("/images/{image_id}/speak-text", methods=["POST"], cors=True)
def speak_image_text(image_id):
    """
    Detect text, translate it, convert to speech with Polly, then save MP3 to S3.
    """
    request_data = json.loads(app.current_request.raw_body)
    from_lang = request_data.get("fromLang", "auto")
    to_lang = request_data.get("toLang", "en")
    voice_id = request_data.get("voiceId", "Joanna")

    min_confidence = 80.0
    text_lines = recognizer.detect_text(image_id)

    translated_texts = []
    for line in text_lines:
        if float(line["confidence"]) >= min_confidence:
            translated = translator.translate_text(line["text"], from_lang, to_lang)
            translated_texts.append(translated["translatedText"])

    if not translated_texts:
        return {"message": "No high-confidence text lines found.", "audioFileUrl": None}

    full_text = ". ".join(translated_texts)
    audio_file_name = f"audio/{image_id.rsplit('.', 1)[0]}-{to_lang}.mp3"
    audio_info = speaker.synthesize_and_upload(full_text, audio_file_name, voice_id)

    return {
        "imageId": image_id,
        "translatedText": full_text,
        "audioFileId": audio_info["fileId"],
        "audioFileUrl": audio_info["fileUrl"],
    }
