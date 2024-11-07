from typing import Dict, Any

class ExamplePlugin:
    def __init__(self):
        self.name = "Example Plugin"

    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        return {
            "status": "success",
            "message": "Example plugin executed successfully",
            "args": args,
            "kwargs": kwargs
        }

def register_plugin():
    return ExamplePlugin()