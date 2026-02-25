from pathlib import Path
from setuptools import setup

plugin_path: str = (Path(__file__).parent / "causal_cut_plugin").as_uri()

setup(
    install_requires=[
        f"causal-cut-plugin @ {plugin_path}/",
    ]
)