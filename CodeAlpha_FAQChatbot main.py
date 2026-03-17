import tkinter as tk
import threading
import time
import math
import random
import re

# ─── PASTE YOUR GEMINI API KEY HERE ──────────────────────────────
GEMINI_API_KEY = "AIzaSyAjLUIBM6G7rrurl4bDGj7emiCp6Rs8czI"

# ─── Gemini AI Setup ──────────────────────────────────────────────
try:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=(
            "You are NOVA, a friendly and knowledgeable AI assistant. "
            "Answer questions clearly and concisely. Use relevant emojis. "
            "Keep answers under 100 words unless more detail is needed. "
            "If asked about yourself, say you are NOVA by CodeAlpha."
        )
    )
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False

# ─── Offline NLP Fallback ─────────────────────────────────────────
SYNONYMS = {
    "big":      ["large","huge","giant","biggest","largest","greatest","massive"],
    "small":    ["tiny","little","smallest","shortest","least","minor"],
    "fast":     ["quick","speed","rapid","fastest","velocity","swift"],
    "make":     ["create","build","invent","develop","produce","construct"],
    "inventor": ["created","invented","made","developed","discovered","founded"],
    "capital":  ["city","headquarters","main","centre","center","seat"],
    "far":      ["distance","away","kilometres","miles","long","reach"],
    "old":      ["age","ancient","years","history","born","since"],
    "hot":      ["temperature","heat","warm","degrees","celsius"],
    "country":  ["nation","land","place","region","state","territory"],
    "explain":  ["what","describe","define","meaning","tell","about"],
    "work":     ["function","operate","process","mechanism","how","does"],
    "animal":   ["creature","beast","species","organism","wildlife","mammal"],
    "health":   ["medical","disease","sick","treatment","medicine","doctor"],
    "money":    ["economy","finance","currency","cost","price","pay","wealth"],
    "war":      ["battle","conflict","fight","military","army","soldier"],
    "language": ["speak","tongue","words","grammar","dialect","linguistic"],
}

def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

def expand(tokens):
    expanded = set(tokens)
    for token in tokens:
        for key, syns in SYNONYMS.items():
            if token == key or token in syns:
                expanded.add(key)
                expanded.update(syns)
    return expanded

def smart_score(query, question):
    q = expand(set(tokenize(query)))
    f = expand(set(tokenize(question)))
    if not q or not f: return 0.0
    return len(q & f) / math.sqrt(len(q) * len(f))

def find_best(user_input, faqs):
    best_score, best_answer = 0.0, None
    for entry in faqs:
        for q in entry["questions"]:
            score = smart_score(user_input, q)
            if score > best_score:
                best_score = score
                best_answer = entry["answer"]
    return (best_answer if best_score >= 0.10 else None)

