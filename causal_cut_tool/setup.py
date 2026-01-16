from pathlib import Path
from setuptools import setup

# This is where you add any fancy path resolution to the local lib:
plugin_handler_path: str = (Path(__file__).parent.parent / "causal_cut_plugin_handler").as_uri()
plugin_path: str = (Path(__file__).parent.parent / "causal_cut_plugin").as_uri()
print("Setting up")
setup(
    install_requires=[
        f"causal-cut-plugin-handler @ {plugin_handler_path}/",
        f"causal-cut-plugin @ {plugin_path}/",
    ]
)