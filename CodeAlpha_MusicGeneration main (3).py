import tkinter as tk
from tkinter import ttk, messagebox
import threading
import random
import os
import time
from midiutil import MIDIFile

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except:
    PYGAME_AVAILABLE = False

BG           = "#050508"
GLASS        = "#0d1117"
GLASS2       = "#111827"
BLUE         = "#2563eb"
BLUE_LIGHT   = "#3b82f6"
BLUE_GLOW    = "#1d4ed8"
SILVER       = "#94a3b8"
SILVER_LIGHT = "#cbd5e1"
WHITE        = "#f1f5f9"
DIM          = "#334155"
ACCENT       = "#38bdf8"
BORDER       = "#1e3a5f"

# ─── Each style has unique scale, tempo, rhythm, durations, rests ─
STYLES = {
    "happy": {
        "scale": [60,62,64,67,69,72,74,76],
        "tempo": 138, "vel": (85,110),
        "durations": [0.25, 0.25, 0.5, 0.25],
        "patterns": [[0,2,4,7,4,2],[4,7,9,7,4,2],[0,4,7,4,0,2]],
        "rest_chance": 0.05,
    },
    "sad": {
        "scale": [57,59,60,62,64,65,67],
        "tempo": 58, "vel": (40,65),
        "durations": [1.0, 1.5, 0.5, 2.0],
        "patterns": [[0,1,2,1,0],[2,1,0,1,2,3],[0,2,1,0]],
        "rest_chance": 0.2,
    },
    "epic": {
        "scale": [60,63,65,67,70,72,75],
        "tempo": 160, "vel": (100,127),
        "durations": [0.25, 0.125, 0.5, 0.25],
        "patterns": [[0,2,4,6,4,2,0,3],[0,4,6,4,0,6,4,0],[2,4,6,2,4,6,2,0]],
        "rest_chance": 0.02,
    },
    "jazz": {
        "scale": [60,62,63,65,67,69,70,72,74],
        "tempo": 112, "vel": (65,95),
        "durations": [0.33, 0.67, 0.33, 0.5, 0.25],
        "patterns": [[0,2,4,3,5,4,2],[1,3,5,4,2,0,3],[0,4,2,5,3,1,4]],
        "rest_chance": 0.15,
    },
    "lofi": {
        "scale": [60,62,64,65,67,69,71],
        "tempo": 75, "vel": (45,68),
        "durations": [0.5, 1.0, 0.75, 0.25],
        "patterns": [[0,2,1,3,2,4],[4,2,3,1,2,0],[0,1,3,2,4,3,1]],
        "rest_chance": 0.25,
    },
    "dark": {
        "scale": [60,61,63,65,66,68,70],
        "tempo": 88, "vel": (60,90),
        "durations": [0.5, 0.75, 1.0, 0.25],
        "patterns": [[0,1,2,1,0,3],[2,1,0,3,2,1],[0,3,2,0,1,3]],
        "rest_chance": 0.18,
    },
    "chill": {
        "scale": [60,62,64,65,67,69,71],
        "tempo": 82, "vel": (50,75),
        "durations": [0.75, 0.5, 1.0, 0.5],
        "patterns": [[0,2,4,2,1,3],[4,2,0,2,4,5],[0,4,2,5,3,1]],
        "rest_chance": 0.2,
    },
    "classical": {
        "scale": [60,62,64,65,67,69,71,72],
        "tempo": 96, "vel": (60,100),
        "durations": [0.5, 0.25, 1.0, 0.5],
        "patterns": [[0,2,4,5,4,2,0],[0,4,7,4,0,2,5,4],[2,4,5,4,2,0,1,2]],
        "rest_chance": 0.08,
    },
    "ambient": {
        "scale": [60,62,64,67,69,72,74],
        "tempo": 65, "vel": (35,60),
        "durations": [2.0, 1.5, 3.0, 1.0],
        "patterns": [[0,2,4,2],[4,2,0,4],[0,4,2,6]],
        "rest_chance": 0.3,
    },
    "blues": {
        "scale": [60,63,65,66,67,70,72,75],
        "tempo": 92, "vel": (72,105),
        "durations": [0.33, 0.67, 0.5, 0.25],
        "patterns": [[0,2,3,2,1,3],[1,3,2,0,3,1],[0,3,2,1,3,2]],
        "rest_chance": 0.12,
    },
    "romantic": {
        "scale": [64,66,67,69,71,72,74,76],
        "tempo": 76, "vel": (55,85),
        "durations": [1.0, 0.5, 1.5, 0.75],
        "patterns": [[0,2,4,5,4,2],[4,2,0,2,4,7],[0,4,2,5,3,4]],
        "rest_chance": 0.15,
    },
    "energetic": {
        "scale": [60,62,64,67,69,72,74,76],
        "tempo": 172, "vel": (95,127),
        "durations": [0.125, 0.25, 0.125, 0.25],
        "patterns": [[0,4,7,4,2,7,4,2],[0,2,4,7,9,7,4,2],[7,4,2,0,2,4,7,9]],
        "rest_chance": 0.03,
    },
    "piano": {
        "scale": [60,62,64,65,67,69,71,72],
        "tempo": 90, "vel": (60,95),
        "durations": [0.5, 0.25, 1.0, 0.75],
        "patterns": [[0,2,4,5,4,2,0],[0,4,7,4,0,5,9,7],[2,5,4,2,0,1,2,4]],
        "rest_chance": 0.1,
    },
}

