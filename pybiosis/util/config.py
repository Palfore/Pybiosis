import argparse
import json
from pathlib import Path

class ConfigurationManager:
    def __init__(self, config_file: str, config_variables: list=None):
        # Set the config file path.
        self.config_file = config_file

        # Set the config variables.
        if not config_variables:
            config_variables = []
        self.config_variables = config_variables
    
        # Load the config file.        
        self.load_config()

    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as file:
                self.config = json.load(file)
        else:
            self.config = {}
            self.save_config()
        return self.config

    def save_config(self):
        with open(self.config_file, 'w') as file:
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

    def has(self, key):
        return key in self.config

    def dispatch(self, args):
        match args:
            case argparse.Namespace(set=[key, value]):
                print(f"Setting `{key}` to `{value}`")
                self.set_config(key, value)
                print("Completed. Listing Now:")
                self.list_config()

            case argparse.Namespace(set=[key]):
                print(f"Clearing `{key}`")
                self.clear_config(key)

            case argparse.Namespace(set=[key, *values]):
                raise ValueError(f"Must provide key or key-value pair for --set, not: {[key, *values]}")            

            case argparse.Namespace(interactive=True):
                self.interactive_mode(self.config_variables)
            
            case argparse.Namespace(list=True):
                print(f"Listing")
                self.list_config()
            
            case _:
                print(f"Listing (default)")
                self.list_config()