FAQS = [
    {"questions":["how far is sun","distance sun earth","sun distance"],"answer":"☀️ The Sun is **149.6 million km** from Earth. Sunlight takes ~8 minutes to reach us!"},
    {"questions":["how far is moon","distance moon earth","moon distance"],"answer":"🌙 The Moon is ~**384,400 km** from Earth. Light takes just 1.3 seconds!"},
    {"questions":["largest planet","biggest planet","jupiter"],"answer":"🪐 **Jupiter** is the largest planet — over 1,300 Earths could fit inside it!"},
    {"questions":["speed of light","how fast is light","light speed"],"answer":"⚡ Speed of light = **299,792,458 m/s**. Nothing travels faster!"},
    {"questions":["what is black hole","black hole explain"],"answer":"🕳️ A **black hole** is where gravity is so extreme nothing escapes — not even light!"},
    {"questions":["what is dna","dna meaning","dna structure"],"answer":"🧬 **DNA** (Deoxyribonucleic Acid) carries genetic instructions — life's blueprint! Double helix structure."},
    {"questions":["what is ai","artificial intelligence","explain ai"],"answer":"🤖 **AI** simulates human intelligence — learning, reasoning, problem-solving. Powers chatbots, self-driving cars!"},
    {"questions":["what is python","python programming"],"answer":"🐍 **Python** — simple, powerful language. #1 for AI/ML, data science, web development!"},
    {"questions":["who invented telephone","alexander graham bell"],"answer":"📞 **Alexander Graham Bell** invented the telephone in **1876**!"},
    {"questions":["who invented light bulb","thomas edison"],"answer":"💡 **Thomas Edison** invented the practical light bulb in **1879**!"},
    {"questions":["how many bones","bones in body"],"answer":"💀 Adult humans have **206 bones**. Babies are born with ~270–300!"},
    {"questions":["capital of france","paris france"],"answer":"🗼 **Paris** is the capital of France — the 'City of Light'!"},
    {"questions":["capital of pakistan","islamabad"],"answer":"🇵🇰 **Islamabad** is Pakistan's capital since 1966!"},
    {"questions":["largest country","biggest country","russia"],"answer":"🗺️ **Russia** is the largest country at **17.1 million km²**!"},
    {"questions":["tallest mountain","mount everest","highest mountain"],"answer":"🏔️ **Mount Everest** = **8,848.86 m** above sea level!"},
    {"questions":["what is gravity","how gravity works"],"answer":"🍎 **Gravity** attracts objects with mass. Newton described it; Einstein explained it as spacetime curvature!"},
    {"questions":["what is photosynthesis","plants make food"],"answer":"🌿 **Photosynthesis**: plants use sunlight + water + CO₂ → glucose + oxygen!"},
    {"questions":["world population","how many people earth"],"answer":"👥 World population: ~**8.1 billion** (2024)!"},
    {"questions":["what is machine learning","ml explained"],"answer":"🧠 **Machine Learning** — algorithms learn patterns from data without explicit programming!"},
    {"questions":["who invented internet","internet history"],"answer":"🌐 **Tim Berners-Lee** invented the World Wide Web in **1989**!"},
    {"questions":["hello","hi","hey","greetings"],"answer":"👋 Hello! I'm **NOVA** — powered by Google Gemini AI. Ask me anything!"},
    {"questions":["thank you","thanks","thankyou"],"answer":"😊 You're welcome! Ask me anything else!"},
    {"questions":["who are you","what are you","nova"],"answer":"🤖 I'm **NOVA**, an AI chatbot powered by Google Gemini! Ask me anything!"},
    {"questions":["bye","goodbye","see you"],"answer":"👋 Goodbye! Come back anytime!"},
    {"questions":["joke","tell me joke","funny"],"answer":"😄 Why don't scientists trust atoms? **Because they make up everything!** 😂"},
]

SUGGESTIONS = [
    "What is artificial intelligence?",
    "How far is the Sun?",
    "Who invented telephone?",
    "What is a black hole?",
    "Tell me a joke!",
    "What is DNA?",
    "How many bones in body?",
    "What is Python?",
]

# ─── Colors ───────────────────────────────────────────────────────
BG_DEEP  = "#04050f"
PANEL    = "#0d1530"
PANEL2   = "#111c3a"
BORDER   = "#1a2a5e"
BORDER2  = "#0f1f4a"
BLUE     = "#2d6cdf"
BLUE2    = "#1a4fa8"
CYAN     = "#00d4ff"
SILVER   = "#8899bb"
SILVER2  = "#aabbd4"
WHITE    = "#e8eeff"
DIM      = "#2a3a5a"
USER_BG  = "#1a3a6a"
BOT_BG   = "#0d1e40"
GLOW     = "#0066ff"
TYPING_DELAY = 15

# ─── Starfield ────────────────────────────────────────────────────
class StarfieldCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=BG_DEEP, highlightthickness=0)
        self.stars = []
        self.after(100, self._init_stars)
        self._animate()

    def _init_stars(self):
        w = self.winfo_width() or 900
        h = self.winfo_height() or 740
        self.stars = [(random.randint(0,w), random.randint(0,h),
                       random.choice([1,1,2]), random.random()) for _ in range(140)]

    def _animate(self):
        self.delete("all")
        w = self.winfo_width() or 900
        h = self.winfo_height() or 740
        t = time.time()
        for x in range(0, w, 60):
            self.create_line(x,0,x,h,fill="#080f22",width=1)
        for y in range(0, h, 60):
            self.create_line(0,y,w,y,fill="#080f22",width=1)
        for i,(ox,oy,r,spd) in enumerate([(w*.15,h*.2,180,.3),(w*.85,h*.75,150,.2),(w*.5,h*.5,120,.4)]):
            p = 0.35+0.12*math.sin(t*spd+i)
            cr = int(r*p)
            self.create_oval(ox-cr,oy-cr,ox+cr,oy+cr,
                           fill=["#001a4a","#001233","#00102a"][i],outline="")
        for (x,y,sz,b) in self.stars:
            tw = 0.4+0.6*abs(math.sin(t*1.5+b*10))
            a = int(160*tw)
            self.create_oval(x-sz,y-sz,x+sz,y+sz,
                           fill=f"#{a:02x}{a:02x}{min(a+50,255):02x}",outline="")
        self.after(80, self._animate)

