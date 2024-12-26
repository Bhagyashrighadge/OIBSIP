import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import sounddevice as sd
from scipy.io.wavfile import write

# Initialize Text-to-Speech Engine
tts_engine = pyttsx3.init()

def speak(message):
    """
    Convert a given message into spoken words.
    """
    global tts_engine
    try:
        tts_engine.stop()  # Stop any ongoing speech
        tts_engine.say(message)
        tts_engine.runAndWait()
    except RuntimeError as e:
        print(f"TTS Error: {e}. Reinitializing TTS engine...")
        tts_engine = pyttsx3.init()  # Reinitialize TTS engine
        tts_engine.say(message)
        tts_engine.runAndWait()

def generate_greeting():
    """
    Generate a greeting based on the current time of day.
    """
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        return "Good morning!"
    elif 12 <= current_hour < 18:
        return "Good afternoon!"
    else:
        return "Good evening!"

def record_audio(duration=4):
    """
    Record audio from the microphone for a specified duration.
    """
    try:
        print("Listening...")
        sample_rate = 44100
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()  # Wait for the recording to complete
        audio_file = "temp_audio.wav"
        write(audio_file, sample_rate, audio_data)
        return audio_file
    except Exception as error:
        print(f"Error during audio recording: {error}")
        return None

def transcribe_audio():
    """
    Transcribe audio to text using Google Speech Recognition.
    """
    recognizer = sr.Recognizer()
    audio_file = record_audio()

    if not audio_file:
        return ""

    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            recognized_text = recognizer.recognize_google(audio_data)
            print(f"Recognized: {recognized_text}")
            return recognized_text.lower()
    except sr.UnknownValueError:
        speak("Sorry, I couldn't understand that. Please try again.")
        return ""
    except sr.RequestError:
        speak("The speech recognition service is unavailable.")
        return ""
    except Exception as error:
        print(f"Unexpected error during transcription: {error}")
        return ""

def announce_time():
    """
    Announce the current time.
    """
    now = datetime.datetime.now()
    formatted_time = now.strftime("%I:%M %p")
    speak(f"The time is {formatted_time}")

def announce_date():
    """
    Announce the current date.
    """
    today = datetime.datetime.now()
    formatted_date = today.strftime("%A, %B %d, %Y")
    speak(f"Today's date is {formatted_date}")

def search_the_web(query):
    """
    Perform a web search using the given query.
    """
    if query:
        url = f"https://www.google.com/search?q={query}"
        speak(f"Searching for {query}")
        webbrowser.open(url)
    else:
        speak("I need a search query.")

def launch_application(app_name):
    """
    Launch a common application based on the name provided.
    """
    try:
        if "notepad" in app_name:
            os.system("notepad")
        elif "calculator" in app_name:
            os.system("calc")
        else:
            speak(f"Sorry, I cannot open {app_name} at the moment.")
    except Exception as error:
        print(f"Error launching application: {error}")
        speak(f"Failed to open {app_name}.")

def assistant_main():
    """
    Main loop for the virtual assistant.
    """
    speak(f"{generate_greeting()} I am your assistant. How can I help you?")
    try:
        while True:
            user_command = transcribe_audio()
            if not user_command:
                continue

            if "hello" in user_command:
                speak("Hello! How may I assist you?")
            elif "time" in user_command:
                announce_time()
            elif "date" in user_command:
                announce_date()
            elif "search" in user_command:
                speak("What would you like to search for?")
                search_query = transcribe_audio()
                search_the_web(search_query)
            elif "open" in user_command:
                speak("Which application would you like me to open?")
                app_name = transcribe_audio()
                launch_application(app_name)
            elif "stop" in user_command or "exit" in user_command or "quit" in user_command:
                speak("Goodbye! Have a great day!")
                break
            else:
                speak("I didn't quite understand that. Can you repeat it?")
    except KeyboardInterrupt:
        speak("Goodbye! See you soon.")
        tts_engine.stop()
        print("Assistant terminated.")

if __name__ == "__main__":
    assistant_main()
