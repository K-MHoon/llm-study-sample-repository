# 음성 녹음을 위한 오디오 레코더 패키지 추가
from audiorecorder import audiorecorder

# 스트림릿 패키지 추가
import streamlit as st

# OpenAI 패키지 추가
from openai import OpenAI

#파이썬 기본 패키지
import os
import base64
import numpy as np

# 음성을 텍스트로 변환하는 STT API
def STT(audio, client) :
  # Whisper API가 파일 형태로 음성을 입력받으므로 input.mp3 파일을 저장
  filename = 'input.mp3'
  wav_file = open(filename, "wb")
  wav_file.write(audio.export().read())
  wav_file.close()

  # 음성 파일 읽기
  audio_file = open(filename, "rb")

  try:
    transcript = client.audio.transcriptions.create(
      model="whisper-1",
      file=audio_file,
      response_format="text"
    )

    audio_file.close()
    os.remove(filename)
  except:
    transcript='API Key를 확인해주세요'
  return transcript

def TTS(response, client):
  # TTS를 활용하여 만든 음성을 파일로 저장
  with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="onyx",
    input=response
  ) as response:
    filename = "output.mp3"
    response.stream_to_file(filename)
  
  # 저장한 음성 파일을 자동 재생
  with open(filename, "rb") as f:
    data = f.read()
    b64 = base64.b64encode(data).decode()

    # 스트림릿에서 음성 자동 재생
    md = f"""
      <audio autoplay="True">
      <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
      </audio>
    """

    st.markdown(md, unsafe_allow_html=True,)

  os.remove(filename)  

def ask_gpt(prompt, client):
  response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=prompt
  )
  return response.choices[0].message.content

def main():
  client = OpenAI(api_key='yourServiceKey')

  st.set_page_config(
    page_title='음성 비서 프로그램🔊',
    layout='wide'
  )

  if "check_audio" not in st.session_state:
    st.session_state["check_audio"] = []

  if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role":"system", "content":"You are a thoughtful assistant. Respond to all input in 25 words and answer in korean"}]

  col1, col2 = st.columns(2)

  with col1:
    st.header('AI Assistant 🔊')
    st.image('ai.png', width=200)
    st.markdown('---')

    flag_start = False
    
    audio = audiorecorder('질문', '녹음중...')
    if len(audio) > 0 and not np.array_equal(audio, st.session_state['check_audio']):
      st.audio(audio.export().read())

      question = STT(audio, client)

      st.session_state["messages"] = st.session_state["messages"] + [{"role":"user", "content": question}]
      st.session_state["check_audio"] = audio
      flag_start=True

  with col2:
    st.subheader('대화기록 ⌨')
    if flag_start:

      response = ask_gpt(st.session_state["messages"], client)
      st.session_state["messages"] = st.session_state["messages"] + [{"role":"assistant", "content": response}]

      for message in st.session_state["messages"]:
        if message["role"] != 'system':
          with st.chat_message(message['role']):
            st.markdown(message["content"])
      
      TTS(response, client)

if __name__=='__main__':
  main()