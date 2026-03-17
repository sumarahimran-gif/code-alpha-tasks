
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from googletrans import Translator, LANGUAGES
import pyperclip

# Try to import gTTS for text-to-speech
try:
    from gtts import gTTS
    import pygame
    import tempfile
    import os
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# ─── Color Palette ───────────────────────────────────────────────
BG_DARK    = "#0f0f1a"
BG_PANEL   = "#1a1a2e"
BG_INPUT   = "#16213e"
ACCENT     = "#e94560"
ACCENT2    = "#0f3460"
TEXT_MAIN  = "#eaeaea"
TEXT_DIM   = "#7a7a9a"
BORDER     = "#2a2a4a"

# ─── Language List ───────────────────────────────────────────────
LANG_LIST = ["Auto Detect"] + sorted([v.title() for v in LANGUAGES.values()])
LANG_CODE = {v.title(): k for k, v in LANGUAGES.items()}

def get_lang_code(name):
    if name == "Auto Detect":
        return "auto"
    return LANG_CODE.get(name, "en")

# ─── Translation Logic ───────────────────────────────────────────
translator = Translator()

def do_translate(text, src, dest, callback):
    def task():
        try:
            src_code  = get_lang_code(src)
            dest_code = get_lang_code(dest)
            result = translator.translate(text, src=src_code, dest=dest_code)
            callback(result.text, None)
        except Exception as e:
            callback(None, str(e))
    threading.Thread(target=task, daemon=True).start()