DEFAULT_STYLE = STYLES["chill"]

def parse_prompt(prompt):
    prompt = prompt.lower()
    for key in STYLES:
        if key in prompt:
            return STYLES[key]
    # keyword matching
    if any(w in prompt for w in ["melancholy","cry","depressing","mourn"]): return STYLES["sad"]
    if any(w in prompt for w in ["powerful","battle","war","intense"]): return STYLES["epic"]
    if any(w in prompt for w in ["night","midnight","mysterious","haunting"]): return STYLES["dark"]
    if any(w in prompt for w in ["relax","sleep","soft","gentle","peaceful"]): return STYLES["chill"]
    if any(w in prompt for w in ["fast","hype","party","dance"]): return STYLES["energetic"]
    if any(w in prompt for w in ["love","heart","tender","sweet"]): return STYLES["romantic"]
    return DEFAULT_STYLE

def generate_music(style, n=64):
    scale     = style["scale"]
    tempo     = style["tempo"]
    vmin, vmax = style["vel"]
    durations  = style["durations"]
    patterns   = style["patterns"]
    rest_chance= style["rest_chance"]

    notes_out = []
    times_out = []
    durs_out  = []
    vels_out  = []

    t = 0.0
    count = 0
    while count < n:
        pat = random.choice(patterns)
        oct_shift = random.choice([0,0,0,12,-12])
        for p in pat:
            if count >= n:
                break
            dur = random.choice(durations)
            if random.random() < rest_chance:
                t += dur
                count += 1
                continue
            note = scale[p % len(scale)] + oct_shift
            vel  = random.randint(vmin, vmax)
            notes_out.append(note)
            times_out.append(t)
            durs_out.append(dur * 0.88)
            vels_out.append(vel)
            t += dur
            count += 1

    return notes_out, times_out, durs_out, vels_out, tempo

def save_midi(notes, times, durs, vels, tempo, filename="generated_music.mid"):
    midi = MIDIFile(1)
    midi.addTempo(0, 0, tempo)
    for note, t, dur, vel in zip(notes, times, durs, vels):
        midi.addNote(0, 0, int(note), t, max(dur, 0.05), int(vel))
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, "wb") as f:
        midi.writeFile(f)
    return filepath

class WaveformCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bars    = 52
        self.heights = [2.0] * self.bars
        self.target  = [2.0] * self.bars
        self.playing = False
        self.configure(bg=GLASS, highlightthickness=0)
        self._animate()

    def start(self): self.playing = True
    def stop(self):
        self.playing = False
        self.target = [2.0] * self.bars

    def _animate(self):
        w = self.winfo_width() or 620
        h = self.winfo_height() or 72
        self.delete("all")
        if self.playing:
            for i in range(self.bars):
                self.target[i] = random.randint(4, int(h * 0.88))
        bar_w = w / self.bars
        for i in range(self.bars):
            self.heights[i] += (self.target[i] - self.heights[i]) * 0.28
            bh = self.heights[i]
            x1 = i * bar_w + 1
            x2 = x1 + bar_w - 2
            y1 = (h - bh) / 2
            y2 = (h + bh) / 2
            ratio = min(bh / h, 1.0)
            r = int(30  + ratio * 15)
            g = int(90  + ratio * 100)
            b = 240
            self.create_rectangle(x1, y1, x2, y2, fill=f"#{r:02x}{g:02x}{b:02x}", outline="")
        self.after(45, self._animate)

class SunoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SoundMind AI — CodeAlpha")
        self.geometry("820x700")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.midi_path = None
        self._build_ui()

    def _build_ui(self):
        tk.Frame(self, height=2, bg=BLUE).pack(fill="x")

        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=35, pady=(28,0))
        lft = tk.Frame(hdr, bg=BG)
        lft.pack(side="left")
        tk.Label(lft, text="SoundMind", font=("Georgia",30,"bold"), bg=BG, fg=WHITE).pack(side="left")
        tk.Label(lft, text=" AI",       font=("Georgia",30,"bold"), bg=BG, fg=ACCENT).pack(side="left")
        bdg = tk.Frame(hdr, bg=BLUE_GLOW)
        bdg.pack(side="left", padx=(12,0), pady=(10,0))
        tk.Label(bdg, text=" CodeAlpha ", font=("Courier",8,"bold"), bg=BLUE_GLOW, fg=WHITE).pack(padx=6,pady=3)
        tk.Label(hdr, text="Generate music with AI", font=("Courier",10), bg=BG, fg=SILVER).pack(side="right", pady=(12,0))

        tk.Frame(self, height=1, bg=BORDER).pack(fill="x", padx=35, pady=(18,22))

        # Prompt
        po = tk.Frame(self, bg=BORDER)
        po.pack(fill="x", padx=35, pady=(0,5))
        pi = tk.Frame(po, bg=GLASS2)
        pi.pack(fill="x", padx=1, pady=1)
        tk.Label(pi, text="✦  DESCRIBE YOUR MUSIC", font=("Courier",8,"bold"), bg=GLASS2, fg=ACCENT).pack(anchor="w", padx=16, pady=(12,4))
        self.prompt_var = tk.StringVar()
        self.prompt_entry = tk.Entry(pi, textvariable=self.prompt_var, font=("Georgia",14), bg=GLASS2, fg=WHITE, insertbackground=ACCENT, relief="flat", bd=0)
        self.prompt_entry.pack(fill="x", padx=16, pady=(0,14))
        self.prompt_entry.insert(0, "calm piano with soft jazz vibes...")
        self.prompt_entry.bind("<FocusIn>", self._clear_ph)
        self.prompt_entry.bind("<Return>", lambda e: self._generate())

        # Tags
        tf = tk.Frame(self, bg=BG)
        tf.pack(fill="x", padx=35, pady=(8,18))
        tk.Label(tf, text="Quick tags: ", font=("Courier",8), bg=BG, fg=DIM).pack(side="left")
        for tag in ["happy","sad","epic","jazz","lofi","dark","chill","blues","ambient","energetic","romantic"]:
            tk.Button(tf, text=tag, font=("Courier",8), bg=GLASS2, fg=SILVER, bd=0, cursor="hand2", padx=7, pady=3,
                      activebackground=BLUE, activeforeground=WHITE,
                      command=lambda t=tag: self._set_tag(t)).pack(side="left", padx=2)

        # Settings
        sf = tk.Frame(self, bg=BG)
        sf.pack(fill="x", padx=35, pady=(0,18))
        for lbl, vname, opts, default in [
            ("DURATION","dur_var",["16 bars","32 bars","64 bars","128 bars"],"64 bars"),
            ("TEMPO OVERRIDE","tempo_var",["Auto","Slow","Medium","Fast","Very Fast"],"Auto"),
        ]:
            bx = tk.Frame(sf, bg=GLASS2)
            bx.pack(side="left", expand=True, fill="x", padx=(0,10))
            tk.Label(bx, text=lbl, font=("Courier",7,"bold"), bg=GLASS2, fg=ACCENT).pack(anchor="w", padx=10, pady=(8,2))
            var = tk.StringVar(value=default)
            setattr(self, vname, var)
            ttk.Combobox(bx, textvariable=var, values=opts, state="readonly", font=("Segoe UI",10), width=16).pack(padx=10, pady=(0,8), fill="x")

        # Generate
        gf = tk.Frame(self, bg=BG)
        gf.pack(pady=(0,16))
        self.gen_btn = tk.Button(gf, text="  ✦  Generate Music  ✦  ", font=("Georgia",13,"bold"),
                                  bg=BLUE, fg=WHITE, bd=0, cursor="hand2", padx=30, pady=12,
                                  activebackground=BLUE_LIGHT, activeforeground=WHITE, command=self._generate)
        self.gen_btn.pack(side="left", padx=8)

        self.status_var = tk.StringVar(value="Ready to create something amazing...")
        tk.Label(self, textvariable=self.status_var, font=("Courier",9), bg=BG, fg=SILVER).pack()

        pf = tk.Frame(self, bg=BG)
        pf.pack(fill="x", padx=35, pady=(6,0))
        self.progress = ttk.Progressbar(pf, mode='determinate')
        self.progress.pack(fill="x")

        # Waveform
        wo = tk.Frame(self, bg=BORDER)
        wo.pack(fill="x", padx=35, pady=(18,0))
        wi = tk.Frame(wo, bg=GLASS)
        wi.pack(fill="x", padx=1, pady=1)
        tk.Label(wi, text="WAVEFORM VISUALIZER", font=("Courier",7,"bold"), bg=GLASS, fg=DIM).pack(anchor="w", padx=14, pady=(10,4))
        self.wave = WaveformCanvas(wi, height=72)
        self.wave.pack(fill="x", padx=14, pady=(0,10))

        # Player
        pl = tk.Frame(self, bg=GLASS2)
        pl.pack(fill="x", padx=35)
        self.track_label = tk.Label(pl, text="♪  No track generated yet", font=("Georgia",11), bg=GLASS2, fg=SILVER_LIGHT)
        self.track_label.pack(side="left", padx=16, pady=14)
        ctrl = tk.Frame(pl, bg=GLASS2)
        ctrl.pack(side="right", padx=16)
        for sym, cmd in [("⏮",self._restart),("▶",self._play),("⏹",self._stop)]:
            tk.Button(ctrl, text=sym, font=("Segoe UI",14), bg=GLASS2, fg=SILVER_LIGHT, bd=0,
                      cursor="hand2", padx=8, activebackground=BLUE, activeforeground=WHITE, command=cmd).pack(side="left", padx=4, pady=10)

        tk.Frame(self, height=2, bg=BLUE_GLOW).pack(fill="x", side="bottom")

    def _clear_ph(self, e):
        if self.prompt_entry.get() == "calm piano with soft jazz vibes...":
            self.prompt_entry.delete(0, "end")

    def _set_tag(self, tag):
        self.prompt_entry.delete(0, "end")
        self.prompt_entry.insert(0, tag)

    def _generate(self):
        prompt = self.prompt_var.get().strip()
        if not prompt or prompt == "calm piano with soft jazz vibes...":
            prompt = "chill"
        self.gen_btn.configure(state="disabled", bg=DIM)
        self.progress['value'] = 0
        self.wave.stop()

        def task():
            try:
                self._upd(10, "🎵 Analyzing prompt...")
                style = parse_prompt(prompt)
                t_choice = self.tempo_var.get()
                if t_choice == "Slow":       style = dict(style); style["tempo"] = 65
                elif t_choice == "Medium":   style = dict(style); style["tempo"] = 95
                elif t_choice == "Fast":     style = dict(style); style["tempo"] = 145
                elif t_choice == "Very Fast":style = dict(style); style["tempo"] = 175
                dur_map = {"16 bars":32,"32 bars":64,"64 bars":128,"128 bars":256}
                n = dur_map.get(self.dur_var.get(), 64)
                self._upd(30, "🎼 Composing melodies...")
                time.sleep(0.3)
                self._upd(60, "⚡ Applying style patterns...")
                notes, times, durs, vels, tempo = generate_music(style, n)
                time.sleep(0.2)
                self._upd(85, "💾 Rendering MIDI...")
                self.midi_path = save_midi(notes, times, durs, vels, tempo)
                self._upd(100, f"✅ Done!  Style: {prompt[:20]}  |  BPM: {tempo}  |  Notes: {len(notes)}")
                self.track_label.configure(text=f"♪  {prompt[:40]}  |  {tempo} BPM")
                self.gen_btn.configure(state="normal", bg=BLUE)
            except Exception as e:
                self.status_var.set(f"❌ {e}")
                self.gen_btn.configure(state="normal", bg=BLUE)

        threading.Thread(target=task, daemon=True).start()

    def _upd(self, pct, msg):
        self.progress['value'] = pct
        self.status_var.set(msg)
        self.update_idletasks()

    def _play(self):
        if not self.midi_path or not os.path.exists(self.midi_path):
            messagebox.showinfo("No Track","Generate a track first!"); return
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.load(self.midi_path)
                pygame.mixer.music.play()
                self.wave.start()
                self.status_var.set("▶ Playing...")
                return
            except: pass
        os.startfile(self.midi_path)
        self.wave.start()

    def _stop(self):
        if PYGAME_AVAILABLE:
            try: pygame.mixer.music.stop()
            except: pass
        self.wave.stop()
        self.status_var.set("⏹ Stopped")

    def _restart(self):
        self._stop(); self._play()

if __name__ == "__main__":
    app = SunoApp()
    app.mainloop()
