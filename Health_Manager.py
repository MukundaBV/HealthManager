import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import secrets
import re

# ================= DESIGN CONFIG =================
WIDTH, HEIGHT = 1100, 660

C_BG      = "#0F172A"
C_NAV     = "#1E293B"
C_ACCENT  = "#6366F1"
C_CARD    = "#1E293B"
C_TEXT    = "#CBD5E1"
C_MUTED   = "#64748B"
C_SUCCESS = "#10B981"
C_DANGER  = "#EF4444"
C_WARN    = "#F59E0B"

EXERCISE_VISUALS = {
    "Running":         ("🏃", "#1a3a5c", "#2d6a9f"),
    "HIIT":            ("⚡", "#3a1a1a", "#9f2d2d"),
    "Cycling":         ("🚴", "#1a3a1a", "#2d9f5c"),
    "Swimming":        ("🏊", "#0a2233", "#1565c0"),
    "Jump Rope":       ("🪢", "#2a1a3a", "#7b2d9f"),
    "Walking":         ("🚶", "#1a2a1a", "#4a7c4e"),
    "Weight Training": ("🏋️", "#1a1a3a", "#3949ab"),
    "Yoga":            ("🧘", "#2a1a2a", "#8e44ad"),
    "Resistance":      ("💪", "#3a1a0a", "#bf5b17"),
    "Squats":          ("🦵", "#1a2a3a", "#1976d2"),
    "Pilates":         ("🤸", "#1a3a2a", "#2e7d32"),
    "Basketball":      ("🏀", "#3a2a0a", "#e65100"),
}

# ================= DATABASE =================
def get_db():
    return sqlite3.connect("Projectacc.db")

