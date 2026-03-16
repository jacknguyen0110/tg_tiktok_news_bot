from gtts import gTTS
import uuid

def generate_voice(text):

    filename = f"/tmp/{uuid.uuid4()}.mp3"

    tts = gTTS(text=text, lang="vi")

    tts.save(filename)

    return filename