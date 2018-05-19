from cx_Freeze import setup, Executable

base = None    

executables = [Executable("vsqMidiV2.py", base=base)]

packages = ["idna", "sys", "pyknon"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "VSQX to MIDI",
    options = options,
    version = "2.0",
    description = 'GUI added',
    executables = executables
)