def create_tables():
    con = get_db()
    con.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, email TEXT UNIQUE,
        phone TEXT UNIQUE, password TEXT, gender TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS activity(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, age INTEGER,
        present_weight REAL, target_weight REAL,
        days INTEGER, calories INTEGER, week_no INTEGER DEFAULT 0)""")
    con.execute("""CREATE TABLE IF NOT EXISTS user_profile(
        username TEXT PRIMARY KEY,
        age INTEGER, height REAL, gender TEXT,
        activity_level TEXT, goal TEXT,
        current_weight REAL, target_weight REAL,
        time_weeks INTEGER)""")
    cur = con.cursor()
    cur.execute("PRAGMA table_info(activity)")
    cols = [r[1] for r in cur.fetchall()]
    if "week_no" not in cols:
        con.execute("ALTER TABLE activity ADD COLUMN week_no INTEGER DEFAULT 0")
    con.commit()
    con.close()

create_tables()

# ================= HELPERS =================
def back(win):
    win.destroy()
    root.deiconify()

def center_window(win, w, h):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

def styled_entry(parent, show="", width=20, var=None):
    kw = dict(font=("Helvetica", 11), show=show, bg="#0F172A", fg="white",
              insertbackground="white", highlightthickness=1,
              highlightbackground="#334155", relief="flat", width=width)
    return tk.Entry(parent, textvariable=var, **kw) if var else tk.Entry(parent, **kw)

def styled_btn(parent, text, command, color=None, **kw):
    c = color or C_ACCENT
    return tk.Button(parent, text=text, command=command, bg=c, fg="white",
                     font=("Helvetica", 11, "bold"), relief="flat", cursor="hand2",
                     activebackground=c, **kw)

def create_sidebar_layout(win, page_title):
    sidebar = tk.Frame(win, bg=C_NAV, width=235)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    lf = tk.Frame(sidebar, bg=C_NAV)
    lf.pack(pady=(22, 6), fill="x", padx=16)
    tk.Label(lf, text="⚕", font=("Helvetica", 26), fg=C_ACCENT, bg=C_NAV).pack()
    tk.Label(lf, text="HEALTH\nMANAGER", font=("Helvetica", 12, "bold"),
             fg="white", bg=C_NAV, justify="center").pack()
    tk.Frame(sidebar, bg=C_ACCENT, height=2).pack(fill="x", padx=16, pady=(4, 10))
    content = tk.Frame(win, bg=C_BG)
    content.pack(side="right", fill="both", expand=True)
    hdr = tk.Frame(content, bg="#1E293B", height=54)
    hdr.pack(fill="x"); hdr.pack_propagate(False)
    tk.Label(hdr, text=page_title, font=("Helvetica", 14, "bold"),
             bg="#1E293B", fg="white").pack(side="left", padx=24, pady=14)
    return sidebar, content

def make_scroll_frame(parent):
    cv = tk.Canvas(parent, bg=C_BG, highlightthickness=0)
    sb = ttk.Scrollbar(parent, orient="vertical", command=cv.yview)
    cv.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    cv.pack(side="left", fill="both", expand=True)
    inner = tk.Frame(cv, bg=C_BG)
    wid = cv.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
    cv.bind("<Configure>", lambda e: cv.itemconfig(wid, width=e.width))
    cv.bind_all("<MouseWheel>", lambda e: cv.yview_scroll(int(-1*(e.delta/120)), "units"))
    return inner

def make_exercise_visual(parent, key, w=220, h=130):
    emoji, dark, light = EXERCISE_VISUALS.get(key, ("🏃", "#1a3a5c", "#2d6a9f"))
    cv = tk.Canvas(parent, width=w, height=h, highlightthickness=0, bg=dark)
    cv.pack(fill="both", expand=True)
    for i in range(14):
        r = i / 14
        r1,g1,b1 = int(dark[1:3],16),int(dark[3:5],16),int(dark[5:7],16)
        r2,g2,b2 = int(light[1:3],16),int(light[3:5],16),int(light[5:7],16)
        col = f"#{int(r1+(r2-r1)*r):02x}{int(g1+(g2-g1)*r):02x}{int(b1+(b2-b1)*r):02x}"
        cv.create_rectangle(0, int(h*i/14), w, int(h*(i+1)/14), fill=col, outline="")
    cv.create_text(w//2, h//2, text=emoji, font=("Segoe UI Emoji", 38), fill="white")

# ================= CALORIE ENGINE =================
def compute_calorie_plan(age, gender, height_cm, weight_kg, target_weight, weeks, activity_level):
    if gender.lower() in ("male", "m"):
        bmr = 10*weight_kg + 6.25*height_cm - 5*age + 5
    else:
        bmr = 10*weight_kg + 6.25*height_cm - 5*age - 161
    factor = {"Sedentary":1.2, "Lightly Active":1.375, "Moderately Active":1.55,
              "Very Active":1.725, "Extremely Active":1.9}.get(activity_level, 1.55)
    tdee = bmr * factor
    diff = weight_kg - target_weight
    daily_delta = (diff * 7700) / (weeks * 7) if weeks > 0 else 0
    losing = diff > 0
    target_cal = max(1200, tdee - daily_delta) if losing else tdee + abs(daily_delta)
    return tdee, target_cal, daily_delta, losing, abs(diff)

# ================= HEALTH RECOMMENDATIONS WINDOW =================
def show_health_recommendations(parent_win, username, age, cur_w, tgt_w, weeks,
                                  target_cal, daily_def, gender="Male", height=170,
                                  activity="Moderately Active"):
    losing = cur_w > tgt_w
    diff   = abs(cur_w - tgt_w)

    win = tk.Toplevel(parent_win)
    win.title(f"Health Plan - {username}")
    win.configure(bg=C_BG)
    win.resizable(True, True)
    center_window(win, 1150, 740)
    win.minsize(900, 600)
    win.grab_set()

    hdr = tk.Frame(win, bg="#0D1B2A", height=60)
    hdr.pack(fill="x"); hdr.pack_propagate(False)
    lf = tk.Frame(hdr, bg="#0D1B2A"); lf.pack(side="left", padx=20, pady=12)
    tk.Label(lf, text="  HEALTH PLAN  ", font=("Helvetica", 8, "bold"),
             bg=C_ACCENT, fg="white", padx=6, pady=2).pack(side="left")
    tk.Label(lf, text=f"  {username}  |  {'Lose' if losing else 'Gain'} {diff:.1f} kg  |  "
                      f"{weeks} wks  |  {activity}",
             font=("Helvetica", 12, "bold"), bg="#0D1B2A", fg="white").pack(side="left", padx=8)
    tk.Button(hdr, text="X  CLOSE", command=win.destroy,
              bg=C_DANGER, fg="white", font=("Helvetica", 9, "bold"),
              relief="flat", cursor="hand2").pack(side="right", padx=20, pady=16, ipadx=12, ipady=3)

    sub = tk.Frame(win, bg="#131f35", height=26); sub.pack(fill="x"); sub.pack_propagate(False)
    protein_g = int(target_cal*0.30/4)
    carbs_g   = int(target_cal*0.45/4)
    fats_g    = int(target_cal*0.25/9)
    tk.Label(sub, font=("Helvetica", 8), bg="#131f35", fg="#94A3B8",
             text=f"  Target: {int(target_cal)} kcal/day  |  "
                  f"{'Deficit' if losing else 'Surplus'}: {int(daily_def)} kcal  |  "
                  f"Weekly: {diff/weeks:.2f} kg/wk  |  "
                  f"Protein {protein_g}g  Carbs {carbs_g}g  Fats {fats_g}g  |  "
                  f"Gender: {gender}  Height: {height}cm"
             ).pack(side="left", pady=4)

    tab_bar = tk.Frame(win, bg="#0D1B2A", height=42)
    tab_bar.pack(fill="x"); tab_bar.pack_propagate(False)
    body = tk.Frame(win, bg=C_BG); body.pack(fill="both", expand=True)

    tabs = {}
    tab_defs = [("exercises","  Exercises"),("diet","  Diet Plan"),
                ("calories","  Calories"),("tips","  Tips")]

    def switch_tab(key):
        for k, b in tabs.items():
            b.config(bg=C_ACCENT if k==key else "#0D1B2A",
                     fg="white" if k==key else C_MUTED)
        for w in body.winfo_children(): w.destroy()
        PAGES[key]()

    for key, label in tab_defs:
        b = tk.Button(tab_bar, text=label, font=("Helvetica", 9, "bold"),
                      bg="#0D1B2A", fg=C_MUTED, relief="flat", cursor="hand2",
                      activebackground=C_ACCENT, activeforeground="white",
                      command=lambda k=key: switch_tab(k), padx=16)
        b.pack(side="left", fill="y", padx=2)
        tabs[key] = b

    bc = int(target_cal*0.30); lc = int(target_cal*0.35)
    dc = int(target_cal*0.25); sc = int(target_cal*0.10)
    is_female = gender.lower() == "female"

    if losing:
        exlist = [
            ("Running","8 km/h","560 kcal/hr","Boosts cardio, burns fat fast","Running"),
            ("HIIT Training","High intensity","600 kcal/hr","Max burn in minimal time","HIIT"),
            ("Cycling","Moderate","500 kcal/hr","Low-impact, great for legs","Cycling"),
            ("Swimming","Laps","480 kcal/hr","Full body, easy on joints","Swimming"),
            ("Jump Rope","Fast","700 kcal/hr","Highest calorie burn per minute","Jump Rope"),
            ("Brisk Walking","6 km/h","300 kcal/hr","Beginner-friendly daily habit","Walking"),
            ("Weight Training","3x/week","350 kcal/hr","Builds muscle, raises metabolism","Weight Training"),
            ("Yoga","60 min","200 kcal/hr","Flexibility, stress relief, recovery","Yoga"),
        ]
        meals = [
            ("Breakfast", "Greek yogurt+berries+oats+chia" if is_female else "Oats+banana+boiled eggs+milk", f"{bc} kcal","#F59E0B"),
            ("Lunch",     "Grilled chicken salad+quinoa+avocado" if is_female else "Grilled chicken+brown rice+salad", f"{lc} kcal","#10B981"),
            ("Dinner",    "Steamed fish+sweet potato+greens" if is_female else "Steamed fish+vegetables+quinoa", f"{dc} kcal","#6366F1"),
            ("Snack",     "Almonds+apple/green smoothie" if is_female else "Almonds/Greek yogurt/protein bar", f"{sc} kcal","#06B6D4"),
        ]
        good = [("Broccoli","34 kcal/100g","🥦"),("Chicken Breast","165 kcal/100g","🍗"),
                ("Boiled Eggs","155 kcal/100g","🥚"),("Salmon","208 kcal/100g","🐟"),
                ("Sweet Potato","86 kcal/100g","🍠"),("Avocado","160 kcal/100g","🥑"),
                ("Blueberries","57 kcal/100g","🫐"),("Greek Yogurt","59 kcal/100g","🥛")]
        bad  = [("Burgers","600+ kcal","🍔"),("Pizza","570 kcal/2 slices","🍕"),
                ("Sugary Drinks","150 kcal/can","🥤"),("Donuts","350 kcal each","🍩"),
                ("French Fries","365 kcal/100g","🍟"),("Milk Chocolate","535 kcal/100g","🍫"),
                ("Alcohol","150 kcal/drink","🍺"),("Cupcakes","400 kcal each","🧁")]
    else:
        exlist = [
            ("Resistance Training","4x/week","350 kcal/hr","Core strength and muscle gain","Resistance"),
            ("Bodyweight Squats","3 sets","280 kcal/hr","Legs, glutes, functional strength","Squats"),
            ("Swimming","Leisure","350 kcal/hr","Full body toning, low impact","Swimming"),
            ("Cycling","Light","300 kcal/hr","Endurance and leg strength","Cycling"),
            ("Pilates","45 min","240 kcal/hr","Core, posture and balance","Pilates"),
            ("Basketball","60 min","400 kcal/hr","Fun cardio with skill training","Basketball"),
            ("Weight Training","Heavy","350 kcal/hr","Essential for mass building","Weight Training"),
            ("Walking","5 km/h","220 kcal/hr","Active recovery between workouts","Walking"),
        ]
        meals = [
            ("Breakfast", "Whole eggs+toast+peanut butter+banana" if is_female else "Eggs+whole grain toast+nuts+milk", f"{bc} kcal","#F59E0B"),
            ("Lunch",     "Brown rice+dal+paneer+salad" if is_female else "Rice+dal+chicken+paneer", f"{lc} kcal","#10B981"),
            ("Dinner",    "Pasta+tofu sauce+cheese+bread" if is_female else "Pasta+meat sauce+cheese+bread", f"{dc} kcal","#6366F1"),
            ("Snack",     "Protein shake+mixed nuts+dark chocolate" if is_female else "Peanut butter+banana+protein shake", f"{sc} kcal","#06B6D4"),
        ]
        good = [("Brown Rice","216 kcal/cup","🍚"),("Peanut Butter","588 kcal/100g","🥜"),
                ("Banana","89 kcal/100g","🍌"),("Lean Beef","250 kcal/100g","🥩"),
                ("Cheese","402 kcal/100g","🧀"),("Whole Eggs","155 kcal/100g","🥚"),
                ("Mixed Nuts","607 kcal/100g","🌰"),("Whole Grain Bread","247 kcal/100g","🍞")]
        bad  = [("Diet Drinks","Empty nutrition","🥤"),("Only Salads","Too low calorie","🥗"),
                ("Candy","No nutrients","🍬"),("Fried Junk","Bad fats only","🍟"),
                ("Alcohol","Empty calories","🍺"),("Bottled Juice","Sugar no fiber","🧃"),
                ("Processed Snacks","Low protein","🍪"),("Coffee Only","Appetite suppressor","☕")]

    tips = [
        ("Hydration","Drink 8-10 glasses of water daily to support metabolism and reduce hunger cues."),
        ("Sleep","7-8 hrs of quality sleep. Poor sleep raises cortisol and increases cravings."),
        ("Meal Timing","Eat every 3-4 hours to keep energy stable. Never skip breakfast."),
        ("Sodium","Reduce salt and avoid processed foods. Excess sodium causes water retention."),
        ("Tracking","Log meals and workouts daily. Awareness is the first step to change."),
        ("Movement","At least 30 minutes of activity every day — even light walking counts."),
        ("Stress","High cortisol causes fat storage. Meditate, breathe, take breaks."),
        ("Weigh-in","Log weight every Monday morning under the same conditions."),
    ]
    tip_icons = ["💧","😴","⏰","🧂","📝","🏃","🧘","⚖️"]

    def page_exercises():
        inner = make_scroll_frame(body)
        tk.Label(inner, text=f"{'Fat-Burning' if losing else 'Muscle-Building'} Exercises",
                 font=("Helvetica", 14, "bold"), bg=C_BG, fg="white").pack(anchor="w", padx=22, pady=(14,2))
        tk.Label(inner, text="45-60 min/day recommended",
                 font=("Helvetica", 9), bg=C_BG, fg=C_MUTED).pack(anchor="w", padx=22, pady=(0,12))
        grid = tk.Frame(inner, bg=C_BG); grid.pack(fill="x", padx=14, pady=6)
        for c in range(4): grid.columnconfigure(c, weight=1)
        for i, (name, detail, kcal, desc, key) in enumerate(exlist):
            r, c = divmod(i, 4)
            card = tk.Frame(grid, bg="#141f35", highlightthickness=1, highlightbackground="#2D3748")
            card.grid(row=r, column=c, padx=7, pady=7, sticky="nsew")
            vf = tk.Frame(card, bg="#0a1628", height=125); vf.pack(fill="x"); vf.pack_propagate(False)
            make_exercise_visual(vf, key)
            badge = tk.Frame(card, bg="#6366F1"); badge.pack(fill="x")
            tk.Label(badge, text=f"  {kcal}", font=("Helvetica", 8, "bold"),
                     bg="#6366F1", fg="white", pady=3).pack(side="left", padx=8)
            tk.Label(badge, text=detail, font=("Helvetica", 8),
                     bg="#6366F1", fg="#C7D2FE", pady=3).pack(side="right", padx=8)
            inf = tk.Frame(card, bg="#141f35", padx=9, pady=7); inf.pack(fill="x")
            tk.Label(inf, text=name, font=("Helvetica", 10, "bold"),
                     bg="#141f35", fg="white", anchor="w").pack(fill="x")
            tk.Label(inf, text=desc, font=("Helvetica", 8),
                     bg="#141f35", fg=C_MUTED, anchor="w", wraplength=175, justify="left").pack(fill="x")

    def page_diet():
        inner = make_scroll_frame(body)
        tk.Label(inner, text="Personalized Daily Meal Plan",
                 font=("Helvetica", 14, "bold"), bg=C_BG, fg="white").pack(anchor="w", padx=22, pady=(14,2))
        tk.Label(inner, text=f"For {gender} | {activity} | Daily target: {int(target_cal)} kcal",
                 font=("Helvetica", 9), bg=C_BG, fg=C_MUTED).pack(anchor="w", padx=22, pady=(0,12))
        mf = tk.Frame(inner, bg=C_BG); mf.pack(fill="x", padx=14, pady=(0,12))
        for c in range(4): mf.columnconfigure(c, weight=1)
        meal_icons = ["🌅","☀️","🌙","🍎"]
        for i, (meal, desc, kcal, color) in enumerate(meals):
            mc = tk.Frame(mf, bg="#141f35", highlightthickness=1, highlightbackground=color)
            mc.grid(row=0, column=i, padx=7, sticky="nsew")
            tk.Frame(mc, bg=color, height=4).pack(fill="x")
            ip = tk.Frame(mc, bg="#141f35", padx=12, pady=12); ip.pack(fill="both", expand=True)
            tk.Label(ip, text=f"{meal_icons[i]} {meal}", font=("Helvetica",10,"bold"),
                     bg="#141f35", fg=color).pack(anchor="w")
            tk.Label(ip, text=desc, font=("Helvetica",9), bg="#141f35", fg=C_TEXT,
                     wraplength=175, justify="left").pack(anchor="w", pady=5)
            tk.Label(ip, text=kcal, font=("Helvetica",11,"bold"), bg="#141f35", fg=color).pack(anchor="e")
        fb = tk.Frame(inner, bg=C_BG); fb.pack(fill="x", padx=14)
        fb.columnconfigure(0,weight=1); fb.columnconfigure(1,weight=1)
        for ci, (title, color, items) in enumerate([
            ("Recommended Foods", C_SUCCESS, good),
            ("Foods to Avoid",    C_DANGER,  bad)]):
            sec = tk.Frame(fb, bg="#141f35", highlightthickness=1, highlightbackground=color)
            sec.grid(row=0, column=ci, padx=7, pady=7, sticky="nsew")
            tk.Frame(sec, bg=color, height=3).pack(fill="x")
            tk.Label(sec, text=title, font=("Helvetica",10,"bold"),
                     bg="#141f35", fg=color, padx=13, pady=8).pack(anchor="w")
            for emoji, nm, val in items:
                rf = tk.Frame(sec, bg="#141f35", padx=13, pady=2); rf.pack(fill="x")
                tk.Label(rf, text=f"{emoji} {nm}", font=("Helvetica",9),
                         bg="#141f35", fg=C_TEXT, anchor="w").pack(side="left")
                tk.Label(rf, text=val, font=("Helvetica",8),
                         bg="#141f35", fg=C_MUTED).pack(side="right")
                tk.Frame(sec, bg="#1e2d45", height=1).pack(fill="x", padx=13)
            tk.Frame(sec, bg="#141f35", height=6).pack()

    def page_calories():
        inner = make_scroll_frame(body)
        tk.Label(inner, text="Personalized Calorie Breakdown",
                 font=("Helvetica",14,"bold"), bg=C_BG, fg="white").pack(anchor="w", padx=22, pady=(14,14))
        wrap = tk.Frame(inner, bg=C_BG); wrap.pack(fill="x", padx=14)
        wrap.columnconfigure(0,weight=2); wrap.columnconfigure(1,weight=1)
        left = tk.Frame(wrap, bg="#141f35", highlightthickness=1, highlightbackground="#2D3748")
        left.grid(row=0, column=0, padx=(0,7), sticky="nsew")
        tk.Frame(left, bg=C_ACCENT, height=3).pack(fill="x")
        tdee, _, _, _, _ = compute_calorie_plan(age, gender, height, cur_w, tgt_w, weeks, activity)
        rows = [
            ("BMR (Base Metabolic Rate)",  f"{int(tdee/1.375)} kcal", "#94A3B8", False),
            ("TDEE (Maintenance Calories)", f"{int(tdee)} kcal",       C_TEXT,    False),
            ("Daily Calorie Target",        f"{int(target_cal)} kcal", C_ACCENT,  True),
            (f"Daily {'Deficit' if losing else 'Surplus'}",
                                            f"{int(daily_def)} kcal",
                                            C_DANGER if losing else C_SUCCESS, True),
            ("Plan Duration",               f"{weeks} weeks",          C_WARN,    False),
            (f"Weight to {'Lose' if losing else 'Gain'}", f"{diff:.1f} kg", C_TEXT, False),
            ("Weekly Goal",                 f"{diff/weeks:.2f} kg/wk", "#8B5CF6", False),
            ("Activity Level",              activity,                   "#06B6D4", False),
        ]
        for lbl, val, col, big in rows:
            sf = tk.Frame(left, bg="#141f35", padx=18, pady=9); sf.pack(fill="x")
            tk.Label(sf, text=lbl, font=("Helvetica",9), bg="#141f35", fg=C_MUTED, anchor="w").pack(fill="x")
            tk.Label(sf, text=val, font=("Helvetica",15 if big else 12,"bold"),
                     bg="#141f35", fg=col, anchor="w").pack(fill="x")
            tk.Frame(left, bg="#1e2d45", height=1).pack(fill="x", padx=14)
        right = tk.Frame(wrap, bg="#141f35", highlightthickness=1, highlightbackground="#2D3748")
        right.grid(row=0, column=1, padx=(7,0), sticky="nsew")
        tk.Frame(right, bg=C_WARN, height=3).pack(fill="x")
        tk.Label(right, text="Macronutrients", font=("Helvetica",11,"bold"),
                 bg="#141f35", fg="white", padx=18, pady=12).pack(anchor="w")
        pg = int(target_cal*0.30/4)
        cg = int(target_cal*0.45/4)
        fg2 = int(target_cal*0.25/9)
        mx = max(pg, cg, fg2)
        for nm, grams, pct, col, v in [
            ("Protein",f"{pg}g/day","30%","#6366F1",pg),
            ("Carbohydrates",f"{cg}g/day","45%","#10B981",cg),
            ("Healthy Fats",f"{fg2}g/day","25%",C_WARN,fg2)]:
            mf2 = tk.Frame(right, bg="#141f35", padx=16, pady=9); mf2.pack(fill="x")
            tr = tk.Frame(mf2, bg="#141f35"); tr.pack(fill="x")
            tk.Label(tr, text=nm, font=("Helvetica",9,"bold"), bg="#141f35", fg=col).pack(side="left")
            tk.Label(tr, text=f"{grams} ({pct})", font=("Helvetica",8), bg="#141f35", fg=C_MUTED).pack(side="right")
            bg2 = tk.Frame(mf2, bg="#0F172A", height=8); bg2.pack(fill="x", pady=(4,0))
            tk.Frame(bg2, bg=col, height=8).place(x=0, y=0, relwidth=v/mx, height=8)

    def page_tips():
        inner = make_scroll_frame(body)
        tk.Label(inner, text="Health and Lifestyle Tips",
                 font=("Helvetica",14,"bold"), bg=C_BG, fg="white").pack(anchor="w", padx=22, pady=(14,2))
        tk.Label(inner, text="Small habits that compound into big results",
                 font=("Helvetica",9), bg=C_BG, fg=C_MUTED).pack(anchor="w", padx=22, pady=(0,12))
        grid = tk.Frame(inner, bg=C_BG); grid.pack(fill="x", padx=14, pady=6)
        grid.columnconfigure(0,weight=1); grid.columnconfigure(1,weight=1)
        cols = [C_ACCENT,"#10B981",C_WARN,"#06B6D4","#8B5CF6",C_DANGER,"#EC4899","#14B8A6"]
        for i, (cat, tip) in enumerate(tips):
            r, c = divmod(i, 2)
            tc = tk.Frame(grid, bg="#141f35", highlightthickness=1, highlightbackground=cols[i])
            tc.grid(row=r, column=c, padx=7, pady=7, sticky="nsew")
            tf = tk.Frame(tc, bg="#141f35", padx=16, pady=14); tf.pack(fill="both", expand=True)
            ef = tk.Frame(tf, bg="#141f35"); ef.pack(fill="x")
            tk.Label(ef, text=tip_icons[i], font=("Helvetica",20),
                     bg="#141f35", fg=cols[i]).pack(side="left")
            tk.Label(ef, text=cat, font=("Helvetica",11,"bold"),
                     bg="#141f35", fg=cols[i]).pack(side="left", padx=8)
            tk.Label(tf, text=tip, font=("Helvetica",9), bg="#141f35", fg=C_TEXT,
                     wraplength=375, justify="left").pack(anchor="w", pady=(6,0))

    PAGES = {"exercises":page_exercises, "diet":page_diet,
             "calories":page_calories, "tips":page_tips}
    switch_tab("exercises")

# ================= FORGOT PASSWORD =================
def open_forgot_password():
    win = tk.Toplevel()
    win.title("Forgot Password")
    center_window(win, 480, 530)
    win.configure(bg=C_BG); win.resizable(False,False); win.grab_set()

    tk.Frame(win, bg=C_ACCENT, height=4).pack(fill="x")
    tk.Label(win, text="RESET PASSWORD", font=("Helvetica",15,"bold"),
             bg=C_BG, fg="white").pack(pady=20)

    card = tk.Frame(win, bg=C_CARD, padx=38, pady=28,
                    highlightthickness=1, highlightbackground="#2D3748")
    card.pack(fill="both", expand=True, padx=28, pady=(0,20))

    token_store = {}
    step1 = tk.Frame(card, bg=C_CARD)
    step2 = tk.Frame(card, bg=C_CARD)

    def show_step(n):
        step1.pack_forget(); step2.pack_forget()
        (step1 if n==1 else step2).pack(fill="both", expand=True)

    tk.Label(step1, text="Step 1 - Verify Your Email",
             font=("Helvetica",12,"bold"), bg=C_CARD, fg=C_ACCENT).pack(anchor="w", pady=(0,12))
    tk.Label(step1, text="Enter your registered email address:",
             bg=C_CARD, fg=C_TEXT, font=("Helvetica",10)).pack(anchor="w")
    em_e = styled_entry(step1, width=32)
    em_e.pack(pady=(5,0), ipady=8, fill="x"); em_e.focus()
    msg1 = tk.Label(step1, text="", bg=C_CARD, font=("Helvetica",9)); msg1.pack(pady=4)

    def verify_email():
        email = em_e.get().strip()
        if not email: msg1.config(text="Enter your email.", fg=C_DANGER); return
        con = get_db(); cur = con.cursor()
        cur.execute("SELECT username FROM users WHERE email=?", (email,))
        row = cur.fetchone(); con.close()
        if not row: msg1.config(text="Email not found.", fg=C_DANGER); return
        tok = secrets.token_hex(4).upper()
        token_store.update(token=tok, email=email, username=row[0])
        messagebox.showinfo("Reset Token",
            f"Your password reset token:\n\n   {tok}\n\n(In production this would be emailed)")
        msg1.config(text=f"Token generated for {email}", fg=C_SUCCESS)
        show_step(2)

    styled_btn(step1, "VERIFY EMAIL", verify_email).pack(pady=14, ipady=10, fill="x")

    tk.Label(step2, text="Step 2 - Enter Token & New Password",
             font=("Helvetica",12,"bold"), bg=C_CARD, fg=C_ACCENT).pack(anchor="w", pady=(0,12))

    tok_e = pw1_e = pw2_e = None
    for lbl, is_pw in [("Reset Token:", False),("New Password:", True),("Confirm Password:", True)]:
        tk.Label(step2, text=lbl, bg=C_CARD, fg=C_TEXT, font=("Helvetica",10)).pack(anchor="w")
        e = styled_entry(step2, show="*" if is_pw else "", width=32)
        e.pack(pady=(4,10), ipady=7, fill="x")
        if "Token" in lbl: tok_e = e
        elif "New" in lbl: pw1_e = e
        else: pw2_e = e

    str_lbl = tk.Label(step2, text="", bg=C_CARD, font=("Helvetica",9)); str_lbl.pack(anchor="w")

    def chk_str(ev=None):
        pw = pw1_e.get()
        s = sum([len(pw)>=8, bool(re.search(r'[A-Z]',pw)),
                 bool(re.search(r'[0-9]',pw)), bool(re.search(r'\W',pw))])
        levels = ["","Weak","Fair","Good","Strong"]
        str_lbl.config(text=f"Strength: {levels[s]}",
                       fg=[C_MUTED,C_DANGER,C_WARN,C_SUCCESS,C_SUCCESS][s])

    pw1_e.bind("<KeyRelease>", chk_str)
    msg2 = tk.Label(step2, text="", bg=C_CARD, font=("Helvetica",9)); msg2.pack(pady=4)

    def do_reset():
        if tok_e.get().strip().upper() != token_store.get("token",""):
            msg2.config(text="Invalid token.", fg=C_DANGER); return
        if pw1_e.get() != pw2_e.get():
            msg2.config(text="Passwords do not match.", fg=C_DANGER); return
        if len(pw1_e.get()) < 6:
            msg2.config(text="Min 6 characters required.", fg=C_DANGER); return
        con = get_db()
        con.execute("UPDATE users SET password=? WHERE email=?",
                    (pw1_e.get(), token_store["email"]))
        con.commit(); con.close()
        messagebox.showinfo("Success",
            f"Password updated for {token_store['username']}!\nPlease login with your new password.")
        win.destroy()

    styled_btn(step2, "RESET PASSWORD", do_reset, color=C_SUCCESS).pack(pady=10, ipady=10, fill="x")
    tk.Button(step2, text="Back", bg=C_CARD, fg=C_MUTED, font=("Helvetica",9),
              relief="flat", command=lambda: show_step(1)).pack()
    show_step(1)

# ================= CALORIE PROFILE POPUP =================
def open_calorie_profile_popup(parent_win, username, on_save_callback):
    win = tk.Toplevel(parent_win)
    win.title("Health Profile")
    center_window(win, 530, 610)
    win.configure(bg=C_BG); win.resizable(False,False); win.grab_set()

    tk.Frame(win, bg=C_ACCENT, height=4).pack(fill="x")
    tk.Label(win, text="Your Health Profile",
             font=("Helvetica",14,"bold"), bg=C_BG, fg="white").pack(pady=16)
    tk.Label(win, text="Complete this once — we will remember your details for future plans.",
             font=("Helvetica",9), bg=C_BG, fg=C_MUTED).pack()

    card = tk.Frame(win, bg=C_CARD, padx=32, pady=22)
    card.pack(fill="both", expand=True, padx=22, pady=14)

    age_v = tk.StringVar(); ht_v  = tk.StringVar(); cw_v = tk.StringVar()
    tw_v  = tk.StringVar(); wk_v  = tk.StringVar(value="8")
    gd_v  = tk.StringVar(value="Male")
    ac_v  = tk.StringVar(value="Moderately Active")
    gl_v  = tk.StringVar(value="Lose Weight")

    con = get_db(); cur = con.cursor()
    cur.execute("SELECT age,height,gender,activity_level,goal,current_weight,target_weight,time_weeks FROM user_profile WHERE username=?", (username,))
    ex = cur.fetchone(); con.close()
    if ex:
        if ex[0]: age_v.set(str(ex[0]))
        if ex[1]: ht_v.set(str(ex[1]))
        if ex[2]: gd_v.set(ex[2])
        if ex[3]: ac_v.set(ex[3])
        if ex[4]: gl_v.set(ex[4])
        if ex[5]: cw_v.set(str(ex[5]))
        if ex[6]: tw_v.set(str(ex[6]))
        if ex[7]: wk_v.set(str(ex[7]))

    def mrow(lbl, var, typ="entry", opts=None):
        rf = tk.Frame(card,bg=C_CARD); rf.pack(fill="x",pady=4)
        tk.Label(rf,text=lbl,bg=C_CARD,fg=C_TEXT,font=("Helvetica",10),width=22,anchor="w").pack(side="left")
        if typ=="combo":
            cb = ttk.Combobox(rf,textvariable=var,values=opts,state="readonly",font=("Helvetica",10),width=22)
            cb.pack(side="left",ipady=4); return cb
        e = styled_entry(rf,var=var,width=22); e.pack(side="left",ipady=6,padx=(8,0)); return e

    mrow("Age (years)", age_v)
    mrow("Height (cm)", ht_v)
    mrow("Current Weight (kg)", cw_v)
    mrow("Target Weight (kg)", tw_v)
    mrow("Time Span (weeks)", wk_v)
    mrow("Gender", gd_v, "combo", ["Male","Female","Other"])
    mrow("Activity Level", ac_v, "combo",
         ["Sedentary","Lightly Active","Moderately Active","Very Active","Extremely Active"])
    mrow("Goal", gl_v, "combo",
         ["Lose Weight","Gain Weight","Maintain Weight","Build Muscle"])

    msg = tk.Label(card,text="",bg=C_CARD,font=("Helvetica",9)); msg.pack(pady=4)

    def save():
        try:
            a  = int(age_v.get()); h  = float(ht_v.get())
            cw = float(cw_v.get()); tw = float(tw_v.get())
            wk = int(wk_v.get())
            if a<=0 or h<=0 or cw<=0 or wk<=0: raise ValueError
        except:
            msg.config(text="Fill all fields with valid numbers.", fg=C_DANGER); return
        con = get_db()
        con.execute("""INSERT OR REPLACE INTO user_profile
            (username,age,height,gender,activity_level,goal,current_weight,target_weight,time_weeks)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (username,a,h,gd_v.get(),ac_v.get(),gl_v.get(),cw,tw,wk))
        con.commit(); con.close()
        win.destroy(); on_save_callback()

    styled_btn(card,"SAVE & GENERATE MY PLAN",save,color=C_SUCCESS).pack(pady=12,ipady=10,fill="x")
    tk.Button(card,text="Skip for now",bg=C_CARD,fg=C_MUTED,font=("Helvetica",9),
              relief="flat",command=win.destroy).pack()

