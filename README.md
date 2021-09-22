# Pybiosis
This project allows users to run python functions from existing devices and services like Stream Deck and Google Assistant. This is done through the use of python decorators that register user functions to those devices after a compiling stage. The compiling stage generates the data files used by Stream Deck while the program Push2Run is used to compile voice commands for Google Assistant. Python wrappers for useful Windows applications like ControlMyMonitor, VirtualDesktop are also included, in the applications folder.

## Installation
1. Install [Push2Run](https://www.push2run.com/) (for voice commands) (tested with dropbox method and the key phrase "on pc", since it is short).
2. Install Pybiosis through pip with `pip install pybiosis`.
3. Create a directory to hold your custom functions and set the Environment Variable `PYBIOSIS_USER_PATH` either using the Windows gui or with the command `setx PYBIOSIS_USER_PATH "your path here"`. You may need to restart your terminal.
4. Add a file called driver.py in that directory that contains this code:

```python
from pybiosis.loader import load_user_modules
from pybiosis.compiler import DeckCompiler, GoogleCompiler

def main():	
    load_user_modules()
    DeckCompiler().compile()
    GoogleCompiler().compile()
```
5. Create a new file in that directory (eg: `my_first_commands.py`) and consider the example below.
6. Run the command `python -m pybiosis` to compile your functions in the command prompt with administrator privileges. Repeat this any time you add new functions.
7. If you use multiple StreamDeck profiles, you can set the Environment Variable `PYBIOSIS_PROFILE_ID` to the desired identifier (without `.sdProfile`). The identifiers can be found in `AppData\Roaming\Elgato\StreamDeck\ProfilesV2`.

## Example
A user wishes to launch a game with a google voice command and/or a StreamDeck button:

```python
from pybiosis.compiler import general, google, deck, multi_phrase

@general(title='Spire', description="Launch Slay the Spire.")
@google(voice=multi_phrase(['open', 'play', 'place'], ['spire', 'fire', 'buyer']))
@deck(location="Games/3,1", image='spire.jpg')
def spire():
    path_to_game = R"C:\Users\...\Games\Slay the Spire.url"
    os.system(Rf'cmd.exe /C START "" "{path_to_game}"')
```
The `multi_phrase` function allows multiple words to trigger the function, since the voice recognition may not hear perfectly. Now the user can execture this function on their computer with a Google voice command and with a Stream Deck button. The user would say something like "Hey Google, on pc, play spire" and the game would be launched on their computer. Their Stream Deck would now have a button in the 4th (0 indexing) column and 2nd row in the Games folder that would also launch the game. Finally, an icon (like `spire.jpg`) can be specified by adding images to a folder called `Icons` located in the `PYBIOSIS_USER_PATH` directory.


## Limitations
1. Currently only tested on Windows, at least some application functionality is windows only.
2. Stream Deck folders must be manually created.
3. If you get a password prompt from Push2Run, simply recompile.

## Questions?
Email me at nawar@palfore.com.
