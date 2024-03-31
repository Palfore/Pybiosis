""" The idea behind this script is to replace the Google Assistant decorator since it is deprecated.

This script should always be on, and listens indefinitely for the keyword "cheesecake/hello/anything".
Once this is recognized, the script will beep twice, indicating that the script heard you and you can hear it.
Then it will wait 5 seconds for a command, which will be dispatched according to the decorators.

I envision "keyword stream deck monitors settings duplicate" (or maybe "4 3" for the button coordinate).
Also, the @Voice decorator would register commands.



Always listen for "keyword".
If detected:
    beep
    cmd = listen(t=5)
    if cmd:
        cmd()
        yes = ask("anything else?")
        if yes:
            // repeat
        else:
            say("Very good.")




"""
# pip install setuptools
# SpeechRecognition
# PyAudio
# pip install pocketsphinx
# pip install pyttsx3


from colorama import Fore, Style
import speech_recognition as sr
import datetime
import inspect
import sys


import pyttsx3 as pyttsx
import time
# time.sleep(6)
engine = pyttsx.init()


class _TTS:

    engine = None
    rate = None
    def __init__(self):
        self.engine = pyttsx.init()


    def start(self,text_):
        self.engine.say(text_)
        self.engine.runAndWait()



def cheesecake_action():
    import winsound
    winsound.Beep(1000, 100)
    winsound.Beep(1000, 100)

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()

            tts = _TTS()
            tts.start("Running: " + str(command))  # gets stuck here
            tts.start("A second command")
            del(tts)
            # engine = pyttsx.init()
            # engine.say("Running: " + str(command))
            # engine.runAndWait()  # This hangs infinitely...  https://stackoverflow.com/questions/56032027/pyttsx3-runandwait-method-gets-stuck
    finally:
        winsound.Beep(1000, 100)
        winsound.Beep(1000, 100)
        winsound.Beep(1000, 100)
        winsound.Beep(1000, 100)



def callback(recognizer, audio):
    try:
        # Recognize speech
        command = recognizer.recognize_google(audio).lower()
        print("You said:", command)
        # Check if the recognized speech contains the keyword "cheesecake"
        if "hello" in command:
            cheesecake_action()
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))


class VoiceCommandInterface:
    def __init__(self, commands):
        self.recognizer = sr.Recognizer()
        self.commands = commands
    
    def listen_command_background(self):
        engine.say("Ready for your command. Say hello.")
        engine.runAndWait()

        with sr.Microphone() as source:
        # source = sr.Microphone()
            print(">>> Listening...", end=' '); sys.stdout.flush()
            self.recognizer.adjust_for_ambient_noise(source)
        stop_listening = self.recognizer.listen_in_background(source, callback, phrase_time_limit=2)
        while True:
            pass

    # def listen_command(self):
    #     # print(sr.Microphone.list_microphone_names().index("Headphones (WH-1000XM3 Stereo)"))
    #     # with sr.Microphone(device_index=2) as source:
    #     with sr.Microphone() as source:
    #         print(">>> Listening...", end=' '); sys.stdout.flush()
    #         self.recognizer.adjust_for_ambient_noise(source)
    #         stop_listening = self.recognizer.listen_in_background(source, callback)
    #         # audio = self.recognizer.listen(source, timeout=2)
    #         # audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
        
        
    #     try:
    #         print("| Processing..."); sys.stdout.flush()
    #         command = self.recognizer.recognize_google(audio).lower()
    #         # command = self.recognizer.recognize_sphinx(audio, keyword_entries=[(cmd, 0.1) for cmd in self.commands]).lower()
    #         print(f"{Fore.GREEN}You said:{Style.RESET_ALL} {command}")
    #         return command
    #     except sr.UnknownValueError:
    #         print(f"{Fore.RED}Could not understand audio{Style.RESET_ALL}")
    #         return ""
    #     except sr.RequestError as e:
    #         print(f"{Fore.RED}Could not request results; {e}{Style.RESET_ALL}")
    #         return ""

    def evaluate_command(self, command):
        action = self.commands.get(command)
        if action:
            engine.say(f'Very good Sir, performing action "{command}".');
            engine.runAndWait()
            action()
        else:
            print(f"{Fore.RED}Command not recognized{Style.RESET_ALL}")
        return True

    def run(self):
        print(f"{Fore.CYAN}Welcome to the Voice Command Interface!{Style.RESET_ALL}")
        print("Instructions:")
        for cmd, fn in self.commands.items():
            print(f"  - {fn.__doc__.replace('COMMAND_NAME', f"{Fore.YELLOW}{cmd}{Style.RESET_ALL}")}")
        print("")

        self.listen_command_background()


        # running = True
        # while running:
        #     command = self.listen_command()
        #     running = self.evaluate_command(command)


class Commands:
    def __init__(self, command_actions=None):
        """ If command_actions are supplied they are used, otherwise the class functions are used. """
        if command_actions is None:
            class_methods = inspect.getmembers(self, predicate=inspect.ismethod)
            self.actions = {cmd: fn for cmd, fn in class_methods if not cmd.startswith("__")}
        else:
            self.actions = command_actions

    def hello(self):
        """ Say 'COMMAND_NAME' for a greeting. """
        print(f"\t- {Fore.BLUE}Hello! How can I assist you?{Style.RESET_ALL}")
        engine.say(f"Hello and good day. How can I help you?")
        engine.runAndWait()

    def time(self):
        """ Say 'COMMAND_NAME' to get the current time. """
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        engine.say(f"The current time is {now.strftime("%I:%M %p")}.")
        engine.runAndWait()
        print(f"\t- {Fore.BLUE}Current time is:{Style.RESET_ALL} {current_time}")

    def list(self):
        """ Say 'COMMAND_NAME' to list the possible commands. """
        for cmd, fn in self.actions.items():
            print(f"\t- {Fore.BLUE}{fn.__doc__.replace('COMMAND_NAME', cmd)}{Style.RESET_ALL}")
        engine.say(f"The available commands are: {', '.join(self.actions)}.")
        engine.runAndWait()

    def exit(self):
        """ Say 'COMMAND_NAME' to quit the program. """
        print(f"\t- {Fore.BLUE}Exiting...{Style.RESET_ALL}")
        engine.say(f"Very good Sir, sleeping now, wake me if you need anything.")
        engine.runAndWait()
        return False


if __name__ == "__main__":
    interface = VoiceCommandInterface(Commands().actions)
    interface.run()