# ================= ADMIN LOGIN =================
def open_admin_login():
    w = tk.Toplevel()
    w.title("Admin Login")
    center_window(w, 400, 310)
    w.configure(bg=C_BG); w.resizable(False,False); w.grab_set()

    tk.Frame(w, bg=C_ACCENT, height=4).pack(fill="x")
    hdr = tk.Frame(w,bg="#0D1B2A",height=68); hdr.pack(fill="x"); hdr.pack_propagate(False)
    tk.Label(hdr,text="ADMIN ACCESS",font=("Helvetica",14,"bold"),
             bg="#0D1B2A",fg="white").pack(pady=20)

    card = tk.Frame(w,bg=C_CARD,padx=38,pady=28); card.pack(fill="both",expand=True,padx=22,pady=14)
    tk.Label(card,text="Admin Key",bg=C_CARD,fg=C_TEXT,font=("Helvetica",10),anchor="w").pack(fill="x")
    key_e = styled_entry(card,show="*",width=30)
    key_e.pack(pady=8,ipady=9,fill="x"); key_e.focus()
    msg = tk.Label(card,text="",bg=C_CARD,fg=C_DANGER,font=("Helvetica",9)); msg.pack()

    def verify():
        if key_e.get() == "admin123":
            w.destroy(); root.withdraw(); admin_dashboard()
        else:
            msg.config(text="Incorrect admin key."); key_e.delete(0,tk.END)

    key_e.bind("<Return>", lambda e: verify())
    styled_btn(card,"LOGIN",verify).pack(pady=14,ipady=10,fill="x")

