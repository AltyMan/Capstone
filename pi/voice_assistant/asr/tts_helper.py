from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
JARVIS_DIR = SCRIPT_DIR / "models" / "jarvis"

def generate_tts_mp3(file_list_str: str) -> bytes:
    """
    Reads local pre-generated MP3 files and combines their bytes.
    Accepts a comma-separated list of filenames.
    """
    if not file_list_str:
        return b""
        
    combined_bytes = b""
    files = [f.strip() for f in file_list_str.split(",")]
    
    print(f"[AUDIO] Fetching local files: {files}")
    
    for filename in files:
        filepath = JARVIS_DIR / filename
        if filepath.exists():
            with open(filepath, "rb") as f:
                combined_bytes += f.read()
        else:
            print(f"[AUDIO ERROR] Missing local file: {filepath}")
            
    return combined_bytes

if __name__ == "__main__":
    # Quick test to ensure pathing works
    test_files = "checking.mp3,plug-one.mp3"
    audio_data = generate_tts_mp3(test_files)
    
    if audio_data:
        with open("local_test_output.mp3", "wb") as f:
            f.write(audio_data)
        print("Saved combined local_test_output.mp3 to disk. Go ahead and play it!")