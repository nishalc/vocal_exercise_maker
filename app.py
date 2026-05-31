# vocal_exercise.py imports the Windows-only `winsound` at the top of the file.
# We are keeping vocal_exercise.py unchanged, and Streamlit Cloud runs on Linux
# where `winsound` does not exist -- so without this line the import below would
# crash the app on startup. We register an empty placeholder so that import
# succeeds. winsound is never used in this app (playback is st.audio), so the
# placeholder is never actually called.
import sys
import types
sys.modules.setdefault("winsound", types.ModuleType("winsound"))

import io
import json
import contextlib

import streamlit as st

from vocal_exercise import VocalExercise
from presets import PRESETS

# --- Footer credits ----------------------------------------------------------
AUTHOR_NAME = "Nishal Chandarana"
AUTHOR_EMAIL = "nishalc@outlook.com"  # set to "" to hide the email link
LINKS = {
    #"Website": "https://your-site.com",
    "Instagram": "https://instagram.com/nish_rana_music",
    "YouTube": "https://www.youtube.com/channel/UCTuJ0230Z-q7la2CZyDwEEw?view_as=subscriber",
    #"Spotify": "https://open.spotify.com/artist/your_id",
    "Buy me a coffee": "https://ko-fi.com/nish_rana",
}

# --- static option lists (mirror program_script.py) --------------------------
SCALES = ("Major", "minor", "Major Pentatonic", "minor Pentatonic")
NOTES = ("C", "C# / Db", "D", "D# / Eb", "E", "F",
         "F# / Gb", "G", "G# / Ab", "A", "A# / Bb", "B")
OCTAVES = (2, 3, 4, 5, 6)
SCALE_PATS = (
    "1,2,3,4,5,4,3,2,1", 
    "1,2,3,2,1", 
    "1,3,5,3,1", 
    "1,5,1", 
    "1,8,1",
    "1,3,5,8,5,3,1", 
    "1,3,5,8,8,8,8,5,3,1",
    "5,4,3,2,1", 
    "8,5,3,1",
    "1,3,5,8,10,12,11,9,7,5,4,2,1",
    "1,2,3,4,5,6,7,8,7,6,5,4,3,2,1",
    "1,2,3,4,5,6,7,8,9,8,7,6,5,4,3,2,1",
)

# Defaults, matching the original GUI's initial widget values.
DEFAULTS = {
    "start_note": "C",
    "start_octave": 2,
    "scale_type": "Major",
    "end_note": "C",
    "end_octave": 4,
    "tempo": 70,
    "filename": "",
    "pattern_mode": "Preset",          # internal -> preset/custom_pat_bin
    "preset_pat": "1,2,3,4,5,4,3,2,1",
    "custom_pat": "",
    "durations": "",
    "duration_multiplier": 1.0,
    "note_steps": 1,
    "note_order": "Ascending",         # internal -> ascend_bin
    "click_track": True,
    "chords_bin": True,
    "reverse_bin": False,
    "pause_bin": False,
}

def init_state():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v

def _safe(value, allowed, default):
    """Keep selectbox values within their option list, else fall back."""
    return value if value in allowed else default

def collect_values():
    """Build a dict matching program_script.py's PySimpleGUI `values`, so the
    exported JSON is interchangeable with the original app."""
    preset = st.session_state["pattern_mode"] == "Preset"
    ascend = st.session_state["note_order"] == "Ascending"
    return {
        "start_note": st.session_state["start_note"],
        "start_octave": int(st.session_state["start_octave"]),
        "scale_type": st.session_state["scale_type"],
        "end_note": st.session_state["end_note"],
        "end_octave": int(st.session_state["end_octave"]),
        "tempo": int(st.session_state["tempo"]),
        "filename": st.session_state["filename"],
        "preset_pat_bin": preset,
        "preset_pat": st.session_state["preset_pat"],
        "custom_pat_bin": not preset,
        "custom_pat": st.session_state["custom_pat"],
        "durations": st.session_state["durations"],
        "duration_multiplier": float(st.session_state["duration_multiplier"]),
        "note_steps": int(st.session_state["note_steps"]),
        "ascend_bin": ascend,
        "click_track": bool(st.session_state["click_track"]),
        "chords_bin": bool(st.session_state["chords_bin"]),
        "reverse_bin": bool(st.session_state["reverse_bin"]),
        "pause_bin": bool(st.session_state["pause_bin"]),
    }