# ================= ADMIN DASHBOARD =================
def admin_dashboard():
    win = tk.Toplevel()
    win.title("Admin Dashboard — Health Manager")
    center_window(win, 1300, 750)
    win.resizable(True, True); win.minsize(1000, 600); win.configure(bg=C_BG)

    # ── Sidebar ──────────────────────────────────────────────────────
    sidebar = tk.Frame(win, bg="#0D1B2A", width=200)
    sidebar.pack(side="left", fill="y"); sidebar.pack_propagate(False)

    tk.Label(sidebar, text="⚕", font=("Helvetica", 28), fg=C_ACCENT, bg="#0D1B2A").pack(pady=(18,2))
    tk.Label(sidebar, text="HEALTH\nMANAGER", font=("Helvetica", 10, "bold"),
             fg="white", bg="#0D1B2A", justify="center").pack()
    tk.Label(sidebar, text="Admin Panel", font=("Helvetica", 8),
             fg=C_ACCENT, bg="#0D1B2A").pack(pady=(2,8))
    tk.Frame(sidebar, bg=C_ACCENT, height=2).pack(fill="x", padx=16, pady=(0,12))

    # ── Main content area ─────────────────────────────────────────────
    content = tk.Frame(win, bg=C_BG)
    content.pack(side="right", fill="both", expand=True)

    # Top header bar
    topbar = tk.Frame(content, bg="#1E293B", height=50)
    topbar.pack(fill="x"); topbar.pack_propagate(False)
    tk.Label(topbar, text="User Management", font=("Helvetica", 13, "bold"),
             bg="#1E293B", fg="white").pack(side="left", padx=20, pady=12)
    tk.Button(topbar, text="LOGOUT", bg=C_DANGER, fg="white",
              font=("Helvetica", 9, "bold"), relief="flat", cursor="hand2",
              command=lambda: back(win)).pack(side="right", padx=16, pady=10, ipadx=12, ipady=3)

    # ── Stats cards row ───────────────────────────────────────────────
    stats_row = tk.Frame(content, bg=C_BG)
    stats_row.pack(fill="x", padx=16, pady=(10, 4))

    def build_stats():
        for w in stats_row.winfo_children(): w.destroy()
        con = get_db(); cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM users");                     total   = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT username) FROM activity");  active  = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE gender='Male'"); males   = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE gender='Female'"); females = cur.fetchone()[0]
        con.close()
        cards = [
            ("Total Users",    str(total),   C_ACCENT,  "#1a1f3a"),
            ("Active Users",   str(active),  C_SUCCESS, "#0f2a1f"),
            ("Male Users",     str(males),   "#06B6D4",  "#0a2030"),
            ("Female Users",   str(females), "#EC4899",  "#2a0a1f"),
        ]
        for i, (label, value, col, bg) in enumerate(cards):
            stats_row.columnconfigure(i, weight=1)
            cf = tk.Frame(stats_row, bg=bg, highlightthickness=1, highlightbackground=col)
            cf.grid(row=0, column=i, padx=5, sticky="ew")
            tk.Frame(cf, bg=col, height=3).pack(fill="x")
            inner = tk.Frame(cf, bg=bg, padx=12, pady=8); inner.pack(fill="x")
            tk.Label(inner, text=value, font=("Helvetica", 22, "bold"), bg=bg, fg=col).pack(anchor="w")
            tk.Label(inner, text=label, font=("Helvetica", 8),          bg=bg, fg=C_MUTED).pack(anchor="w")

    # ── Search bar ────────────────────────────────────────────────────
    search_row = tk.Frame(content, bg=C_BG)
    search_row.pack(fill="x", padx=16, pady=(4, 2))

    tk.Label(search_row, text="Search:", font=("Helvetica", 10),
             bg=C_BG, fg=C_TEXT).pack(side="left", padx=(0,6))
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_row, textvariable=search_var,
                            font=("Helvetica", 10), bg="#1E293B", fg="white",
                            insertbackground="white", relief="flat",
                            highlightthickness=1, highlightbackground="#334155", width=28)
    search_entry.pack(side="left", ipady=5, padx=(0,10))

    filter_var = tk.StringVar(value="All")
    tk.Label(search_row, text="Filter:", font=("Helvetica", 10),
             bg=C_BG, fg=C_TEXT).pack(side="left", padx=(4,6))
    filter_cb = ttk.Combobox(search_row, textvariable=filter_var,
                              values=["All","Male","Female","Other"],
                              state="readonly", font=("Helvetica", 10), width=10)
    filter_cb.pack(side="left", ipady=4)

    # ── Split pane: table LEFT, graph RIGHT ───────────────────────────
    split_pane = tk.Frame(content, bg=C_BG)
    split_pane.pack(fill="both", expand=True, padx=16, pady=(4, 0))
    split_pane.columnconfigure(0, weight=3)
    split_pane.columnconfigure(1, weight=2)
    split_pane.rowconfigure(0, weight=1)

    # ── LEFT: Treeview table ──────────────────────────────────────────
    tbl_outer = tk.Frame(split_pane, bg=C_BG)
    tbl_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
    tbl_outer.rowconfigure(0, weight=1); tbl_outer.columnconfigure(0, weight=1)

    style = ttk.Style(); style.theme_use("default")
    style.configure("Admin.Treeview",
                    background="#141f35", foreground=C_TEXT,
                    fieldbackground="#141f35", rowheight=28, font=("Helvetica", 9))
    style.configure("Admin.Treeview.Heading",
                    background="#0D1B2A", foreground=C_ACCENT,
                    font=("Helvetica", 9, "bold"), relief="flat")
    style.map("Admin.Treeview",
              background=[("selected", C_ACCENT)],
              foreground=[("selected", "white")])

    cols = ("ID", "Username", "Email", "Phone", "Gender", "Activity Data")
    col_widths = [38, 120, 180, 100, 68, 90]
    tree = ttk.Treeview(tbl_outer, columns=cols, show="headings",
                         height=14, style="Admin.Treeview", selectmode="browse")
    for c, w in zip(cols, col_widths):
        tree.heading(c, text=c, anchor="center")
        tree.column(c, width=w, anchor="center", minwidth=35)
    tree.tag_configure("even", background="#141f35")
    tree.tag_configure("odd",  background="#0f1a2e")

    vsb = ttk.Scrollbar(tbl_outer, orient="vertical",   command=tree.yview)
    hsb = ttk.Scrollbar(tbl_outer, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    # ── RIGHT: Inline user graph panel ───────────────────────────────
    graph_panel = tk.Frame(split_pane, bg="#0D1B2A",
                            highlightthickness=1, highlightbackground="#2D3748")
    graph_panel.grid(row=0, column=1, sticky="nsew")

    # Graph panel header
    gp_hdr = tk.Frame(graph_panel, bg="#0D1B2A")
    gp_hdr.pack(fill="x", padx=0)
    tk.Frame(gp_hdr, bg=C_ACCENT, height=3).pack(fill="x")
    gp_title_row = tk.Frame(gp_hdr, bg="#0D1B2A")
    gp_title_row.pack(fill="x", padx=12, pady=(8, 4))
    gp_title = tk.Label(gp_title_row, text="📊  User Weight Graph",
                         font=("Helvetica", 10, "bold"), bg="#0D1B2A", fg="white")
    gp_title.pack(side="left")
    gp_subtitle = tk.Label(gp_title_row, text="Select a user →",
                            font=("Helvetica", 8), bg="#0D1B2A", fg=C_MUTED)
    gp_subtitle.pack(side="right")

    # Info strip under graph header
    gp_info = tk.Frame(graph_panel, bg="#111827")
    gp_info.pack(fill="x")
    gp_name_lbl  = tk.Label(gp_info, text="—", font=("Helvetica", 9, "bold"),
                             bg="#111827", fg=C_ACCENT, padx=12, pady=4)
    gp_name_lbl.pack(side="left")
    gp_stats_lbl = tk.Label(gp_info, text="", font=("Helvetica", 8),
                             bg="#111827", fg=C_MUTED, pady=4)
    gp_stats_lbl.pack(side="left", padx=4)

    # Graph canvas holder
    gp_body = tk.Frame(graph_panel, bg="#0D1B2A")
    gp_body.pack(fill="both", expand=True)

    # Placeholder label
    gp_placeholder = tk.Label(gp_body,
        text="👆  Click any user\nin the table to\nview their weight\nprogress graph",
        font=("Helvetica", 11), bg="#0D1B2A", fg="#334155",
        justify="center")
    gp_placeholder.pack(expand=True)

    # Profile mini-cards strip at bottom of graph panel
    gp_profile_strip = tk.Frame(graph_panel, bg="#0D1B2A")
    gp_profile_strip.pack(fill="x", pady=(0, 4), padx=10)

    current_fig = [None]   # store ref to close old figure

    def render_user_graph(username, gender):
        """Draw the inline weight progress graph for the selected user."""
        # Clear old widgets
        for w in gp_body.winfo_children(): w.destroy()
        for w in gp_profile_strip.winfo_children(): w.destroy()
        if current_fig[0]:
            try: plt.close(current_fig[0])
            except: pass

        con = get_db(); cur = con.cursor()
        cur.execute(
            "SELECT week_no, present_weight, target_weight FROM activity "
            "WHERE username=? ORDER BY week_no ASC", (username,))
        rows = cur.fetchall()
        cur.execute(
            "SELECT age, height, current_weight, target_weight, goal, activity_level "
            "FROM user_profile WHERE username=?", (username,))
        prof = cur.fetchone()
        con.close()

        # Update header labels
        gp_title.config(text=f"📊  {username}'s Weight Graph")
        gp_subtitle.config(text=f"Gender: {gender}")
        gp_name_lbl.config(text=f"  {username}")

        if rows:
            wks = [r[0] for r in rows]
            wts = [r[1] for r in rows]
            tgts = [r[2] for r in rows]
            avg_w = sum(wts) / len(wts)
            delta = wts[-1] - wts[0] if len(wts) > 1 else 0
            gp_stats_lbl.config(
                text=f"  {len(rows)} entries  |  Avg: {avg_w:.1f}kg  |  "
                     f"{'▼' if delta < 0 else '▲'} {abs(delta):.1f}kg total",
                fg=C_SUCCESS if delta <= 0 else C_WARN)

            # --- Matplotlib chart ---
            fig, ax = plt.subplots(figsize=(4.6, 3.0))
            fig.patch.set_facecolor("#0D1B2A")
            ax.set_facecolor("#0a1220")

            x = list(range(len(wks)))
            labels = [f"Wk{w}" for w in wks]

            # Shaded area
            ax.fill_between(x, wts, alpha=0.15, color=C_ACCENT)
            # Actual weight line
            ax.plot(x, wts, marker='o', color=C_ACCENT, linewidth=2.2,
                    markersize=7, label="Weight", zorder=3)
            # Target weight line (dashed)
            if any(t and t > 0 for t in tgts):
                ax.plot(x, tgts, linestyle='--', color=C_WARN, linewidth=1.5,
                        alpha=0.7, label="Target", zorder=2)
                ax.legend(fontsize=7, facecolor="#0D1B2A", labelcolor=C_TEXT,
                          framealpha=0.6, loc="upper right")

            # Annotate each point
            for i, (wk_lbl, wt) in enumerate(zip(labels, wts)):
                ax.annotate(f"{wt}",
                    xy=(i, wt), xytext=(0, 9), textcoords="offset points",
                    ha='center', fontsize=7, color="#A5B4FC", fontweight='bold')

            ax.set_title(f"Weight History", fontsize=9, color="white",
                         pad=6, fontweight="bold")
            ax.set_ylabel("kg", fontsize=8, color=C_TEXT)
            ax.tick_params(colors=C_TEXT, labelsize=7)
            ax.set_xticks(x); ax.set_xticklabels(labels, color=C_TEXT, fontsize=7)
            ax.grid(True, linestyle='--', alpha=0.15, color="white")
            ax.spines['bottom'].set_color("#2D3748")
            ax.spines['left'].set_color("#2D3748")
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            fig.tight_layout(pad=1.2)

            current_fig[0] = fig
            canvas = FigureCanvasTkAgg(fig, master=gp_body)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=6)

        else:
            # No activity data
            gp_stats_lbl.config(text="  No activity data yet", fg=C_MUTED)
            no_data = tk.Frame(gp_body, bg="#0D1B2A")
            no_data.pack(expand=True, fill="both")
            tk.Label(no_data, text="📭", font=("Helvetica", 28),
                     bg="#0D1B2A", fg="#334155").pack(expand=True, pady=(30, 4))
            tk.Label(no_data, text="No weekly entries logged yet",
                     font=("Helvetica", 9), bg="#0D1B2A", fg=C_MUTED).pack()

        # ── Profile mini-strip ──
        if prof:
            age, ht, cw, tw, goal, act = prof
            mini_items = []
            if age:  mini_items.append(("Age", f"{age}y"))
            if ht:   mini_items.append(("Ht", f"{ht}cm"))
            if cw:   mini_items.append(("Curr", f"{cw}kg"))
            if tw:   mini_items.append(("Goal", f"{tw}kg"))
            if goal: mini_items.append(("Plan", goal.split()[0]))

            for lbl, val in mini_items:
                pf = tk.Frame(gp_profile_strip, bg="#111827",
                              highlightthickness=1, highlightbackground="#1E293B")
                pf.pack(side="left", padx=2, pady=2, ipadx=4, ipady=2)
                tk.Label(pf, text=lbl, font=("Helvetica", 6), bg="#111827", fg=C_MUTED).pack()
                tk.Label(pf, text=val, font=("Helvetica", 8, "bold"), bg="#111827", fg=C_TEXT).pack()

    # Status bar
    status_bar = tk.Frame(content, bg="#0D1B2A", height=24)
    status_bar.pack(fill="x"); status_bar.pack_propagate(False)
    status_lbl = tk.Label(status_bar, text="", font=("Helvetica", 8),
                          bg="#0D1B2A", fg=C_MUTED)
    status_lbl.pack(side="left", padx=12, pady=3)
    count_lbl  = tk.Label(status_bar, text="", font=("Helvetica", 8),
                          bg="#0D1B2A", fg=C_ACCENT)
    count_lbl.pack(side="right", padx=12, pady=3)

    # ── Internal data store ───────────────────────────────────────────
    all_users = []

    def load(search="", gender_filter="All"):
        nonlocal all_users
        tree.delete(*tree.get_children())
        con = get_db(); cur = con.cursor()
        cur.execute("SELECT id,username,email,phone,password,gender FROM users")
        all_users = cur.fetchall()
        cur.execute("SELECT username, COUNT(*) FROM activity GROUP BY username")
        act_map = {r[0]: r[1] for r in cur.fetchall()}
        con.close()

        shown = 0
        for i, r in enumerate(all_users):
            uid, uname, email, phone, _pw, ugender = r
            if search and search.lower() not in (uname+email+phone).lower(): continue
            if gender_filter != "All" and ugender != gender_filter: continue
            act_str = f"{act_map.get(uname, 0)} entries"
            tag = "even" if shown % 2 == 0 else "odd"
            tree.insert("", "end", values=(uid, uname, email, phone, ugender, act_str), tags=(tag,))
            shown += 1

        build_stats()
        count_lbl.config(text=f"Showing {shown} of {len(all_users)} users")
        status_lbl.config(text="Ready", fg=C_MUTED)

    def do_search(*_):
        load(search_var.get(), filter_var.get())

    search_var.trace_add("write", do_search)
    filter_cb.bind("<<ComboboxSelected>>", do_search)

    def get_sel():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a user from the table first.")
            return None
        uid = tree.item(sel[0])["values"][0]
        for u in all_users:
            if u[0] == uid: return u
        return None

    # ── Tree selection → update inline graph ─────────────────────────
    def on_tree_select(event=None):
        sel = tree.selection()
        if not sel: return
        uid = tree.item(sel[0])["values"][0]
        for u in all_users:
            if u[0] == uid:
                render_user_graph(u[1], u[5] or "—")
                break

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    # ── Add User ──────────────────────────────────────────────────────
    def add_user():
        dlg = tk.Toplevel(win); center_window(dlg, 440, 500)
        dlg.title("Add New User"); dlg.configure(bg=C_BG); dlg.grab_set()
        tk.Frame(dlg, bg=C_SUCCESS, height=4).pack(fill="x")
        tk.Label(dlg, text="Add New User", font=("Helvetica",14,"bold"),
                 bg=C_BG, fg="white").pack(pady=16)
        card = tk.Frame(dlg, bg=C_CARD, padx=30, pady=20)
        card.pack(fill="both", expand=True, padx=20, pady=(0,18))

        ev = {k: tk.StringVar() for k in ["username","email","phone","password"]}
        gv2 = tk.StringVar(value="Male")
        for lbl, key, pw in [("Username","username",False),("Email","email",False),
                               ("Phone","phone",False),("Password","password",True)]:
            tk.Label(card,text=lbl,bg=C_CARD,fg=C_TEXT,font=("Helvetica",10),anchor="w").pack(fill="x",pady=(8,0))
            e = styled_entry(card, show="*" if pw else "", var=ev[key], width=32)
            e.pack(fill="x", ipady=6, pady=(2,0))
        tk.Label(card,text="Gender",bg=C_CARD,fg=C_TEXT,font=("Helvetica",10),anchor="w").pack(fill="x",pady=(8,0))
        ttk.Combobox(card,textvariable=gv2,values=["Male","Female","Other"],
                     state="readonly",font=("Helvetica",10),width=30).pack(fill="x",ipady=4,pady=(2,0))
        msg_a = tk.Label(card,text="",bg=C_CARD,font=("Helvetica",9)); msg_a.pack(pady=5)

        def do_add():
            u,em,ph,pw2 = [ev[k].get().strip() for k in ["username","email","phone","password"]]
            if not all([u,em,ph,pw2]): msg_a.config(text="All fields required.",fg=C_DANGER); return
            try:
                con = get_db()
                con.execute("INSERT INTO users (username,email,phone,password,gender) VALUES (?,?,?,?,?)",
                            (u,em,ph,pw2,gv2.get()))
                con.commit(); con.close()
                status_lbl.config(text=f"User '{u}' added successfully.", fg=C_SUCCESS)
                dlg.destroy(); load(search_var.get(), filter_var.get())
            except sqlite3.IntegrityError:
                msg_a.config(text="Email or Phone already exists.", fg=C_DANGER)

        styled_btn(card,"ADD USER",do_add,color=C_SUCCESS).pack(pady=12,ipady=9,fill="x")

    # ── Update User ───────────────────────────────────────────────────
    def update_user():
        u = get_sel()
        if not u: return
        uid, uname, email, phone, stored_pw, ugender = u

        dlg = tk.Toplevel(win); center_window(dlg, 440, 520)
        dlg.title(f"Edit User — {uname}"); dlg.configure(bg=C_BG); dlg.grab_set()
        tk.Frame(dlg, bg=C_ACCENT, height=4).pack(fill="x")

        hf = tk.Frame(dlg, bg="#1a1f3a"); hf.pack(fill="x")
        tk.Label(hf, text=f"  Editing: {uname}", font=("Helvetica",12,"bold"),
                 bg="#1a1f3a", fg=C_ACCENT).pack(side="left", padx=18, pady=12)
        tk.Label(hf, text=f"ID: {uid}", font=("Helvetica",9),
                 bg="#1a1f3a", fg=C_MUTED).pack(side="right", padx=18)

        card = tk.Frame(dlg, bg=C_CARD, padx=30, pady=18)
        card.pack(fill="both", expand=True, padx=20, pady=(8,18))

        gv3 = tk.StringVar(value=ugender)
        ents3 = []
        for lbl, val in [("Username", uname),("Email", email),("Phone", phone)]:
            tk.Label(card,text=lbl,bg=C_CARD,fg=C_TEXT,font=("Helvetica",10),anchor="w").pack(fill="x",pady=(8,0))
            e = styled_entry(card, width=32); e.insert(0, val)
            e.pack(fill="x", ipady=6, pady=(2,0)); ents3.append(e)

        tk.Label(card,text="Gender",bg=C_CARD,fg=C_TEXT,font=("Helvetica",10),anchor="w").pack(fill="x",pady=(8,0))
        ttk.Combobox(card,textvariable=gv3,values=["Male","Female","Other"],
                     state="readonly",font=("Helvetica",10),width=30).pack(fill="x",ipady=4,pady=(2,0))

        tk.Frame(card, bg="#2D3748", height=1).pack(fill="x", pady=12)
        tk.Label(card,text="New Password  (leave blank to keep current)",
                 bg=C_CARD,fg=C_MUTED,font=("Helvetica",9),anchor="w").pack(fill="x")
        pw_e = styled_entry(card, show="*", width=32)
        pw_e.pack(fill="x", ipady=6, pady=(4,0))

        msg_u = tk.Label(card,text="",bg=C_CARD,font=("Helvetica",9)); msg_u.pack(pady=4)

        def do_update():
            new_u  = ents3[0].get().strip()
            new_em = ents3[1].get().strip()
            new_ph = ents3[2].get().strip()
            new_g  = gv3.get()
            new_pw = pw_e.get().strip()
            if not all([new_u, new_em, new_ph]):
                msg_u.config(text="Username / Email / Phone cannot be empty.", fg=C_DANGER); return
            final_pw = new_pw if new_pw else stored_pw
            try:
                con = get_db()
                con.execute("UPDATE users SET username=?,email=?,phone=?,gender=?,password=? WHERE id=?",
                            (new_u, new_em, new_ph, new_g, final_pw, uid))
                con.commit(); con.close()
                status_lbl.config(text=f"User '{new_u}' updated successfully.", fg=C_SUCCESS)
                dlg.destroy(); load(search_var.get(), filter_var.get())
            except sqlite3.IntegrityError:
                msg_u.config(text="Email or Phone already in use by another user.", fg=C_DANGER)

        styled_btn(card,"SAVE CHANGES",do_update,color=C_ACCENT).pack(pady=10,ipady=9,fill="x")
        tk.Button(card,text="Cancel",bg=C_CARD,fg=C_MUTED,font=("Helvetica",9),
                  relief="flat",command=dlg.destroy).pack()

    # ── Delete User ───────────────────────────────────────────────────
    def delete_user():
        u = get_sel()
        if not u: return
        if messagebox.askyesno("Confirm Delete",
                               f"Permanently delete user  '{u[1]}'?\n\nThis cannot be undone.",
                               icon="warning"):
            con = get_db()
            con.execute("DELETE FROM users WHERE id=?",    (u[0],))
            con.execute("DELETE FROM activity WHERE username=?", (u[1],))
            con.execute("DELETE FROM user_profile WHERE username=?", (u[1],))
            con.commit(); con.close()
            status_lbl.config(text=f"User '{u[1]}' deleted.", fg=C_DANGER)
            # Reset graph panel
            for w in gp_body.winfo_children(): w.destroy()
            for w in gp_profile_strip.winfo_children(): w.destroy()
            gp_title.config(text="📊  User Weight Graph")
            gp_subtitle.config(text="Select a user →")
            gp_name_lbl.config(text="—")
            gp_stats_lbl.config(text="")
            gp_placeholder2 = tk.Label(gp_body,
                text="👆  Click any user\nin the table to\nview their weight\nprogress graph",
                font=("Helvetica", 11), bg="#0D1B2A", fg="#334155", justify="center")
            gp_placeholder2.pack(expand=True)
            load(search_var.get(), filter_var.get())

    # ── View User Detail ──────────────────────────────────────────────
    def view_detail():
        u = get_sel()
        if not u: return
        uid, uname, email, phone, _pw, ugender = u

        dlg = tk.Toplevel(win); center_window(dlg, 780, 560)
        dlg.title(f"User Detail — {uname}"); dlg.configure(bg=C_BG); dlg.grab_set()

        hf = tk.Frame(dlg, bg="#0D1B2A"); hf.pack(fill="x")
        tk.Frame(hf, bg=C_ACCENT, height=4).pack(fill="x")
        ih = tk.Frame(hf, bg="#0D1B2A"); ih.pack(fill="x", padx=20, pady=12)
        tk.Label(ih, text=f"👤  {uname}", font=("Helvetica",14,"bold"),
                 bg="#0D1B2A", fg="white").pack(side="left")
        tk.Label(ih, text=f"ID: {uid}  |  {ugender}",
                 font=("Helvetica",9), bg="#0D1B2A", fg=C_MUTED).pack(side="right")

        body2 = tk.Frame(dlg, bg=C_BG); body2.pack(fill="both", expand=True, padx=16, pady=10)
        body2.columnconfigure(0, weight=1); body2.columnconfigure(1, weight=2)

        left = tk.Frame(body2, bg=C_CARD, highlightthickness=1, highlightbackground="#2D3748")
        left.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        tk.Frame(left, bg=C_ACCENT, height=3).pack(fill="x")
        tk.Label(left, text="Account Info", font=("Helvetica",10,"bold"),
                 bg=C_CARD, fg=C_ACCENT, padx=14, pady=8).pack(anchor="w")

        con = get_db(); cur = con.cursor()
        cur.execute("SELECT age,height,gender,activity_level,goal,current_weight,target_weight,time_weeks FROM user_profile WHERE username=?", (uname,))
        prof = cur.fetchone()
        cur.execute("SELECT week_no,present_weight FROM activity WHERE username=? ORDER BY week_no ASC", (uname,))
        act_data = cur.fetchall(); con.close()

        for label, val in [("Username", uname),("Email", email),("Phone", phone),
                            ("Gender", ugender),("Password", "●●●●●●●●  (hidden)")]:
            rf = tk.Frame(left, bg=C_CARD, padx=14, pady=5); rf.pack(fill="x")
            tk.Label(rf, text=label, font=("Helvetica",8), bg=C_CARD, fg=C_MUTED, width=12, anchor="w").pack(side="left")
            col = C_MUTED if label == "Password" else C_TEXT
            tk.Label(rf, text=str(val), font=("Helvetica",9,"bold"), bg=C_CARD, fg=col, anchor="w").pack(side="left")
            tk.Frame(left, bg="#2D3748", height=1).pack(fill="x", padx=14)

        if prof:
            tk.Label(left, text="Health Profile", font=("Helvetica",10,"bold"),
                     bg=C_CARD, fg=C_SUCCESS, padx=14, pady=(12,4)).pack(anchor="w")
            keys = ["Age","Height (cm)","Gender","Activity","Goal","Curr. Weight","Target Weight","Weeks"]
            for k, v in zip(keys, prof):
                if v is None: continue
                rf2 = tk.Frame(left, bg=C_CARD, padx=14, pady=4); rf2.pack(fill="x")
                tk.Label(rf2, text=k, font=("Helvetica",8), bg=C_CARD, fg=C_MUTED, width=14, anchor="w").pack(side="left")
                tk.Label(rf2, text=str(v), font=("Helvetica",9,"bold"), bg=C_CARD, fg=C_TEXT, anchor="w").pack(side="left")

        right = tk.Frame(body2, bg=C_CARD, highlightthickness=1, highlightbackground="#2D3748")
        right.grid(row=0, column=1, sticky="nsew")
        tk.Frame(right, bg=C_SUCCESS, height=3).pack(fill="x")
        tk.Label(right, text="Weight Progress", font=("Helvetica",10,"bold"),
                 bg=C_CARD, fg=C_SUCCESS, padx=14, pady=8).pack(anchor="w")

        if act_data:
            fig, ax = plt.subplots(figsize=(5.2, 3.2))
            fig.patch.set_facecolor("#1E293B"); ax.set_facecolor("#0F172A")
            wks = [f"Wk{r[0]}" for r in act_data]; wts = [r[1] for r in act_data]
            ax.plot(wks, wts, marker='o', color=C_ACCENT, linewidth=2.2, markersize=8)
            ax.fill_between(range(len(wks)), wts, alpha=0.18, color=C_ACCENT)
            for i,(wk,wt) in enumerate(zip(wks,wts)):
                ax.annotate(f"{wt}kg", xy=(i,wt), xytext=(0,10), textcoords="offset points",
                            ha='center', fontsize=8, color="#A5B4FC", fontweight='bold')
            ax.set_title(f"{uname} — Weight History", fontsize=10, color="white", pad=8, fontweight="bold")
            ax.set_ylabel("kg", fontsize=9, color=C_TEXT)
            ax.tick_params(colors=C_TEXT, labelsize=8)
            ax.set_xticks(range(len(wks))); ax.set_xticklabels(wks, color=C_TEXT, fontsize=8)
            ax.grid(True, linestyle='--', alpha=0.2, color="white"); fig.tight_layout()
            FigureCanvasTkAgg(fig, master=right).get_tk_widget().pack(fill="both", expand=True, padx=10, pady=8)
        else:
            tk.Label(right, text="No weekly data logged yet.",
                     font=("Helvetica",10), bg=C_CARD, fg=C_MUTED).pack(expand=True)

        tk.Button(dlg, text="CLOSE", bg=C_DANGER, fg="white",
                  font=("Helvetica",9,"bold"), relief="flat", cursor="hand2",
                  command=dlg.destroy).pack(pady=10, ipadx=20, ipady=5)

    # ── Sidebar action buttons ────────────────────────────────────────
    bk = dict(font=("Helvetica", 10), relief="flat", cursor="hand2", pady=2)
    tk.Label(sidebar, text="ACTIONS", font=("Helvetica",7,"bold"),
             bg="#0D1B2A", fg=C_MUTED).pack(anchor="w", padx=16, pady=(4,4))

    tk.Button(sidebar, text="  View Detail",    bg="#1E3A5F", fg="white", command=view_detail,  **bk).pack(fill="x", padx=12, pady=3, ipady=7)
    tk.Button(sidebar, text="  Add User",       bg=C_SUCCESS, fg="white", command=add_user,     **bk).pack(fill="x", padx=12, pady=3, ipady=7)
    tk.Button(sidebar, text="  Edit User",      bg="#475569",  fg="white", command=update_user, **bk).pack(fill="x", padx=12, pady=3, ipady=7)
    tk.Button(sidebar, text="  Delete User",    bg=C_DANGER,  fg="white", command=delete_user,  **bk).pack(fill="x", padx=12, pady=3, ipady=7)

    tk.Frame(sidebar, bg="#2D3748", height=1).pack(fill="x", padx=12, pady=8)
    tk.Label(sidebar, text="TABLE", font=("Helvetica",7,"bold"),
             bg="#0D1B2A", fg=C_MUTED).pack(anchor="w", padx=16, pady=(0,4))
    tk.Button(sidebar, text="  Refresh", bg="#334155", fg="white",
              command=lambda: load(search_var.get(), filter_var.get()), **bk).pack(fill="x", padx=12, pady=3, ipady=7)

    # Double-click row to view detail
    tree.bind("<Double-1>", lambda e: view_detail())

    load()

