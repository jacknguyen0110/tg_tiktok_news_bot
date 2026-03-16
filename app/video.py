from moviepy.editor import *
import uuid

def render_video(text, audio):

    clip = ColorClip(size=(1080,1920), color=(0,0,0), duration=45)

    txt = TextClip(
        text[:200],
        fontsize=60,
        color="white",
        size=(900,1600),
        method="caption"
    ).set_position("center").set_duration(45)

    audio_clip = AudioFileClip(audio)

    video = CompositeVideoClip([clip,txt])

    video = video.set_audio(audio_clip)

    path = f"/tmp/{uuid.uuid4()}.mp4"

    video.write_videofile(path, fps=30)

    return path