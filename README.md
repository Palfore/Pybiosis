
# Pybiosis

> What could empower you more than a symbiotic relationship with Python?

Pybiosis is an automation software that focuses on making python functions more accessible by providing versatile entry-points to functions.
This project makes heavy use of decorators, which define the entry-points. Currently, there are existing implementations for services like [StreamDeck](#streamdeck), [Google Assistant](#google-assistant), and [Windows Task Scheduler](#scheduler). Pybiosis also provides a CLI, a _GUI_ CLI (using [gooey](https://github.com/chriskiehl/Gooey/tree/master)), and a GUI (using [streamlit](https://github.com/streamlit/streamlit)) to access these functions.

## How It Works
### Example:
Wrap your functions in decorators to add entry points from other devices and services:
```python
from pybiosis import *

@Device(title='Spire', description="Launch Slay the Spire.")
@Google(voice=multi_phrase(['open', 'play', 'place'], ['spire', 'fire', 'buyer']))
@Deck(location="Games/3,1", image='spire.jpg')
@Scheduler(trigger="Daily", start="today-5:01pm")
def spire():
    # Launch the game shortcut using cmd.
    path_to_game = R"C:\Games\Slay the Spire.url"
    os.system(Rf'cmd.exe /C START "" "{path_to_game}"')
```


In this example, I can launch the specified game from: a Graphical User Interface (GUI), a Command-Line Interface (CLI), Voice Commands (through Google Assistant), the StreamDeck Hardware, and on a schedule. 

---
Let's unpack all of that!

First, the function itself `spire()` launches a game called [Slay the Spire](https://store.steampowered.com/app/646570/Slay_the_Spire) from my  installation folder for games.

Then, there are the decorators:


- ```@Device(title='Spire', description="Launch Slay the Spire.")```
    - The `Device` decorator simply provides metadata to the function. 
- ```@Google(voice=multi_phrase(['open', 'play', 'place'], ['spire', 'fire', 'buyer']))```
    - The `Google` decorator provides an entry point through Google Assistant.
    - With the [appropriate setup](#google-assistant), the user would trigger the function with _"Hey Google, on pc, play spire"_. 
    - The `multi_phrase` function uses synonyms to accommodate phrases that may be misunderstood by the voice recognition.
- ```@Deck(location="Games/3,1", image='spire.jpg')```
    - The `StreamDeck` is a [device with programmable buttons](https://www.elgato.com/en/stream-deck) and this decorator places a button in a specific location (with an icon `spire.jpg`).

- ```@Scheduler(trigger="Daily", start="today-5:01pm")```
    - The `Scheduler` decorator executes the provided function regularly, in this case right on time to unwind!

### Decorators:
Each decorator is powered by a compiler that connects that function to a given service or device. Here are some basic examples. See [Compilers](#compilers) below for more details.

1. Create a simple function. 
    ```python
    import webbrowser

    def func():
        webbrowser.open("www.google.com")
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
    @Device(show=True, pause=True)  # Make a terminal window appear, and pause when execution is finished.
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

The number of functions can accumulate quickly, so to improve organization the `class syntax` uses nested `classes` to mimic a folder structure, as syntatic sugar. 
```python
@register(globals())
class Monitor:
    MAX_BRIGHTNESS: int = 100

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
To understand class syntax, we need to know a little bit about how Pybiosis works under the hood.

Each function must be accessible at the module level. This means that Pybiosis expects to be able to call something like `import monitors; monitors.brightness_up()`. The class syntax is nice because it allows us to organize the functions logically, but it complicates the namespace.

This is what the `register` decorator resolves. It decomposes the nested classes and puts the methods back into the global namespace (this is why `globals()` is used, and why the methods don't take `self`). So, even with the nesting, we can call `monitors.brightness_up()` directly. Note that class attributes _do_ need to be fully qualified: i.e. `Monitor.MAX_BRIGHTNESS` not just `MAX_BRIGHTNESS`.

Furthermore, some decorators (eg: streamdeck, scheduler) save an execution string (`python ...`) in a `.vbs` and `.bat` file. Those allow us to control whether a debug window pops up, for example. This accessible format allows the functions to be called from other programs that can't easily access python directly. For example, the StreamDeck doesn't easily support executing the right python command, but it easily supports running those script files.

## Compilers
Pybiosis comes with some built-in device compilers. You may also define your own if you have a novel device.

### StreamDeck
Requires a [StreamDeck](https://www.elgato.com/en/stream-deck).

1. Specify a location for the button to be placed specifying a folder, row, and column. See [Limitations](#limitations) about needing to _manually_ create folders through the StreamDeck GUI.
    ```python
    @StreamDeck(location='Folder/On/Stream/Deck/3,2')
    def func()
        pass
    ```
2. You can also specify multiple locations.
    ```python
    @StreamDeck(location=['Path1/3,2', 'Path2/3,2'])
    def func()
        pass
    ```
2. And an image. Images should be placed  in `PYBIOSIS_USER_PATH/Images`. See [Installation](#installation) for more details.
    ```python
    @StreamDeck(location='Path/3,2', image="my_image.png")
    def func()
        pass
    ```
If you use multiple StreamDeck profiles, you can set the Environment Variable `PYBIOSIS_PROFILE_ID` to the desired identifier (without `.sdProfile`). The identifiers can be found in `AppData\Roaming\Elgato\StreamDeck\ProfilesV2`.
### Google Assistant
Requires a [Push2Run](https://www.push2run.com/) installation and access to a Google Assistant device. Push2Run has been tested with the Dropbox method and the key phrase "on pc", although the API has historically been depreciated and possibly restored, so please check the link for the current status.

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

### Scheduler
Requires a Windows machine. No installation is required since it uses the Windows Task Scheduler. See [`schtasks.exe`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create) for more details on usage.

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

### CLI

You can access the full CLI, including any functions that are decorated (using `run`).
```bash
python -m pybiosis --help  # Get CLI usage information.
python -m pybiosis config --set user_path /Path/To/User/Path/  # Set the user path.
python -m pybiosis config --list  # List config variables.
python -m pybiosis compile  # Compile all decorated functions.
python -m pybiosis user  # Launch the user driver.py file (could be a CLI or main module).
python -m pybiosis run monitors.to_70  # Run a specific user function.
python -m pybiosis gui  # Launch the GUI to access functions graphically.
python -m pybiosis  # Launch the CLI as a simple GUI.
```
Please note that two aliases are also registered: `pybiosis` and `bb`, so you can run:
```bash
python -m pybiosis # Launch the CLI as a simple GUI.
pybiosis # Use a short form
bb  # Even shorter
```

See usage for more.

### GUI

Each compiler may implement a GUI (using `streamlit`) to provide more tailored access to their functions. This improves ease of use over the GUI CLI, but it requires additional development time to create.

See usage for more.

### Custom
You can also create your own compiler just by inheriting from `Device` (or a subclass). Check out the existing implementations for ideas.

## Installation
1. Install `Pybiosis` through pip with `pip install pybiosis`. For the latest version, simply use Githuib Desktop (or Git) to clone this repository and use `pip install -r requirements.txt -e .` in the directory with `setup.py`.
2. Create a directory to hold your custom functions and run `python -m pybiosis config --set user_path /Path/To/My/User/Path`.
3. Add a file called `driver.py` to that directory and have it contain this code:
    ```python
    import pybiosis
    import winsound
    
    @pybiosis.Device()  # Add additional decorators here.
    def beep():
        winsound.Beep(1000, 200)
    ```
    You can also decorate functions in any python files within your user path (eg: user_path/games.py), and they will also get registered.

## Usage
A CLI, a GUI wrapper for that CLI, and a GUI provide general access to these functions. Otherwise, they are accessible through the attached device/service.

1. Run `python -m pybiosis --help` to learn about the CLI, which includes `config`, `compile`, `run`, `gui`, and `user` commands. All decorated functions are accessible through the CLI.

![something](pybiosis/images/CLI.png)

2. Run `python -m pybiosis` to launch the CLI as a GUI (thanks to [gooey](https://github.com/chriskiehl/Gooey)). This GUI opens by default if no command is specified when invoking `pybiosis`.

![The CLI as a GUI](pybiosis/images/CLI_GUI.png)

3. It is highly recommended to provide a CLI for your driver.py file:

```python
from pybiosis.compilers.cli import CommandFramework
from rich import print  # Optional `pip install rich`

class Commands(CommandFramework):
    def add_videos(self, setup, args):
        if setup:
            pass # Use setup.add_arguments(...) to add parameters.
            return

        print(f"📺 Running the [green]Youtube[/green] command.")
	webbrowser.open("https://www.youtube.com")
```
This provides the ability for the user to define a CLI for custom  commands (in addition to being able to access the decorated functions). You can access a command (eg: videos) with `python -m pybiosis user videos`, or access the GUI CLI with `python -m pybiosis user`.

4. The command `python -m pybiosis gui` will launch a GUI for you to access the device functions. 

![The GUI, showing the streamdeck page.](pybiosis/images/GUI.png)

5. Finally, you can access your functions through the respective device (eg: google assistant, streamdeck, waiting for the scheduler).

## Limitations
1. Most of this functionality is tested on Windows.
2. If you get a password prompt from Push2Run, simply recompile until it stops.

## Future Work
1. Stream Deck folders cannot be generated programmatically yet, nor is deleting supported.
2. Make the PYBIOSIS_USER_PATH variable a config variable, rather than an environment one.
3. Fill out the GUI. Each device subclass should implement their own widget. For now, only the `StreamDeck` does.
4. Add tools like monitor control, audio controls, usb devices, games, GUI automation, dashboard.
5. Add keyboard and mouse decorators, eg: `@Click(region=(...))`, `@Press(combo=['SHIFT', 'A'])`. Add new cli command `monitor`/`watch`. Likely to use pip libraries [`keyboard`](https://pypi.org/project/keyboard/) and [`mouse`](https://pypi.org/project/mouse/).
6. Add examples folder.


## Questions?
Email me at nawar@palfore.com, or make a pull request!
