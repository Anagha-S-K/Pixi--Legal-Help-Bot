⚖️ Pixi – Legal Help Chatbot
Pixi is a multilingual desktop-based AI chatbot designed to provide accessible legal help. It allows users to ask legal questions in natural language and receive relevant responses from a curated Q&A dataset. With language translation, voice output, and a clean GUI, Pixi aims to bridge the gap between legal knowledge and the common user.

Features:
💬 Semantic Question Matching: Uses transformer-based embeddings to find the most relevant legal answer.
🌐 Multilingual Support: Responds in English, Hindi, and Kannada using Google Translate API.
🔊 Text-to-Speech (TTS): Converts responses to speech using gTTS, improving accessibility.
🖥️ User-Friendly GUI: Built using Tkinter with a scrollable chat window.
🎧 Audio Controls: Users can play, pause, resume, or stop audio responses using Pygame.
🗂️ Expandable Q&A Dataset: Easily update the legal knowledge base via legal_qa.txt.

Technologies Used:
-Python 3
-SentenceTransformers (all-MiniLM-L6-v2) – For semantic similarity.
-PyTorch – Backend for embeddings.
-gTTS (Google Text-to-Speech) – Converts responses to audio.
-Googletrans – For translation support.
-Tkinter – Desktop GUI.
-Pygame – For audio playback.
