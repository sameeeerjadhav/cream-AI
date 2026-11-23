"""Root entrypoint for Streamlit Community Cloud.

Forwards execution to ui/app.py so both 'streamlit_app.py' and 'ui/app.py'
work as valid main file paths on Streamlit Cloud.
"""

from pathlib import Path
import runpy

UI_APP_PATH = Path(__file__).resolve().parent / "ui" / "app.py"

if __name__ == "__main__":
    runpy.run_path(str(UI_APP_PATH), run_name="__main__")