def build_exercise(values):
    """Mirror of program_script.intialize_exercise -> (exercise, name_stem)."""
    bin_d = {
        "click_track": values["click_track"],
        "reverse_bin": values["reverse_bin"],
        "ascend_bin": values["ascend_bin"],
        "chords_bin": values["chords_bin"],
        "note_steps": int(values["note_steps"]),
        "pause_bin": values["pause_bin"],
    }
    start_note_tup = (values["start_note"], values["start_octave"])
    end_note_tup = (values["end_note"], values["end_octave"])
    tempo = int(values["tempo"])
    if values["preset_pat_bin"]:
        pattern = values["preset_pat"].split(",")
    else:
        pattern = values["custom_pat"].split(",")
    durations = values["durations"].split(",")
    scale_type = values["scale_type"]
    filename = values["filename"]
    duration_multiplier = float(values["duration_multiplier"])

    ex = VocalExercise(start_note_tup, end_note_tup, tempo, pattern,
                       durations, scale_type, bin_d, filename,
                       duration_multiplier)
    ex.generate()
    return ex, ex.name.split(".")[0]

def apply_import(raw):
    """Populate session_state from an imported JSON dict (original schema)."""
    g = raw.get
    st.session_state["start_note"] = _safe(g("start_note", DEFAULTS["start_note"]), NOTES, DEFAULTS["start_note"])
    st.session_state["end_note"] = _safe(g("end_note", DEFAULTS["end_note"]), NOTES, DEFAULTS["end_note"])
    st.session_state["scale_type"] = _safe(g("scale_type", DEFAULTS["scale_type"]), SCALES, DEFAULTS["scale_type"])
    st.session_state["preset_pat"] = _safe(g("preset_pat", DEFAULTS["preset_pat"]), SCALE_PATS, DEFAULTS["preset_pat"])

    try:
        st.session_state["start_octave"] = _safe(int(g("start_octave", DEFAULTS["start_octave"])), OCTAVES, DEFAULTS["start_octave"])
    except (TypeError, ValueError):
        st.session_state["start_octave"] = DEFAULTS["start_octave"]
    try:
        st.session_state["end_octave"] = _safe(int(g("end_octave", DEFAULTS["end_octave"])), OCTAVES, DEFAULTS["end_octave"])
    except (TypeError, ValueError):
        st.session_state["end_octave"] = DEFAULTS["end_octave"]
    try:
        st.session_state["tempo"] = int(g("tempo", DEFAULTS["tempo"]))
    except (TypeError, ValueError):
        st.session_state["tempo"] = DEFAULTS["tempo"]
    try:
        st.session_state["note_steps"] = max(1, int(g("note_steps", DEFAULTS["note_steps"])))
    except (TypeError, ValueError):
        st.session_state["note_steps"] = DEFAULTS["note_steps"]
    try:
        st.session_state["duration_multiplier"] = float(g("duration_multiplier", DEFAULTS["duration_multiplier"]))
    except (TypeError, ValueError):
        st.session_state["duration_multiplier"] = DEFAULTS["duration_multiplier"]

    st.session_state["filename"] = str(g("filename", DEFAULTS["filename"]))
    st.session_state["custom_pat"] = str(g("custom_pat", DEFAULTS["custom_pat"]))
    st.session_state["durations"] = str(g("durations", DEFAULTS["durations"]))
    st.session_state["click_track"] = bool(g("click_track", DEFAULTS["click_track"]))
    st.session_state["chords_bin"] = bool(g("chords_bin", DEFAULTS["chords_bin"]))
    st.session_state["reverse_bin"] = bool(g("reverse_bin", DEFAULTS["reverse_bin"]))
    st.session_state["pause_bin"] = bool(g("pause_bin", DEFAULTS["pause_bin"]))

    # two mutually-exclusive radios -> single radio
    if bool(g("custom_pat_bin", False)) and not bool(g("preset_pat_bin", True)):
        st.session_state["pattern_mode"] = "Custom"
    else:
        st.session_state["pattern_mode"] = "Preset"
    st.session_state["note_order"] = "Ascending" if bool(g("ascend_bin", True)) else "Descending"


