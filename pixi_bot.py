import tkinter as tk
from tkinter import scrolledtext
from sentence_transformers import SentenceTransformer, util
import numpy as np
import torch
from gtts import gTTS
import os
from googletrans import Translator
import pygame
import threading  # For running animation separately
import time
pygame.mixer.init()

last_audio_path = None
audio_playing = False
animation_running = False
animation_tag = 'audio_button'


last_audio_path = None

# Load and parse the legal Q&A text file into structured data
def load_qna(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    question, answer = '', ''
    for line in lines:
        line = line.strip()
        if line.lower().startswith('user:'):
            question = line[5:].strip()
        elif line.lower().startswith('bot:'):
            answer = line[4:].strip()
            data.append({"question": question, "answer": answer})
    return data

# Load Q&A
qa_data = load_qna("legal_qa.txt")
questions = [entry['question'] for entry in qa_data]
answers = [entry['answer'] for entry in qa_data]

# Load SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')
question_embeddings = model.encode(questions, convert_to_tensor=True)

# Translator and TTS setup
translator = Translator()
def text_to_speech(text, lang='hi'):
    tts = gTTS(text=text, lang=lang)
    audio_path = "pixi_reply.mp3"
    tts.save(audio_path)
    os.system(f"start {audio_path}" if os.name == 'nt' else f"mpg123 {audio_path}")

# Get the most relevant answer using semantic similarity
def get_pixi_response(user_input):
    user_embedding = model.encode(user_input, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(user_embedding, question_embeddings)
    idx = torch.argmax(similarities).item()
    if similarities[0][idx] < 0.4:
        return "I'm sorry, I couldn't find an answer to that question. Please try rephrasing."
    return answers[idx]

# GUI Logic
current_lang = 'en'
def send_message(event=None):
    global last_audio_path
    user_input = entry.get().strip()
    if not user_input:
        return
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, f"\n👤 You: {user_input}", 'user')

    response = get_pixi_response(user_input)
    display_response = response
    
    last_audio_path = None
    
    if current_lang != 'en':
        translation = translator.translate(response, dest=current_lang)
        display_response = translation.text
        
        tts = gTTS(text=display_response, lang=current_lang)
        filename = f"pixi_reply_{int(time.time()*1000)}.mp3"
        tts.save(filename)
        last_audio_path = filename


    chat_display.insert(tk.END, f"\n⚖️ Pixi: {display_response} ", 'bot')
    
    if last_audio_path:
        chat_display.insert(tk.END, " 🔊", 'audio_button')
        chat_display.tag_bind('audio_button', '<Button-1>', play_audio)
        chat_display.tag_config('audio_button', foreground="blue", underline=True, font=("Helvetica", 12, "bold"))
        chat_display.insert(tk.END, "\n")
    else:
        chat_display.insert(tk.END, "\n")

    chat_display.config(state=tk.DISABLED)
    chat_display.see(tk.END)
    entry.delete(0, tk.END)

# Change language
def set_language(lang):
    global current_lang
    current_lang = lang
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, f"\n🌐 Language set to: {lang.upper()}\n")
    chat_display.config(state=tk.DISABLED)

# Flags to manage audio state
audio_paused = False
audio_stopped = False

def play_audio(event=None):
    global last_audio_path, audio_playing, animation_running, audio_paused, audio_stopped

    if not last_audio_path or not os.path.exists(last_audio_path):
        return

    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    pygame.mixer.music.load(last_audio_path)
    pygame.mixer.music.play()
    audio_playing = True
    audio_paused = False
    audio_stopped = False

    # Start animation thread if not already running
    if not animation_running:
        threading.Thread(target=animate_audio_icon, daemon=True).start()

    # Monitor playback to stop animation when audio ends
    def monitor_music():
        global audio_playing, animation_running
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        audio_playing = False
        animation_running = False
        chat_display.tag_config(animation_tag, foreground="blue")
    
    threading.Thread(target=monitor_music, daemon=True).start()


def pause_audio():
    global audio_paused
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        audio_paused = True


def resume_audio():
    global audio_paused, audio_stopped
    if audio_paused:
        pygame.mixer.music.unpause()
        audio_paused = False
    else:
        print("Cannot resume, audio was stopped. Please play again.")



def stop_audio():
    global audio_playing, animation_running, audio_paused, audio_stopped
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    audio_playing = False
    audio_paused = False
    audio_stopped = True
    animation_running = False
    chat_display.tag_config(animation_tag, foreground="blue")


def animate_audio_icon():
    global animation_running
    animation_running = True
    colors = ["blue", "darkblue", "dodgerblue"]
    i = 0
    while animation_running:
        chat_display.tag_config(animation_tag, foreground=colors[i])
        chat_display.update_idletasks()
        i = (i + 1) % len(colors)
        time.sleep(0.5)





# GUI Setup
root = tk.Tk()
root.title("⚖️ Pixi - Legal Help Chatbot")
root.geometry("700x700")
root.configure(bg="#ecf0f1")

# Title
title_label = tk.Label(root, text="⚖️ Pixi - Legal Help for Everyone", font=("Helvetica", 18, "bold"), bg="#34495e", fg="white", pady=10)
title_label.pack(fill=tk.X)

# Chat Window
chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Helvetica", 12), bg="white", height=25)
chat_display.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)
chat_display.tag_config('user', foreground="#2c3e50", font=("Helvetica", 12, "bold"))
chat_display.tag_config('bot', foreground="#4CAF50", font=("Helvetica", 12))
chat_display.config(state=tk.DISABLED)

# Input
entry_frame = tk.Frame(root, bg="#ecf0f1")
entry_frame.pack(fill=tk.X, padx=15, pady=10)

entry = tk.Entry(entry_frame, font=("Helvetica", 13), width=50)
entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
entry.bind("<Return>", send_message)

send_button = tk.Button(entry_frame, text="Send", command=send_message, bg="#2ecc71", fg="white", font=("Helvetica", 12), relief=tk.FLAT, padx=10, pady=4)
send_button.pack(side=tk.RIGHT)

# Language Buttons
lang_frame = tk.Frame(root, bg="#ecf0f1")
lang_frame.pack(pady=5)
tk.Button(lang_frame, text="English", command=lambda: set_language('en')).pack(side=tk.LEFT, padx=5)
tk.Button(lang_frame, text="Hindi", command=lambda: set_language('hi')).pack(side=tk.LEFT, padx=5)
tk.Button(lang_frame, text="Kannada", command=lambda: set_language('kn')).pack(side=tk.LEFT, padx=5)

control_frame = tk.Frame(root, bg="#ecf0f1")
control_frame.pack(pady=5)

pause_btn = tk.Button(control_frame, text="Pause Audio", command=pause_audio, bg="#f39c12", fg="white", font=("Helvetica", 12), relief=tk.FLAT, padx=10, pady=4)
pause_btn.pack(side=tk.LEFT, padx=5)

resume_btn = tk.Button(control_frame, text="Resume Audio", command=resume_audio, bg="#27ae60", fg="white", font=("Helvetica", 12), relief=tk.FLAT, padx=10, pady=4)
resume_btn.pack(side=tk.LEFT, padx=5)



stop_btn = tk.Button(control_frame, text="Stop Audio", command=stop_audio, bg="#e74c3c", fg="white", font=("Helvetica", 12), relief=tk.FLAT, padx=10, pady=4)
stop_btn.pack(side=tk.LEFT, padx=5)


# Run the bot
entry.focus()
root.mainloop()