# ─── TTS Logic ───────────────────────────────────────────────────
def speak_text(text, lang_code):
    if not TTS_AVAILABLE:
        messagebox.showinfo("TTS Unavailable", "Install gTTS and pygame:\npip install gTTS pygame")
        return
    def task():
        try:
            tts = gTTS(text=text, lang=lang_code)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                tts.save(f.name)
                tmp = f.name
            pygame.mixer.init()
            pygame.mixer.music.load(tmp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pass
            os.unlink(tmp)
        except Exception as e:
            messagebox.showerror("TTS Error", str(e))
    threading.Thread(target=task, daemon=True).start()

# ─── Main App ────────────────────────────────────────────────────
class TranslatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌐 Language Translator — CodeAlpha")
        self.geometry("900x620")
        self.resizable(True, True)
        self.configure(bg=BG_DARK)
        self._build_ui()

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill="x", padx=30, pady=(25, 5))

        tk.Label(header, text="🌐", font=("Segoe UI Emoji", 28),
                 bg=BG_DARK, fg=ACCENT).pack(side="left")
        tk.Label(header, text="  Language Translator",
                 font=("Georgia", 22, "bold"),
                 bg=BG_DARK, fg=TEXT_MAIN).pack(side="left")
        tk.Label(header, text="  by CodeAlpha",
                 font=("Courier", 11),
                 bg=BG_DARK, fg=TEXT_DIM).pack(side="left", pady=(6, 0))

        sep = tk.Frame(self, height=1, bg=BORDER)
        sep.pack(fill="x", padx=30, pady=(10, 15))

        # ── Language Selectors ──────────────────────────────────
        sel_frame = tk.Frame(self, bg=BG_DARK)
        sel_frame.pack(fill="x", padx=30, pady=(0, 10))

        # Source
        src_box = tk.Frame(sel_frame, bg=BG_PANEL, bd=0, relief="flat")
        src_box.pack(side="left", expand=True, fill="x", padx=(0, 8))
        tk.Label(src_box, text="SOURCE LANGUAGE", font=("Courier", 8, "bold"),
                 bg=BG_PANEL, fg=ACCENT).pack(anchor="w", padx=10, pady=(8,2))
        self.src_var = tk.StringVar(value="Auto Detect")
        src_cb = ttk.Combobox(src_box, textvariable=self.src_var,
                              values=LANG_LIST, state="normal",
                              font=("Segoe UI", 11), width=25)
        src_cb.bind('<KeyRelease>', lambda e: self._filter_langs(e, src_cb, LANG_LIST))
        src_cb.pack(padx=10, pady=(0, 8), fill="x")
        self._style_combo(src_cb)

        # Swap button
        swap_btn = tk.Button(sel_frame, text="⇄", font=("Segoe UI", 16, "bold"),
                             bg=ACCENT2, fg=ACCENT, bd=0, cursor="hand2",
                             activebackground=ACCENT, activeforeground=BG_DARK,
                             command=self._swap_langs, width=3)
        swap_btn.pack(side="left", padx=4, pady=4)

        # Target
        tgt_box = tk.Frame(sel_frame, bg=BG_PANEL, bd=0)
        tgt_box.pack(side="left", expand=True, fill="x", padx=(8, 0))
        tk.Label(tgt_box, text="TARGET LANGUAGE", font=("Courier", 8, "bold"),
                 bg=BG_PANEL, fg=ACCENT).pack(anchor="w", padx=10, pady=(8,2))
        self.tgt_var = tk.StringVar(value="Spanish")
        tgt_cb = ttk.Combobox(tgt_box, textvariable=self.tgt_var,
                              values=LANG_LIST[1:], state="normal",
                              font=("Segoe UI", 11), width=25)
        tgt_cb.bind('<KeyRelease>', lambda e: self._filter_langs(e, tgt_cb, LANG_LIST[1:]))
        tgt_cb.pack(padx=10, pady=(0, 8), fill="x")
        self._style_combo(tgt_cb)

        # ── Text Areas ──────────────────────────────────────────
        text_frame = tk.Frame(self, bg=BG_DARK)
        text_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        # Input
        in_frame = tk.Frame(text_frame, bg=BG_PANEL)
        in_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(in_frame, text="INPUT TEXT", font=("Courier", 8, "bold"),
                 bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w", padx=10, pady=(8, 2))
        self.input_text = tk.Text(in_frame, height=10, wrap="word",
                                  font=("Segoe UI", 12),
                                  bg=BG_INPUT, fg=TEXT_MAIN,
                                  insertbackground=ACCENT,
                                  relief="flat", bd=0,
                                  selectbackground=ACCENT2,
                                  padx=10, pady=8)
        self.input_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Output
        out_frame = tk.Frame(text_frame, bg=BG_PANEL)
        out_frame.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(out_frame, text="TRANSLATED TEXT", font=("Courier", 8, "bold"),
                 bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w", padx=10, pady=(8, 2))
        self.output_text = tk.Text(out_frame, height=10, wrap="word",
                                   font=("Segoe UI", 12),
                                   bg=BG_INPUT, fg="#4ecdc4",
                                   relief="flat", bd=0, state="disabled",
                                   selectbackground=ACCENT2,
                                   padx=10, pady=8)
        self.output_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ── Buttons ─────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg=BG_DARK)
        btn_frame.pack(pady=(0, 20))

        self._btn(btn_frame, "  🔄  TRANSLATE", ACCENT, BG_DARK,
                  self._translate).pack(side="left", padx=6, ipadx=10, ipady=6)

        self._btn(btn_frame, "  📋  COPY", ACCENT2, TEXT_MAIN,
                  self._copy).pack(side="left", padx=6, ipadx=10, ipady=6)

        self._btn(btn_frame, "  🔊  SPEAK", ACCENT2, TEXT_MAIN,
                  self._speak).pack(side="left", padx=6, ipadx=10, ipady=6)

        self._btn(btn_frame, "  🗑️  CLEAR", "#2a2a4a", TEXT_DIM,
                  self._clear).pack(side="left", padx=6, ipadx=10, ipady=6)

        # ── Status Bar ──────────────────────────────────────────
        self.status_var = tk.StringVar(value="Ready ✓")
        tk.Label(self, textvariable=self.status_var,
                 font=("Courier", 9), bg=BG_DARK, fg=TEXT_DIM
                 ).pack(pady=(0, 8))

    def _btn(self, parent, text, bg, fg, cmd):
        return tk.Button(parent, text=text, font=("Segoe UI", 11, "bold"),
                         bg=bg, fg=fg, bd=0, cursor="hand2",
                         activebackground=ACCENT, activeforeground=BG_DARK,
                         command=cmd)

    def _style_combo(self, cb):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=BG_INPUT,
                        background=BG_INPUT,
                        foreground=TEXT_MAIN,
                        selectbackground=ACCENT2,
                        selectforeground=TEXT_MAIN,
                        bordercolor=BORDER,
                        arrowcolor=ACCENT)

    def _filter_langs(self, event, combobox, full_list):
        typed = combobox.get().lower()
        if typed == "":
            combobox['values'] = full_list
        else:
            filtered = [l for l in full_list if typed in l.lower()]
            combobox['values'] = filtered
        combobox.event_generate('<Down>')

    def _swap_langs(self):
        s, t = self.src_var.get(), self.tgt_var.get()
        if s != "Auto Detect":
            self.src_var.set(t)
            self.tgt_var.set(s)
            # Also swap text
            in_txt  = self.input_text.get("1.0", "end").strip()
            out_txt = self.output_text.get("1.0", "end").strip()
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", out_txt)
            self._set_output(in_txt)

    def _translate(self):
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Empty Input", "Please enter some text to translate.")
            return
        self.status_var.set("Translating…")
        self.update_idletasks()

        src = self.src_var.get()
        tgt = self.tgt_var.get()

        def on_done(result, error):
            if error:
                self.status_var.set(f"Error: {error}")
                messagebox.showerror("Translation Error", error)
            else:
                self._set_output(result)
                self.status_var.set("Translation complete ✓")

        do_translate(text, src, tgt, on_done)

    def _set_output(self, text):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.configure(state="disabled")

    def _copy(self):
        text = self.output_text.get("1.0", "end").strip()
        if text:
            pyperclip.copy(text)
            self.status_var.set("Copied to clipboard ✓")
        else:
            messagebox.showinfo("Nothing to Copy", "Translate something first!")

    def _speak(self):
        text = self.output_text.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("Nothing to Speak", "Translate something first!")
            return
        lang_code = get_lang_code(self.tgt_var.get())
        speak_text(text, lang_code)
        self.status_var.set("Speaking…")

    def _clear(self):
        self.input_text.delete("1.0", "end")
        self._set_output("")
        self.status_var.set("Cleared ✓")


if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()