# ================= HOME PAGE =================
def open_home_page(current_window, gender, username):
    current_window.destroy()
    home = tk.Toplevel()
    home.title(f"Health Manager - {username}")
    center_window(home, 1100, 660)
    home.resizable(True,True); home.minsize(820,520); home.configure(bg=C_BG)

    sidebar, content_parent = create_sidebar_layout(home, f"Welcome, {username}")

    tk.Frame(sidebar,bg="#2D3748",height=1).pack(fill="x",padx=15)
    uf = tk.Frame(sidebar,bg=C_NAV,pady=10); uf.pack(fill="x",padx=10)
    tk.Label(uf,text="👤",font=("Helvetica",20),bg=C_NAV,fg=C_ACCENT).pack()
    tk.Label(uf,text=username,font=("Helvetica",10,"bold"),bg=C_NAV,fg="white").pack()
    tk.Label(uf,text=gender,font=("Helvetica",8),bg=C_NAV,fg=C_MUTED).pack()
    tk.Frame(sidebar,bg="#2D3748",height=1).pack(fill="x",padx=15,pady=8)

    right_area = tk.Frame(content_parent, bg=C_BG)
    right_area.pack(fill="both", expand=True)

    def clear():
        for w in right_area.winfo_children(): w.destroy()

    def get_profile():
        con = get_db(); cur = con.cursor()
        cur.execute("SELECT age,height,gender,activity_level,goal,current_weight,target_weight,time_weeks FROM user_profile WHERE username=?", (username,))
        row = cur.fetchone(); con.close(); return row

    def quick_check_calories():
        p = get_profile()
        if not p or not all(p):
            open_calorie_profile_popup(home, username, quick_check_calories); return
        age,ht,gd,act,goal,cw,tw,wk = p
        try:
            _, tc, dd, _, _ = compute_calorie_plan(age, gd, ht, cw, tw, wk, act)
            show_health_recommendations(home, username, age, cw, tw, wk, tc, dd, gd, ht, act)
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def show_cal():
        clear()
        p = get_profile()

        sc = tk.Canvas(right_area, bg=C_BG, highlightthickness=0)
        ssb = ttk.Scrollbar(right_area, orient="vertical", command=sc.yview)
        sc.configure(yscrollcommand=ssb.set)
        ssb.pack(side="right",fill="y"); sc.pack(side="left",fill="both",expand=True)
        wrap = tk.Frame(sc, bg=C_BG)
        sc.create_window((0,0), window=wrap, anchor="nw")
        wrap.bind("<Configure>", lambda e: sc.configure(scrollregion=sc.bbox("all")))
        sc.bind_all("<MouseWheel>", lambda e: sc.yview_scroll(int(-1*(e.delta/120)),"units"))

        card = tk.Frame(wrap, bg=C_CARD, padx=38, pady=32,
                        highlightthickness=1, highlightbackground="#2D3748")
        card.pack(expand=True, pady=26, padx=55, fill="x")

        th = tk.Frame(card,bg=C_CARD); th.pack(fill="x",pady=(0,18))
        tk.Label(th,text="CALORIE MANAGEMENT",font=("Helvetica",14,"bold"),
                 bg=C_CARD,fg=C_ACCENT).pack(side="left")
        tk.Button(th,text="Edit Profile",bg="#334155",fg=C_TEXT,font=("Helvetica",9),
                  relief="flat",cursor="hand2",
                  command=lambda: open_calorie_profile_popup(home,username,show_cal)
                  ).pack(side="right",ipadx=8,ipady=4)

        age_v = tk.StringVar(value=str(p[0]) if p and p[0] else "")
        ht_v  = tk.StringVar(value=str(p[1]) if p and p[1] else "")
        cw_v  = tk.StringVar(value=str(p[5]) if p and p[5] else "")
        tw_v  = tk.StringVar(value=str(p[6]) if p and p[6] else "")
        wk_v  = tk.StringVar(value=str(p[7]) if p and p[7] else "8")
        gd_v  = tk.StringVar(value=p[2]  if p and p[2]  else gender)
        ac_v  = tk.StringVar(value=p[3]  if p and p[3]  else "Moderately Active")

        gf = tk.Frame(card,bg=C_CARD); gf.pack(fill="x")
        gf.columnconfigure(0,weight=1); gf.columnconfigure(1,weight=1)

        def ge(parent, row, col, lbl, var, typ="entry", opts=None):
            f = tk.Frame(parent,bg=C_CARD); f.grid(row=row,column=col,padx=9,pady=6,sticky="ew")
            tk.Label(f,text=lbl,bg=C_CARD,fg=C_TEXT,font=("Helvetica",9),anchor="w").pack(fill="x")
            if typ == "combo":
                cb = ttk.Combobox(f,textvariable=var,values=opts,state="readonly",
                                  font=("Helvetica",10),width=20)
                cb.pack(ipady=4,fill="x"); return cb
            e = styled_entry(f,var=var); e.pack(ipady=6,fill="x"); return e

        ge(gf,0,0,"Age (years)",age_v)
        ge(gf,0,1,"Height (cm)",ht_v)
        ge(gf,1,0,"Current Weight (kg)",cw_v)
        ge(gf,1,1,"Target Weight (kg)",tw_v)
        ge(gf,2,0,"Time Span (weeks)",wk_v)
        ge(gf,2,1,"Gender",gd_v,"combo",["Male","Female","Other"])
        ge(gf,3,0,"Activity Level",ac_v,"combo",
           ["Sedentary","Lightly Active","Moderately Active","Very Active","Extremely Active"])

        res_box = tk.Frame(card,bg="#0F172A",highlightthickness=1,highlightbackground="#334155")
        res_box.pack(fill="x",pady=(14,0))
        res_lbl = tk.Label(res_box,
                           text="  Fill your details then click CHECK DIET PLAN to see your plan",
                           bg="#0F172A",fg=C_MUTED,font=("Helvetica",10),pady=10,justify="left")
        res_lbl.pack(anchor="w",padx=12)

        def check_diet():
            try:
                age = int(age_v.get()); ht = float(ht_v.get())
                cw  = float(cw_v.get()); tw = float(tw_v.get())
                wk  = int(wk_v.get());   gd = gd_v.get(); ac = ac_v.get()
                if wk<=0 or cw<=0 or ht<=0: raise ValueError
            except:
                messagebox.showerror("Input Error","Please fill all fields with valid numbers.")
                return
            con = get_db()
            con.execute("""INSERT OR REPLACE INTO user_profile
                (username,age,height,gender,activity_level,goal,current_weight,target_weight,time_weeks)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (username,age,ht,gd,ac,"Custom",cw,tw,wk))
            con.commit(); con.close()
            _, tc, dd, losing, diff = compute_calorie_plan(age,gd,ht,cw,tw,wk,ac)
            res_lbl.config(
                text=f"  Weight to {'lose' if losing else 'gain'}: {diff:.1f} kg   |   "
                     f"Target: {int(tc)} kcal/day   |   "
                     f"Daily {'deficit' if losing else 'surplus'}: {int(dd)} kcal",
                fg=C_SUCCESS)
            show_health_recommendations(home,username,age,cw,tw,wk,tc,dd,gd,ht,ac)

        styled_btn(card, "CHECK DIET PLAN  ->", check_diet, color=C_ACCENT
                   ).pack(pady=20, fill="x", ipady=13)

    def show_perf():
        clear()
        cv2 = tk.Canvas(right_area,bg=C_BG,highlightthickness=0)
        sb2 = ttk.Scrollbar(right_area,orient="vertical",command=cv2.yview)
        wrap = tk.Frame(cv2,bg=C_BG)
        wrap.bind("<Configure>",lambda e: cv2.configure(scrollregion=cv2.bbox("all")))
        cv2.create_window((0,0),window=wrap,anchor="nw")
        cv2.configure(yscrollcommand=sb2.set)
        cv2.pack(side="left",fill="both",expand=True,padx=28,pady=14)
        sb2.pack(side="right",fill="y")
        cv2.bind_all("<MouseWheel>",lambda e: cv2.yview_scroll(int(-1*(e.delta/120)),"units"))

        card = tk.Frame(wrap,bg=C_CARD,padx=32,pady=26,
                        highlightthickness=1,highlightbackground="#2D3748")
        card.pack(fill="x")
        tk.Label(card,text="WEEKLY LOG",font=("Helvetica",14,"bold"),
                 bg=C_CARD,fg=C_ACCENT).pack(anchor="w",pady=(0,14))

        p = get_profile()
        try: nw = max(1, int(p[7]) if p and p[7] else 8)
        except: nw = 8

        wf2 = tk.Frame(card,bg=C_CARD); wf2.pack(fill="x",pady=4)
        tk.Label(wf2,text="Select Week",bg=C_CARD,fg=C_TEXT,font=("Helvetica",10),
                 width=22,anchor="w").pack(side="left")
        wk_box = ttk.Combobox(wf2,values=[f"Week {i}" for i in range(1,nw+1)],
                               state="readonly",font=("Helvetica",11),width=18)
        wk_box.set("Week 1"); wk_box.pack(side="left",ipady=4)

        ef2 = tk.Frame(card,bg=C_CARD); ef2.pack(fill="x",pady=4)
        tk.Label(ef2,text="Weight (kg)",bg=C_CARD,fg=C_TEXT,font=("Helvetica",10),
                 width=22,anchor="w").pack(side="left")
        w_e = styled_entry(ef2,width=18); w_e.pack(side="left",ipady=6,padx=(8,0))

        st_lbl = tk.Label(card,text="",bg=C_CARD,font=("Helvetica",10)); st_lbl.pack(pady=4)

        lc3 = tk.Frame(wrap,bg=C_CARD,highlightthickness=1,highlightbackground="#2D3748")
        lc3.pack(fill="x",pady=10)
        tk.Label(lc3,text="Saved Entries",font=("Helvetica",11,"bold"),
                 bg=C_CARD,fg="white").pack(anchor="w",padx=14,pady=8)
        lcols = ("Week","Weight (kg)","Target (kg)","Age")
        lt = ttk.Treeview(lc3,columns=lcols,show="headings",height=5)
        for c in lcols: lt.heading(c,text=c); lt.column(c,width=168,anchor="center")
        lt.pack(fill="x",padx=14,pady=(0,12))

        def refresh():
            lt.delete(*lt.get_children())
            con = get_db(); cur = con.cursor()
            cur.execute("SELECT week_no,present_weight,target_weight,age FROM activity WHERE username=? ORDER BY week_no",(username,))
            for r in cur.fetchall(): lt.insert("","end",values=r)
            con.close()

        def save():
            try:
                p2 = get_profile()
                if not p2: messagebox.showerror("Missing","Complete your health profile first."); return
                ai = int(p2[0]); tf = float(p2[6]); wi = int(p2[7])
                wno = int(wk_box.get().split()[1]); wf3 = float(w_e.get().strip())
                con = get_db(); cur = con.cursor()
                cur.execute("SELECT id FROM activity WHERE username=? AND week_no=?",(username,wno))
                ex = cur.fetchone()
                if ex:
                    con.execute("UPDATE activity SET present_weight=?,age=?,target_weight=?,days=? WHERE id=?",
                                (wf3,ai,tf,wi*7,ex[0]))
                else:
                    con.execute("INSERT INTO activity (username,age,present_weight,target_weight,days,calories,week_no) VALUES (?,?,?,?,?,500,?)",
                                (username,ai,wf3,tf,wi*7,wno))
                con.commit(); con.close()
                st_lbl.config(text=f"Week {wno} - {wf3} kg saved",fg=C_SUCCESS)
                w_e.delete(0,tk.END); refresh()
            except ValueError: messagebox.showerror("Error","Enter a valid weight.")
            except Exception as ex: messagebox.showerror("DB Error",str(ex))

        styled_btn(card,"SAVE PROGRESS",save,color=C_SUCCESS).pack(pady=14,fill="x",ipady=9)
        refresh()

    def show_graph():
        clear()
        wrap = tk.Frame(right_area,bg=C_BG); wrap.pack(fill="both",expand=True,padx=22,pady=12)
        hd = tk.Frame(wrap,bg=C_BG); hd.pack(fill="x",pady=(0,8))
        tk.Label(hd,text="MY PERFORMANCE GRAPH",font=("Helvetica",14,"bold"),
                 bg=C_BG,fg="white").pack(side="left")
        tk.Button(hd,text="Refresh",bg=C_ACCENT,fg="white",font=("Helvetica",9,"bold"),
                  relief="flat",command=show_graph).pack(side="right",ipadx=8,ipady=4)
        gc = tk.Frame(wrap,bg=C_CARD,highlightthickness=1,highlightbackground="#2D3748")
        gc.pack(fill="both",expand=True)
        con = get_db(); cur = con.cursor()
        cur.execute("SELECT week_no,present_weight FROM activity WHERE username=? ORDER BY week_no ASC",(username,))
        data = cur.fetchall(); con.close()
        if not data:
            tk.Label(gc,text="No data yet.\nSave weekly entries first, then click Refresh.",
                     font=("Helvetica",12),bg=C_CARD,fg=C_MUTED,justify="center").pack(expand=True,pady=60)
            return
        wks = [f"Wk {r[0]}" for r in data]; wts = [r[1] for r in data]
        fig,ax = plt.subplots(figsize=(max(5,home.winfo_width()//100), max(3,home.winfo_height()//150)))
        fig.patch.set_facecolor("#1E293B"); ax.set_facecolor("#0F172A")
        ax.plot(wks,wts,marker='o',color=C_ACCENT,linewidth=2.5,markersize=9)
        ax.fill_between(range(len(wks)),wts,alpha=0.2,color=C_ACCENT)
        for i,(wk,wt) in enumerate(zip(wks,wts)):
            ax.annotate(f"{wt}kg",xy=(i,wt),xytext=(0,12),textcoords="offset points",
                        ha='center',fontsize=9,color="#A5B4FC",fontweight='bold')
        ax.set_title(f"Weekly Weight Progress - {username}",fontweight='bold',fontsize=12,color="white",pad=10)
        ax.set_ylabel("Weight (kg)",fontsize=10,color=C_TEXT)
        ax.set_xlabel("Week",fontsize=10,color=C_TEXT)
        ax.tick_params(colors=C_TEXT)
        ax.set_xticks(range(len(wks))); ax.set_xticklabels(wks,color=C_TEXT)
        ax.grid(True,linestyle='--',alpha=0.2,color="white"); fig.tight_layout()
        FigureCanvasTkAgg(fig,master=gc).get_tk_widget().pack(fill="both",expand=True,padx=14,pady=14)

    nav_btns = []
    def nav_click(fn, idx):
        for i,b in enumerate(nav_btns): b.config(bg=C_ACCENT if i==idx else "#2D3748")
        fn()

    for idx, (lbl, fn) in enumerate([("Calorie Mgmt",show_cal),
                                      ("Weekly Progress",show_perf),
                                      ("My Graph",show_graph)]):
        b = tk.Button(sidebar,text=lbl,font=("Helvetica",10),relief="flat",cursor="hand2",
                      fg="white",bg="#2D3748",command=lambda f=fn,i=idx: nav_click(f,i))
        b.pack(fill="x",pady=4,padx=15,ipady=9); nav_btns.append(b)

    tk.Frame(sidebar,bg="#2D3748",height=1).pack(fill="x",padx=15,pady=8)
    tk.Label(sidebar,text="QUICK TOOLS",font=("Helvetica",7,"bold"),
             bg=C_NAV,fg=C_MUTED).pack(anchor="w",padx=18)
    tk.Button(sidebar,text="Check Calories",font=("Helvetica",10,"bold"),
              relief="flat",cursor="hand2",fg="white",bg="#1a3a5c",
              command=quick_check_calories).pack(fill="x",pady=4,padx=15,ipady=9)
    tk.Button(sidebar,text="My Profile",font=("Helvetica",10),
              relief="flat",cursor="hand2",fg="white",bg="#2D3748",
              command=lambda: open_calorie_profile_popup(home,username,show_cal)
              ).pack(fill="x",pady=4,padx=15,ipady=9)
    tk.Button(sidebar,text="SIGN OUT",bg=C_DANGER,fg="white",
              font=("Helvetica",10,"bold"),relief="flat",
              command=lambda: back(home)).pack(side="bottom",fill="x",pady=18,padx=15,ipady=8)

    if not get_profile():
        home.after(400, lambda: open_calorie_profile_popup(home,username,show_cal))

    nav_click(show_cal, 0)

# ================= LOGIN =================
def open_login():
    root.withdraw()
    win = tk.Toplevel()
    win.title("User Login")
    center_window(win, 1100, 660)
    win.resizable(True,True); win.minsize(600,450); win.configure(bg=C_BG)

    lp = tk.Frame(win,bg=C_ACCENT,width=380); lp.pack(side="left",fill="y"); lp.pack_propagate(False)
    tk.Label(lp,text="⚕",font=("Helvetica",56),bg=C_ACCENT,fg="white").pack(pady=(72,8))
    tk.Label(lp,text="HEALTH\nMANAGER",font=("Helvetica",22,"bold"),
             bg=C_ACCENT,fg="white",justify="center").pack()
    tk.Label(lp,text="Your personal wellness companion\nTrack - Improve - Thrive",
             font=("Helvetica",11),bg=C_ACCENT,fg="#C7D2FE",justify="center").pack(pady=14)
    for f in ["Personalized calorie plans","Weight progress tracking",
               "Workout recommendations","Smart diet guidance"]:
        tk.Label(lp,text=f"  {f}",font=("Helvetica",10),bg=C_ACCENT,fg="#E0E7FF").pack(anchor="w",padx=38,pady=3)

    rs = tk.Frame(win,bg=C_BG); rs.pack(side="right",fill="both",expand=True)
    card = tk.Frame(rs,bg=C_CARD,padx=48,pady=42,
                    highlightthickness=1,highlightbackground="#2D3748")
    card.place(relx=0.5,rely=0.5,anchor="center")
    rs.bind("<Configure>",lambda e: card.place(relx=0.5,rely=0.5,anchor="center"))

    tk.Label(card,text="Welcome Back",font=("Helvetica",20,"bold"),fg="white",bg=C_CARD).pack(pady=(0,5))
    tk.Label(card,text="Sign in to continue your health journey",
             font=("Helvetica",10),fg=C_MUTED,bg=C_CARD).pack(pady=(0,20))

    u_e = p_e = None
    for lbl, is_pw in [("Username",False),("Password",True)]:
        tk.Label(card,text=lbl,bg=C_CARD,font=("Helvetica",10),fg=C_TEXT,anchor="w").pack(fill="x")
        e = styled_entry(card,show="*" if is_pw else "")
        e.pack(pady=(4,10),ipady=8,fill="x")
        if not is_pw: u_e = e
        else: p_e = e
    u_e.focus()

    msg = tk.Label(card,text="",bg=C_CARD,fg=C_DANGER,font=("Helvetica",9)); msg.pack(pady=(0,4))

    def do_login():
        con = get_db(); cur = con.cursor()
        cur.execute("SELECT username,gender FROM users WHERE username=? AND password=?",
                    (u_e.get(),p_e.get()))
        row = cur.fetchone(); con.close()
        if row: open_home_page(win,row[1],row[0])
        else: msg.config(text="Invalid username or password.")

    u_e.bind("<Return>",lambda e: do_login())
    p_e.bind("<Return>",lambda e: do_login())
    styled_btn(card,"SIGN IN",do_login).pack(pady=(6,4),ipady=11,fill="x")

    lnk = tk.Frame(card,bg=C_CARD); lnk.pack(fill="x",pady=6)
    tk.Button(lnk,text="Forgot Password?",bg=C_CARD,fg=C_WARN,
              font=("Helvetica",9),relief="flat",cursor="hand2",
              command=open_forgot_password).pack(side="left")
    tk.Button(lnk,text="Back to Register",bg=C_CARD,fg=C_MUTED,
              font=("Helvetica",9),relief="flat",command=lambda: back(win)).pack(side="right")

# ================= REGISTRATION =================
root = tk.Tk()
root.title("Health Manager - Create Account")
center_window(root, 1100, 660)
root.resizable(True,True); root.minsize(800,500); root.configure(bg=C_BG)

lp = tk.Frame(root,bg="#0D1B2A",width=380); lp.pack(side="left",fill="y"); lp.pack_propagate(False)
tk.Label(lp,text="⚕",font=("Helvetica",56),bg="#0D1B2A",fg=C_ACCENT).pack(pady=(62,8))
tk.Label(lp,text="HEALTH\nMANAGER",font=("Helvetica",22,"bold"),
         bg="#0D1B2A",fg="white",justify="center").pack()
tk.Label(lp,text="Start your transformation today",
         font=("Helvetica",11),bg="#0D1B2A",fg=C_MUTED,justify="center").pack(pady=8)
tk.Frame(lp,bg=C_ACCENT,height=2).pack(fill="x",padx=48,pady=14)
for icon,txt in [("🎯","Personalized calorie plans"),("📊","Visual progress tracking"),
                  ("🏃","Custom workout guides"),("🥗","Smart diet recommendations")]:
    pf = tk.Frame(lp,bg="#0D1B2A"); pf.pack(anchor="w",padx=38,pady=5)
    tk.Label(pf,text=icon,font=("Helvetica",13),bg="#0D1B2A").pack(side="left")
    tk.Label(pf,text=txt,font=("Helvetica",10),bg="#0D1B2A",fg=C_TEXT).pack(side="left",padx=7)

top_bar = tk.Frame(root,bg=C_BG)
top_bar.place(relx=1.0,x=-10,y=8,anchor="ne")
tk.Button(top_bar,text="Admin",command=open_admin_login,bg=C_NAV,fg=C_TEXT,
          font=("Helvetica",9),relief="flat",cursor="hand2").pack(side="right",ipadx=10,ipady=3)
tk.Button(top_bar,text="Login",command=open_login,bg=C_NAV,fg=C_TEXT,
          font=("Helvetica",9),relief="flat",cursor="hand2").pack(side="right",padx=6,ipadx=10,ipady=3)

rs = tk.Frame(root,bg=C_BG); rs.pack(side="right",fill="both",expand=True)
reg_card = tk.Frame(rs,bg=C_CARD,padx=42,pady=32,
                    highlightthickness=1,highlightbackground="#2D3748")
reg_card.place(relx=0.5,rely=0.5,anchor="center")
rs.bind("<Configure>",lambda e: reg_card.place(relx=0.5,rely=0.5,anchor="center"))

tk.Label(reg_card,text="Create Account",font=("Helvetica",20,"bold"),
         fg="white",bg=C_CARD).pack(pady=(0,4))
tk.Label(reg_card,text="Join your health journey today",
         font=("Helvetica",10),fg=C_MUTED,bg=C_CARD).pack(pady=(0,18))

ents = []
for lbl,is_pw in [("Username",False),("Email",False),("Phone",False),("Password",True)]:
    tk.Label(reg_card,text=lbl,bg=C_CARD,font=("Helvetica",10),fg=C_TEXT,anchor="w").pack(fill="x")
    e = styled_entry(reg_card,show="*" if is_pw else "")
    e.pack(pady=(4,9),ipady=7,fill="x"); ents.append(e)

gv = tk.StringVar(value="Male")
gf = tk.Frame(reg_card,bg=C_CARD); gf.pack(fill="x",pady=(0,9))
tk.Label(gf,text="Gender",bg=C_CARD,font=("Helvetica",10),fg=C_TEXT).pack(anchor="w")
ttk.Combobox(gf,textvariable=gv,values=["Male","Female","Other"],
             state="readonly",font=("Helvetica",11),width=28).pack(ipady=5,fill="x")

msg_reg = tk.Label(reg_card,text="",bg=C_CARD,fg=C_DANGER,font=("Helvetica",9)); msg_reg.pack()

def reg():
    u,em,ph,pw = [e.get().strip() for e in ents]; g = gv.get()
    if not all([u,em,ph,pw]):
        msg_reg.config(text="All fields are required."); return
    try:
        con = get_db()
        con.execute("INSERT INTO users (username,email,phone,password,gender) VALUES (?,?,?,?,?)",
                    (u,em,ph,pw,g))
        con.commit(); con.close()
        messagebox.showinfo("Success",f"Welcome {u}!\nAccount created. Please login.")
        for e in ents: e.delete(0,tk.END)
        open_login()
    except sqlite3.IntegrityError:
        msg_reg.config(text="Email or Phone already registered.")

styled_btn(reg_card,"CREATE ACCOUNT",reg,color=C_SUCCESS).pack(pady=10,ipady=10,fill="x")
tk.Button(reg_card,text="Already have an account? Login",bg=C_CARD,fg=C_ACCENT,
          font=("Helvetica",9),relief="flat",cursor="hand2",command=open_login).pack(pady=(0,10))

tk.Frame(reg_card,bg="#2D3748",height=1).pack(fill="x",pady=(4,8))
tk.Label(reg_card,text="Admin Access",bg=C_CARD,fg=C_MUTED,font=("Helvetica",8)).pack()
tk.Button(reg_card,text="Go to Admin Dashboard",
          command=open_admin_login,
          bg="#1E3A5F",fg="white",
          font=("Helvetica",10,"bold"),
          relief="flat",cursor="hand2",
          activebackground=C_ACCENT,activeforeground="white"
          ).pack(pady=(4,0),ipady=8,fill="x")

root.mainloop()