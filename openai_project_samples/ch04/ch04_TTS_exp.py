from openai import OpenAI

client = OpenAI(api_key="yourServiceKey")

speech_file_path = "speech.mp3"

with client.audio.speech.with_streaming_response.create(
  model="tts-1",
  voice="alloy",
  input="오늘은 사람들이 좋아하는 것을 만들기에 좋은 날입니다!"
) as response:
  response.stream_to_file(speech_file_path)