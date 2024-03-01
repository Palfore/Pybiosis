import argparse
import json
from pathlib import Path

class ConfigurationManager:
    CONFIG_FILE: Path = Path(__file__).parent.parent / ".config.json"

    def __init__(self):
        self.load_config()

    def load_config(self):
        if self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE, 'r') as file:
                self.config = json.load(file)
        else:
            self.config = {}
        return self.config

    def save_config(self):
        with open(self.CONFIG_FILE, 'w') as file:
            json.dump(self.config, file, indent=4)

    def list_config(self):
        config = self.load_config()
        if config:
            for key, value in config.items():
                print(f"{key}: {value}")
        else:
            print("There are no configuration variables set.")

    def clear_config(self, key):
        if key in self.config:
            del self.config[key]
            self.save_config()

    def set_config(self, key, value):
        self.config[key] = value
        self.save_config()

    def interactive_mode(self, variables):
        config = self.load_config()
        variables = list(set(variables) | set(config)) # TODO: SORT        
        print("Interactive mode:")
        for i, key in enumerate(variables, 1):
            match input(f"Set Key #{i} `{key}`: "):
                case '':
                    print(f"\tSkipping. `{key}` is `{self.config.get(key)}`")

                case '""':
                    print(f"\tClearing {key}")
                    self.clear_config(key)

                case "''":
                    print(f"\tClearing {key}")
                    self.clear_config(key)

                case value:
                    print(f"\tSetting `{key}` to `{value}`")
                    self.set_config(key, value)
                    

        print("Exiting interactive mode.")

    def get(self, key, default=None):
        return self.config.get(key, default)
