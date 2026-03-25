import boto3


class SpeechService:
    def __init__(self, storage_service):
        self.polly = boto3.client("polly")
        self.storage_service = storage_service

    def synthesize_and_upload(self, text, output_file_name, voice_id="Joanna"):
        response = self.polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=voice_id,
            Engine="neural",
        )

        audio_stream = response["AudioStream"].read()
        return self.storage_service.upload_file(
            audio_stream,
            output_file_name,
            content_type="audio/mpeg",
        )
