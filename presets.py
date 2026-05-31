"""
presets.py - catalogue of premade exercise configurations.

Each preset is a settings dict using the SAME keys as the app's import/export
JSON, so loading a preset reuses app.apply_import() directly - no extra logic.

HOW TO AUTHOR YOUR OWN:
  - Copy a line in PRESETS, give it a new name, and override what you want.
  - _base() fills in sensible defaults; you only pass the keys you change.
  - Notes must be EXACTLY one of the app's option strings, e.g.:
        "C", "C# / Db", "D", "D# / Eb", "E", "F",
        "F# / Gb", "G", "G# / Ab", "A", "A# / Bb", "B"
  - Octaves are ints (2-6). The app allows up to octave 5 freely, plus "C" at 6.
  - IMPORTANT: stay within the notes you actually have .wav files for in
    resources/Notes, or generation will fail for that preset.

The vocal ranges below are ROUGH, commonly-cited ranges as a starting point.
They are not authoritative and warm-up ranges are often narrower - tune by ear.
"""


def _base(**overrides):
    """Sensible defaults; override only the keys you want to change."""
    cfg = {
        "start_note": "C", "start_octave": 3,
        "end_note": "C", "end_octave": 4,
        "scale_type": "Major",
        "tempo": 100,
        "filename": "",
        "preset_pat_bin": True,
        "preset_pat": "1,2,3,2,1",
        "custom_pat_bin": False,
        "custom_pat": "",
        "durations": "",
        "duration_multiplier": 1.0,
        "note_steps": 1,
        "ascend_bin": True,
        "click_track": True,
        "chords_bin": True,
        "reverse_bin": True,
        "pause_bin": False,
    }
    cfg.update(overrides)
    return cfg


# Flat catalogue: the dropdown shows these keys. Rename / add / remove freely.
PRESETS = {
    "Bass (E2-E4)":
        _base(start_note="E", start_octave=2, end_note="E", end_octave=4,
              filename="bass_warmup"),
    "Baritone (A2-A4)":
        _base(start_note="A", start_octave=2, end_note="A", end_octave=4,
              filename="baritone_warmup"),
    "Tenor (C3-C5)":
        _base(start_note="C", start_octave=3, end_note="C", end_octave=5,
              filename="tenor_warmup"),
    "Alto (F3-F5)":
        _base(start_note="F", start_octave=3, end_note="F", end_octave=5,
              filename="alto_warmup"),
    "Mezzo-soprano (A3-A5)":
        _base(start_note="A", start_octave=3, end_note="A", end_octave=5,
              filename="mezzo_warmup"),
    "Soprano (C4-C6)":
        _base(start_note="C", start_octave=4, end_note="C", end_octave=6,
              filename="soprano_warmup"),

    # Example of a non-range-based preset (a specific drill rather than a voice):
    "Five-note major (1-2-3-4-5)":
        _base(start_note="C", start_octave=3, end_note="C", end_octave=4,
              preset_pat="1,2,3,4,5,4,3,2,1", tempo=120, filename="five_note"),
}


# OPTIONAL: if you'd rather group by category (e.g. Male / Female) and use two
# dropdowns in the app, structure it like this instead and adjust the app UI.
# Left here as a template - not used unless you switch the app over to it.
#
# PRESET_GROUPS = {
#     "Male":   {k: v for k, v in PRESETS.items()
#                if k.startswith(("Bass", "Baritone", "Tenor"))},
#     "Female": {k: v for k, v in PRESETS.items()
#                if k.startswith(("Alto", "Mezzo", "Soprano"))},
# }
