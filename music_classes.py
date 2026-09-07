#Inside a class or function, the first triple-quoted string becomes the docstring.
class Note:

    def __init__(self, pitch, start, end, velocity=100, channel=0, flags=None):
        """
        Represents one musical note extracted from a score or MIDI track.

        :param pitch: MIDI note number (int) or custom representation
        :param start: start time in seconds (float)
        :param end: end time in seconds (float)
        :param velocity: how loud (0–127)
        :param channel: MIDI channel (0–15)
        :param flags: dictionary for extra metadata (e.g. articulation)
        """

        self.pitch = int(pitch)
        self.start = float(start)
        self.end = float(end)
        self.velocity = int(velocity)
        self.channel = int(channel)
        self.flags = flags if flags is not None else []

    #The string that shows when printing or debugging.
    def __repr__(self):

        return (f"Note(pitch={self.pitch}, start={self.start:.3f}, "
            f"end={self.end:.3f}, int={self.velocity}, ch={self.channel}, "
            f"flags={self.flags})")
   
    #Allows duration to be called like a normal attribute ("note.duration" instead of "note.get_duration()").
    @property
    def duration(self):

        return self.end - self.start


class Track:

    def __init__(self, name = "", notes = None):
        """
        Represents one track with all of its metadata and associated notes.

        :param name: track name
        """

        self.name = name
        self.notes = notes if notes is not None else []

    def __repr__(self):

        return (f"Track(name={self.name}, notes={len(self.notes)})")
    
    @property
    def duration(self):
        """Compute total track end length by looking at the latest instruction end."""

        if not self.notes:
            return 0.0
        
        return max(i.end for i in self.notes)

    def sort(self):
        """Sort notes by start time, then pitch."""

        self.notes.sort(key=lambda inst: (inst.start, inst.pitch))

    def add_note(self, note):
        """Add a single Note object to the track."""

        self.notes.append(note)


class Song:

    def __init__(self, title="Untitled", key="C", tempo=500000, time_signature="4/4", tracks = None):
        """
        Represents a full song composed of multiple tracks.

        :param title: song title
        :param key: key signature (e.g., 'C', 'Am', 'F#')
        :param tempo: measured in microseconds, default value corresponds to 120 bpm if time_signature is 4/4
        :param time_signature: time signature (e.g., '4/4', '3/4')
        """

        self.title = str(title)
        self.key = str(key)
        self.tempo=int(tempo)
        self.time_signature = str(time_signature)
        self.tracks = tracks if tracks is not None else []

    @property
    def duration(self):
        """Compute total song length by looking at the latest track end."""

        if not self.tracks:
            return 0.0
        
        return max(i.duration for i in self.tracks)

    @property
    def bpm(self):
        """Beats per minute. hardocded for 4/4 time signature"""
        
        return int(60000000 / self.tempo)

    def __repr__(self):
        
        return (f"Song(title='{self.title}', key='{self.key}', bpm='{self.bpm}' "
                f"time_signature='{self.time_signature}', "
                f"tracks={len(self.tracks)})")
    
    def add_track(self, track):
        """Add a single track object to the song."""

        self.tracks.append(track)


class Staff:

    def __init__(self, lines = None):
        
        self.lines = lines if lines is not None else []

        ys = [row[0] for line in self.lines for row in line]

        self.center = int(sum(ys)/len(ys))

        self.symbols = []

    def __repr__(self):

        return (f"Center='{self.center}', N_Lines='{len(self.lines)}', Lines='{self.lines}'")
    
    @property
    def max_thickness(self):

        return len(max(self.lines, key=len)) if self.lines else None

    def order_symbols(self):
        
        self.symbols = sorted(self.symbols, key=lambda s: s["bbox"][0])