# ─── Main App ─────────────────────────────────────────────────────
class NOVAChatbot(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NOVA — AI Chatbot | CodeAlpha")
        self.geometry("920x740")
        self.configure(bg=BG_DEEP)
        self.resizable(True, True)
        self._build_ui()
        self.after(600, self._welcome)

    def _build_ui(self):
        self.bg = StarfieldCanvas(self)
        self.bg.place(x=0,y=0,relwidth=1,relheight=1)

        cont = tk.Frame(self, bg=PANEL)
        cont.place(relx=0.03,rely=0.025,relwidth=0.94,relheight=0.95)
        tk.Frame(cont, height=2, bg=CYAN).pack(fill="x")

        # Header
        hdr = tk.Frame(cont, bg=PANEL2)
        hdr.pack(fill="x")
        hl = tk.Frame(hdr, bg=PANEL2)
        hl.pack(side="left", padx=20, pady=14)
        self.dot_c = tk.Canvas(hl, width=14, height=14, bg=PANEL2, highlightthickness=0)
        self.dot_c.pack(side="left", padx=(0,10))
        self._pulse()
        tk.Label(hl, text="NOVA", font=("Courier",22,"bold"), bg=PANEL2, fg=CYAN).pack(side="left")

        # Show if Gemini is connected
        ai_status = "  ✦ Powered by Gemini AI" if GEMINI_AVAILABLE else "  ✦ Offline Mode"
        ai_color  = "#00ff88" if GEMINI_AVAILABLE else "#ffaa00"
        tk.Label(hl, text=ai_status, font=("Courier",10), bg=PANEL2, fg=ai_color).pack(side="left", pady=(4,0))

        hr = tk.Frame(hdr, bg=PANEL2)
        hr.pack(side="right", padx=20)
        tk.Label(hr, text="by CodeAlpha", font=("Courier",9), bg=PANEL2, fg=DIM).pack(pady=(6,0))
        self.status = tk.Label(hr, text="● ONLINE", font=("Courier",8,"bold"), bg=PANEL2, fg="#00ff88")
        self.status.pack()
        tk.Frame(cont, height=1, bg=BORDER).pack(fill="x")

        # Chips
        cf = tk.Frame(cont, bg=PANEL)
        cf.pack(fill="x", padx=16, pady=(10,4))
        tk.Label(cf, text="Try:", font=("Courier",8), bg=PANEL, fg=DIM).pack(side="left", padx=(4,8))
        for s in SUGGESTIONS[:5]:
            short = s[:24]+"..." if len(s)>24 else s
            tk.Button(cf, text=short, font=("Courier",8), bg=PANEL2, fg=SILVER2,
                      bd=0, cursor="hand2", padx=9, pady=4,
                      activebackground=BLUE2, activeforeground=CYAN,
                      command=lambda q=s: self._quick(q)).pack(side="left", padx=3)
        tk.Frame(cont, height=1, bg=BORDER2).pack(fill="x", padx=16, pady=(6,0))

        # Chat
        cc = tk.Frame(cont, bg=PANEL)
        cc.pack(fill="both", expand=True, padx=16, pady=(8,0))
        self.cv = tk.Canvas(cc, bg=PANEL, highlightthickness=0, bd=0)
        sb = tk.Scrollbar(cc, orient="vertical", command=self.cv.yview,
                          bg=PANEL, troughcolor=PANEL2, activebackground=BLUE)
        self.cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.cv.pack(side="left", fill="both", expand=True)
        self.cf = tk.Frame(self.cv, bg=PANEL)
        self.cw = self.cv.create_window((0,0), window=self.cf, anchor="nw")
        self.cf.bind("<Configure>", lambda e: self.cv.configure(scrollregion=self.cv.bbox("all")))
        self.cv.bind("<Configure>", lambda e: self.cv.itemconfig(self.cw, width=e.width))
        self.cv.bind_all("<MouseWheel>", lambda e: self.cv.yview_scroll(int(-1*(e.delta/120)),"units"))

        tk.Frame(cont, height=1, bg=BORDER).pack(fill="x", padx=16, pady=(8,0))

        # Input
        inf = tk.Frame(cont, bg=PANEL2)
        inf.pack(fill="x", padx=16, pady=(0,14))
        ib = tk.Frame(inf, bg=BORDER)
        ib.pack(fill="x", padx=0, pady=8)
        ii = tk.Frame(ib, bg=PANEL2)
        ii.pack(fill="x", padx=1, pady=1)
        self.ivar = tk.StringVar()
        self.ent = tk.Entry(ii, textvariable=self.ivar, font=("Courier",12),
                            bg=PANEL2, fg=WHITE, insertbackground=CYAN,
                            relief="flat", bd=0)
        self.ent.pack(side="left", fill="x", expand=True, padx=14, pady=12)
        self.ent.bind("<Return>", lambda e: self._send())
        self.sbtn = tk.Button(ii, text="  SEND ›  ", font=("Courier",10,"bold"),
                               bg=BLUE, fg=WHITE, bd=0, cursor="hand2",
                               padx=14, pady=8,
                               activebackground=CYAN, activeforeground=BG_DEEP,
                               command=self._send)
        self.sbtn.pack(side="right", padx=8, pady=4)
        tk.Frame(cont, height=2, bg=GLOW).pack(fill="x", side="bottom")
        self.ent.focus_set()

    def _pulse(self):
        self.dot_c.delete("all")
        sz = 4+int(2*abs(math.sin(time.time()*2)))
        self.dot_c.create_oval(7-sz,7-sz,7+sz,7+sz,fill=CYAN,outline="")
        self.after(100, self._pulse)

    def _quick(self, q):
        self.ivar.set(q)
        self._send()

    def _welcome(self):
        if GEMINI_AVAILABLE:
            msg = "👋 Hello! I'm **NOVA**, powered by **Google Gemini AI**.\n\nI can answer ANY question — science, history, tech, math, sports, movies, cooking, or anything else!\n\nJust ask me anything! ✨"
        else:
            msg = "👋 Hello! I'm **NOVA**.\n\n⚠️ Gemini AI not connected. Running in offline mode with FAQ database.\n\nPlease add your API key to the code to enable full AI!"
        self._bot(msg)

    def _send(self):
        text = self.ivar.get().strip()
        if not text: return
        self.ivar.set("")
        self._user(text)
        self.status.configure(text="● THINKING...", fg="#ffaa00")
        threading.Thread(target=self._respond, args=(text,), daemon=True).start()

    def _respond(self, text):
        if GEMINI_AVAILABLE:
            try:
                response = model.generate_content(text)
                answer = response.text
            except Exception as e:
                # Fallback to offline
                answer = find_best(text, FAQS)
                if not answer:
                    answer = f"⚠️ Gemini error: {str(e)[:80]}\n\nTry again or check your API key!"
        else:
            time.sleep(0.3)
            answer = find_best(text, FAQS)
            if not answer:
                answer = "🔍 I don't have that in my offline database. Add your Gemini API key for unlimited answers!"

        self.after(0, lambda: self._bot(answer))
        self.after(0, lambda: self.status.configure(text="● ONLINE", fg="#00ff88"))

    def _user(self, text):
        row = tk.Frame(self.cf, bg=PANEL)
        row.pack(fill="x", padx=12, pady=(6,2), anchor="e")
        bf = tk.Frame(row, bg=PANEL)
        bf.pack(side="right")
        tk.Label(bf, text="YOU", font=("Courier",7,"bold"), bg=PANEL, fg=CYAN).pack(anchor="e", padx=4)
        bub = tk.Frame(bf, bg=USER_BG)
        bub.pack(anchor="e")
        tk.Frame(bub, height=1, bg=CYAN).pack(fill="x")
        tk.Label(bub, text=text, font=("Courier",11), bg=USER_BG, fg=WHITE,
                 wraplength=520, justify="right", padx=14, pady=10).pack()
        tk.Frame(bub, height=1, bg=BLUE).pack(fill="x")
        self._scroll()

    def _bot(self, text):
        row = tk.Frame(self.cf, bg=PANEL)
        row.pack(fill="x", padx=12, pady=(6,2), anchor="w")
        bf = tk.Frame(row, bg=PANEL)
        bf.pack(side="left")
        tk.Label(bf, text="⬡ NOVA", font=("Courier",7,"bold"), bg=PANEL, fg=CYAN).pack(anchor="w", padx=4)
        bub = tk.Frame(bf, bg=BOT_BG)
        bub.pack(anchor="w")
        tk.Frame(bub, height=1, bg=CYAN).pack(fill="x")
        clean = text.replace("**","").replace("*","")
        lbl = tk.Label(bub, text="", font=("Courier",11), bg=BOT_BG, fg=SILVER2,
                       wraplength=540, justify="left", padx=14, pady=10)
        lbl.pack(anchor="w")
        tk.Frame(bub, height=1, bg=BLUE2).pack(fill="x")
        def typewrite(i=0):
            if i <= len(clean):
                lbl.configure(text=clean[:i])
                self._scroll()
                self.after(TYPING_DELAY, lambda: typewrite(i+1))
        typewrite()

    def _scroll(self):
        self.cv.update_idletasks()
        self.cv.yview_moveto(1.0)

if __name__ == "__main__":
    app = NOVAChatbot()
    app.mainloop()
