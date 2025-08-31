import streamlit as st
from openai import OpenAI

import os
import io
import base64
from PIL import Image

api_key = "yourServiceKey"
client = OpenAI(api_key=api_key)

def describe(text):
  response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
      {
        "role":"user",
        "content":[
          {"teype":"text", "text":"이 이미지에 대해서 아주 자세히 묘사해줘"},
          {
            "type":"image_url",
            "image_url": {
              "url":text,
            },
          },
        ],
      }
    ],
    max_tokens=1024,
  )
  return response.choices[0].message.content

def TTS(response):
  with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="onyx",
    input=response
  ) as response:
    filename="output.mp3"
    response.stream_to_file(filename)

  with open(filename, "rb") as f:
    data = f.read()
    b64 = base64.b64encode(data).decode()
    md = f"""
        <audio autoplay="True">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)

  os.remove(filename)

def describe(text):
  response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
      {
        "role":"user",
        "content": [
          {"type":"text", "text":"이 이미지에 대해서 아주 자세히 묘사해줘"},
          {
            "type":"image_url",
            "image_url": {
              "url":text,
            },
          },
        ],
      }
    ],
    max_tokens=1024,
  )
  return response.choices[0].message.content

def main():
  st.image('ai.PNG', width=200)
  st.title('이미지를 해설해드립니다.')

  img_file_buffer = st.file_uploader('Upload a PNG image', type='png')

  if img_file_buffer is not None:
    image = Image.open(img_file_buffer)

    # 업로드한 이미지를 화면에 출력
    st.image(image, caption='Uploaded Image.', use_container_width=True)

    # 이미지 => 바이트 버퍼로 변환
    buffered = io.BytesIO()
    image.save(buffered, format='PNG')
    
    # 바이트 버퍼 => Base64 인코딩 바이트 문자열로 변환
    img_base64 = base64.b64encode(buffered.getvalue())
    
    # Base64 인코딩 바이트 문자열 => UTF-8 문자열로 디코딩
    img_base64_str = img_base64.decode('utf-8')

    # GPT-4에서 입력받을 수 있는 형태로 변환
    image = f"data:image/jpeg;base64,{img_base64_str}"

    # GPT4V가 이미지에 대한 설명을 반환하고 이를 st.info()로 출력
    text= describe(image)
    st.info(text)

    # 이미지에 대한 설명을 음성으로 변환
    TTS(text)

if __name__ == "__main__":
  main()