def main():
    st.set_page_config(page_title="Vocal Exercise Maker", layout="centered")
    init_state()
    st.title("Nish's Vocal Exercise Maker v1.0")

    # ---- Preset catalogue (handled before widgets so session_state can be set)
    if PRESETS:
        with st.expander("Load preset / voice type", expanded=False):
            names = list(PRESETS.keys())
            c = st.columns([4,1], vertical_alignment="bottom")
            c[0].selectbox("Voice type / preset", names, key="preset_choice")
            if c[1].button("Apply preset"):
                apply_import(PRESETS[chosen])
                st.rerun()
 
    # ---- Import (handled before widgets so session_state can be set) --------
    with st.expander("Import exercise (.json)"):
        up = st.file_uploader("Load a saved settings file", type="json", key="import_file")
        if up is not None:
            file_id = (up.name, up.size)
            if st.session_state.get("_last_import_id") != file_id:
                try:
                    apply_import(json.load(up))
                    st.session_state["_last_import_id"] = file_id
                    st.rerun()
                except Exception as e:
                    st.error(f"Import failed: {e}")
            else:
                st.caption(f"Loaded: {up.name}")

    # ---- Inputs ------------------------------------------------------
    st.header("Input")
    c = st.columns([2,2])
    c[0].text_input("Filename header (can be blank)", key="filename")
    c[1].number_input("Tempo (bpm)", key="tempo", min_value=1, step=1)
    
    c = st.columns([2, 1, 2, 1, 0.25, 2])
    c[0].selectbox("Lowest note", NOTES, key="start_note")
    c[1].selectbox("Octave", OCTAVES, key="start_octave")
    c[2].selectbox("Highest note", NOTES, key="end_note")
    c[3].selectbox("Octave ", OCTAVES, key="end_octave")  # trailing space = distinct label
    c[5].selectbox("Scale", SCALES, key="scale_type")

    c = st.columns([1, 3])
    c[0].radio("Pattern", ["Preset", "Custom"], key="pattern_mode", horizontal=True)
    if st.session_state["pattern_mode"] == "Preset":
        c[1].selectbox("Preset pattern", SCALE_PATS, key="preset_pat")
    else:
        c[1].text_input("Custom pattern (comma separated scale degrees)", key="custom_pat")

    c = st.columns([1, 3])
    c[0].number_input("Multiplier", key="duration_multiplier", min_value=0.0, step=0.25, format="%.2f")
    c[1].text_input("Durations (comma separated, 1 = single beat, blank = all notes get 1)", key="durations")

    #c = st.columns([3, 1])
    #c[0].text_input("Note durations (comma-separated; leave blank for all equal)", key="durations")
    #c[1].number_input("Multiplier", key="duration_multiplier", min_value=0.0, step=0.25, format="%.2f")

    #c = st.columns([3, 1])
    #c[0].text_input("Filename", key="filename")
    #c[1].number_input("Tempo (bpm)", key="tempo", min_value=1, step=5)

    # ---- Options ---------------------------------------------------
    st.header("Options")
    c = st.columns([2, 2])
    c[0].number_input("Note increment", key="note_steps", min_value=1, step=1)
    c[1].radio("Order", ["Ascending", "Descending"], key="note_order", horizontal=True)

    c = st.columns(4)
    c[0].checkbox("Click track", key="click_track")
    c[1].checkbox("Chords", key="chords_bin")
    c[2].checkbox("Repeat and reverse", key="reverse_bin")
    c[3].checkbox("Extra pause between", key="pause_bin")

    # ---- Outputs --------------------------------------------------------
    st.header("Output")

    if st.button("Generate track", type="primary"):
        values = collect_values()
        log = io.StringIO()
        try:
            with contextlib.redirect_stdout(log):
                ex, stem = build_exercise(values)
            buf = io.BytesIO()
            ex.exercise.export(buf, format="wav")
            st.session_state["wav_bytes"] = buf.getvalue()
            st.session_state["wav_name"] = ex.name
            st.session_state["json_bytes"] = json.dumps(values).encode("utf-8")
            st.session_state["json_name"] = stem + ".json"
            st.session_state["gen_log"] = log.getvalue()
            st.session_state["gen_error"] = None
        except Exception as e:
            st.session_state["wav_bytes"] = None
            st.session_state["gen_log"] = log.getvalue()
            st.session_state["gen_error"] = f"{type(e).__name__}: {e}"

    # Output box (mirrors the sg.Output element) + any error
    log_text = st.session_state.get("gen_log", "")
    if log_text:
        st.text_area("Output", log_text, height=120, disabled=True)
    if st.session_state.get("gen_error"):
        st.error(st.session_state["gen_error"])

    # Player + downloads (only after a successful generate)
    if st.session_state.get("wav_bytes"):
        st.audio(st.session_state["wav_bytes"], format="audio/wav")
        c = st.columns(2)
        c[0].download_button("Download settings (.json)", data=st.session_state["json_bytes"],
                             file_name=st.session_state["json_name"], mime="application/json")
        c[1].download_button("Download .wav", data=st.session_state["wav_bytes"],
                             file_name=st.session_state["wav_name"], mime="audio/wav")

    # ---- Footer / credits ---------------------------------------------------
    st.divider()
    items = list(LINKS.items())
    if AUTHOR_EMAIL:
        items.append(("Email me", f"mailto:{AUTHOR_EMAIL}"))
    link_md = " · ".join(f"[{name}]({url})" for name, url in items if url)
    st.caption(f"Made by {AUTHOR_NAME}")
    if link_md:
        st.caption(link_md)

if __name__ == "__main__":
    main()
