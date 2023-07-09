
# Pybiosis
This project allows users to run python functions from existing devices and services like Stream Deck and Google Assistant. This is done through the use of python decorators that register user functions to those devices after a compiling stage. 

## Examples
Here is a showcase of a function that is hooked up to several devices/services.

```python
from pybiosis import *

@Device(title='Spire', description="Launch Slay the Spire.")
@Google(voice=multi_phrase(['open', 'play', 'place'], ['spire', 'fire', 'buyer']))
@Deck(location="Games/3,1", image='spire.jpg')
@Scheduler(trigger="Daily", start="today-5:01pm")
def spire():
    path_to_game = R"C:\Users\...\Games\Slay the Spire.url"
    os.system(Rf'cmd.exe /C START "" "{path_to_game}"')
```
The `Device` decorator is a generic decorator that simply provides some metadata to the function. 
The `Google` decorator let's a user talk to their google assistant to trigger a `python` function to run. The `multi_phrase` function gives room for more freedom and possible mishearing (since the voice recognition may not hear perfectly). To actually call this function, the user would say "Hey Google, on pc, play spire" (or some variation) and the game would be launched on their computer.
The `StreamDeck` decorator places a button in the 4th column and 2nd row in the Games folder (0-indexing)  that also launches the game. An icon (like `spire.jpg`) can be specified by adding images to a specified folder.
The `Scheduler` decorator schedules the game to run on a provided schedule, in this case every day right after 5pm.

