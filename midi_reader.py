import mido

mid = mido.MidiFile("/app/midi_files/Coldplay - Viva La Vida.mid")

for i, track in enumerate(mid.tracks):
    print(f"Track {i}: {track.name}")
    for msg in track:
        print(msg)