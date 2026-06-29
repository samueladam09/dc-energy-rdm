import os
import streamlit.components.v1 as components

_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

# DEBUG — print the path so we can see what Streamlit is looking for
print("=" * 60)
print(f"Component frontend dir: {_FRONTEND_DIR}")
print(f"Dir exists: {os.path.exists(_FRONTEND_DIR)}")
if os.path.exists(_FRONTEND_DIR):
    print(f"Files found: {os.listdir(_FRONTEND_DIR)}")
else:
    print("DIRECTORY NOT FOUND")
print("=" * 60)

_parcoords = components.declare_component(
    "parcoords_component",
    path=_FRONTEND_DIR,
)


def parcoords_chart(payload: dict, height: int = 700) -> None:
    _parcoords(payload=payload, height=height, default=None)