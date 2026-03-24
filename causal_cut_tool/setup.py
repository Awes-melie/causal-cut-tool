from pathlib import Path
from setuptools import setup

plugin_path: str = (Path(__file__).parent / "causal_cut_plugin").as_uri()

setup(
    install_requires=[
        f"causal-cut-plugin @ {plugin_path}/",
        "pyarrow>=16.1.0",
        "jsonpickle>=3.2.2",
        "causal_testing_framework==8.1.0",
        "pyswarms==1.3.0",
        "python-dotenv==1.0.0",
        "markovify==0.9.4",
        "jinja2==3.1.4",
        "openpyxl==3.1.0",
        "cliffs_delta==1.0.0",
        "setuptools<=81",
    ]
)