### General:
Each device or service has an associated compiler that provides a decorator. There are some built-in to `Pybiosis` but you can also define your own. These decorators are used on a function to associated them with a device/service. Here are some basic templates for example functions. See [Compilers](#compilers) below for more details.

1. Create a parameter-less function. 
    ```python
    def func():
        pass  # Do anything
    ```

2. Provide a title and description to the function.
    ```python
    @Device(title='My First Function', description="This is a demonstration.")
    def func():
        pass
    ```

3. Attach it to a service, like the Google Assistant (see  [Compiler Examples](#compilers) below).
    ```python
    @Device(title='My First Function', description="This can be called from the Assistant.")
    @Assistant(phrase="first")
    def func():
        pass
    ```

4. Note that the `Device` is optional (when included though, it should always be the highest decorator).
    ```python
    @Assistant(phrase="first")
    def func():
        pass
    ```

5. Control what happens to the command window that opens when a function is triggered.
    ```python
    @Device(show=True, pause=True)
    @StreamDeck(phrase="settings")
    def func():
        pass
    ```
    
5. Easily apply a list of decorators (this may be useful for a list comprehension).
    ```python
    @apply_list([Scheduler(trigger='daily', start="2022/05/14-08:30"),
                 Scheduler(trigger='daily', start="2022/05/14-05:00")])
    def func():
        pass
    ```
    
### Class syntax vs Function syntax
The number of function can accumulate quickly, so to improve organization the `class syntax` uses nested `classes` to mimic a folder structure, as syntatic sugar. 
The `register` decorator brings all functions to the top level (i.e. it ignores all classes). Note that this means if you are calling a nested function, you do not need to prefix it with the class name i.e. not `Monitor.MonitorBrightness.brightness_up()`, just `brightness_up()`. This also means that duplicate names will override the function, so naming must be unique at the function level (per module). By contrast, constants _do_ need the class name i.e. `Monitor.MAX_BRIGHTNESS` not just `MAX_BRIGHTNESS`.
```python
@register(globals())
class Monitor:
    class Brightness:
        @StreamDeck(location='Monitors/Display\nSettings/1,0')
        def brightness_up():  # Note that "up()" isn't used since it would clash with Contrast.
            pass

        @StreamDeck(location='Monitors/Display\nSettings/2,0')
        def brightness_down():
            pass

    class Contrast:
        @StreamDeck(location='Monitors/Display\nSettings/3,0')
        def contrast_up():
            pass

        @StreamDeck(location='Monitors/Display\nSettings/4,0')
        def contrast_down():
            pass
```


### Compilers
Pybiosis comes with some built-in device compilers. You may also define your own if you have a novel device.

#### StreamDeck
Requires a [StreamDeck](https://www.elgato.com/en/stream-deck).

1. Specify a location for the button to be placed. The value of `x` and `y` are the 0-indexed column and row, respectively. Note that the folder must first be created _manually_ through the application GUI.
    ```
    @StreamDeck(location='Folder/On/Stream/Deck/x,y)
    def func()
        pass
    ```
2. You can also specify multiple locations.
    ```
    @StreamDeck(location=['Path1/x,y', 'Path2/x,y'])
    def func()
        pass
    ```
2. And an image. Images should be placed  in `PYBIOSIS_USER_PATH/Images`. See [Installation](#installation) for more details.
    ```
    @StreamDeck(location='Path/x,y', image="my_image.png")
    def func()
        pass
    ```
If you use multiple StreamDeck profiles, you can set the Environment Variable `PYBIOSIS_PROFILE_ID` to the desired identifier (without `.sdProfile`). The identifiers can be found in `AppData\Roaming\Elgato\StreamDeck\ProfilesV2`.
#### Google Assistant
Requires a [Push2Run](https://www.push2run.com/) installation and access to a Google Assistant device.
1. The simpliest way to register a command is with a single word.
    ```python
    @Assistant(phrase="Hello")
    def greet():
        pass
    ```
2. Sometimes a single word can be mis-heard or you may want more freedom, a list can provide synonyms.
    ```python
    @Assistant(phrase=["loop", "lamp", "new", "blue"])
    def loop():
        pass
    ```
3. To register a phrase, use the `multi_phrase` function. Note that each word is wrapped in a list.
    ```python
    @Assistant(phrase=multi_phrase(['slay'], ['the'], ['spire']))
    def slay_the_spire():
        pass
    ```
4. To register a phrase with synonyms, provide them in the list.
    ```python
    @Assistant(phrase=multi_phrase(['mode', 'mod'], ['the'], ['spire', 'fire', 'buyer']))
    def mod_the_spire():
        os.chdir(R"C:\Program Files (x86)\Steam\steamapps\common\SlayTheSpire")
        os.system(R'jre\bin\java.exe -jar mts-launcher.jar')
    ```
Push2Run has been tested with the Dropbox method and the key phrase "on pc", since it is short.
#### Scheduler
Requires a Windows OS. No installation is required since it uses the Windows Task Scheduler. See [`schtasks.exe`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create) for more details on usage.

1. Schedule a function to run now (in the next minute).
    ```python
    @Scheduler(trigger='once', start='now')
    def hourly_beep():
        import winsound  # imports can be local
        winsound.Beep(1000, 200)
    ```

2. Schedule a function to run daily at 8am.
    ```python
    @Scheduler(trigger='daily', start=f"2022/05/14-08:00")
    def hourly_beep():
        import winsound  # imports can be local
        winsound.Beep(1000, 200)
    ```

3. Schedule a function to run multiple times.
    ```python
    @Scheduler(trigger='daily', start=f"2022/05/14-05:00")
    @Scheduler(trigger='daily', start=f"2022/05/14-08:00")
    def hourly_beep():
        import winsound
        winsound.Beep(1000, 200)
    ```
4. Schedule a function to run at multiple times within an interval using the `apply_list` decorator.
    ```python
    @apply_list([Scheduler(trigger='daily', start=f"2022/05/14-1{i}:00") for i in range(0, 7+1)])
    def hourly_beep():
        import winsound
        winsound.Beep(1000, 200)
    ```
#### Creating your own
You can also create your own compiler just by inheriting from `Device` (or a subclass).

## Installation
1. Install `Pybiosis` through pip with `pip install pybiosis`.
2. Create a directory to hold your custom functions and set the Environment Variable `PYBIOSIS_USER_PATH` either using the Windows gui or with the command `setx PYBIOSIS_USER_PATH "your/path/here"`. You may need to restart your terminal.
3. Add a file called `driver.py` to that directory and have it contain this code:
    ```python
    import pybiosis
    import winsound
    
    # Add whatever decorators you want here.
    def beep():
        winsound.Beep(1000, 200)
        
    def main(): 
        pybiosis.load()
        pybiosis.Device.compile_all()
    ```
    You can also create other new python files in  `PYBIOSIS_USER_PATH` for modularity.
5. Run the command `python -m pybiosis` to compile your functions in the command prompt with administrator privileges. Repeat this any time you add new functions. 

## Limitations
0. *All compilers must be valid, even if they don't get used. This should change in future.
1. *Currently only tested on Windows, at least some application functionality is windows only. Again, the whole application is restricted to windows even though only one compiler requires it.
2. Stream Deck folders must be manually created.
3. If you get a password prompt from Push2Run, simply recompile.

## Questions?
Email me at nawar@palfore.com.
