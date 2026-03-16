from moviepy import ColorClip, TextClip, AudioFileClip, CompositeVideoClip
import uuid

def render_video(text, audio):
    duration = 45

    clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)

    txt = (
        TextClip(
            text=text[:200],
            font_size=60,
            color="white",
            size=(900, 1600),
            method="caption",
        )
        .with_position("center")
        .with_duration(duration)
    )

    audio_clip = AudioFileClip(audio)

    video = CompositeVideoClip([clip, txt]).with_audio(audio_clip)

    path = f"/tmp/{uuid.uuid4()}.mp4"
    video.write_videofile(path, fps=30, codec="libx264", audio_codec="aac")

    return path
