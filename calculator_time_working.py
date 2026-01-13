from datetime import datetime, timedelta
import re
import sys

# ===============================
# CONFIGURATION
# ===============================
DEFAULT_GOAL = timedelta(hours=8, minutes=30)

# 🎨 Couleurs ANSI
COLORS = {
    "reset": "\033[0m",
    "title": "\033[95m",
    "info": "\033[94m",
    "success": "\033[92m",
    "warning": "\033[93m",
    "error": "\033[91m",
}

# 🌍 Textes multilingues
TEXT = {
    "fr": {
        "title": "CALCULATEUR DE TEMPS DE TRAVAIL",
        "goal": "Objectif du jour",
        "arrival": "Heure d'arrivée",
        "add_pause": "Ajouter une pause ? (o/n)",
        "pause_start": "Début de pause",
        "pause_end": "Fin de pause",
        "results": "RÉSULTATS",
        "worked": "Temps travaillé",
        "remaining": "Temps restant",
        "departure": "Heure de départ",
        "done": "OBJECTIF ATTEINT !",
        "quit": "👋 Programme quitté.",
        "invalid": "❌ Saisie invalide",
        "now": "Heure actuelle",
        "pause_total": "Total pauses",

        "flex_gain": "Flex time gagné",
        "flex_loss": "Flex time perdu",

        "help_goal": "Formats: 8h30 | 8:30 | 8 | ENTER = 8h30",
        "help_time": "Formats: 7 | 7h | 07:30 | ENTER = heure actuelle",
        "help_pause": "Réponds o/oui pour ajouter une pause, n/non sinon",
    },
    "en": {
        "title": "WORK TIME CALCULATOR",
        "goal": "Daily goal",
        "arrival": "Arrival time",
        "add_pause": "Add a break? (y/n)",
        "pause_start": "Break start",
        "pause_end": "Break end",
        "results": "RESULTS",
        "worked": "Worked time",
        "remaining": "Remaining time",
        "departure": "Departure time",
        "done": "GOAL REACHED!",
        "quit": "👋 Program exited.",
        "invalid": "❌ Invalid input",
        "now": "Current time",
        "pause_total": "Total breaks",

        "flex_gain": "Flex time earned",
        "flex_loss": "Flex time lost",

        "help_goal": "Formats: 8h30 | 8:30 | 8 | ENTER = 8h30",
        "help_time": "Formats: 7 | 7h | 07:30 | ENTER = now",
        "help_pause": "Answer y/yes to add a break, n/no otherwise",
    },
}

HELP_GLOBAL = {
    "fr": """
AIDE GLOBALE
-------------
- Quitter : q | quit | exit | CTRL+C
- Aide : help ou ?
- Formats acceptés :
  7 | 7h | 07:30 | 8h30 | 8:30
""",
    "en": """
GLOBAL HELP
-------------
- Quit: q | quit | exit | CTRL+C
- Help: help or ?
- Accepted formats:
  7 | 7h | 07:30 | 8h30 | 8:30
"""
}

# ===============================
# OUTILS
# ===============================
def quit_check(value):
    if value.lower() in {"q", "quit", "exit"}:
        print(COLORS["warning"] + TEXT[LANG]["quit"] + COLORS["reset"])
        sys.exit(0)

def help_check(value, topic=None):
    if value.lower() in {"help", "?"}:
        print(COLORS["info"] + HELP_GLOBAL[LANG])
        if topic:
            print("👉 " + TEXT[LANG][topic])
        print(COLORS["reset"])
        return True
    return False

def input_safe(prompt, help_topic=None):
    while True:
        value = input(prompt).strip()
        quit_check(value)
        if help_check(value, help_topic):
            continue
        return value

# ===============================
# PARSING
# ===============================
def parse_time(user_input):
    s = re.sub(r"[h;,./\s]", ":", user_input.lower())
    s = re.sub(r":+", ":", s)

    if ":" not in s:
        s += ":00"

    h, m = map(int, s.split(":"))
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError

    return datetime.strptime(f"{h:02d}:{m:02d}", "%H:%M")

def get_time_input(label):
    while True:
        user_input = input_safe(
            f"{label} (ENTER = {datetime.now().strftime('%H:%M')}) : ",
            "help_time"
        )
        if user_input == "":
            return datetime.strptime(datetime.now().strftime("%H:%M"), "%H:%M")
        try:
            return parse_time(user_input)
        except ValueError:
            print(COLORS["error"] + TEXT[LANG]["invalid"] + COLORS["reset"])

def parse_duration(user_input):
    s = re.sub(r"[h;,./\s]", ":", user_input.lower())
    if ":" not in s:
        s += ":00"

    h, m = map(int, s.split(":"))
    if h < 0 or m < 0 or m >= 60:
        raise ValueError

    return timedelta(hours=h, minutes=m)

def get_duration_input(label, default):
    while True:
        user_input = input_safe(f"{label} [8h30] : ", "help_goal")
        if user_input == "":
            return default
        try:
            return parse_duration(user_input)
        except ValueError:
            print(COLORS["error"] + TEXT[LANG]["invalid"] + COLORS["reset"])

def format_td(td):
    minutes = int(td.total_seconds() // 60)
    sign = "-" if minutes < 0 else ""
    minutes = abs(minutes)
    return f"{sign}{minutes // 60:02d}h{minutes % 60:02d}"

# ===============================
# PROGRAMME PRINCIPAL
# ===============================
def main():
    global LANG

    lang = input("Language / Langue (fr/en) [fr] : ").strip().lower()
    LANG = lang if lang in TEXT else "fr"

    print(COLORS["title"] + "=" * 60)
    print(TEXT[LANG]["title"].center(60))
    print("=" * 60 + COLORS["reset"])

    work_goal = get_duration_input(TEXT[LANG]["goal"], DEFAULT_GOAL)
    arrival = get_time_input(TEXT[LANG]["arrival"])

    total_pause = timedelta()

    while True:
        add = input_safe(f"{TEXT[LANG]['add_pause']} : ", "help_pause").lower() or "n"
        if add in {"n", "no", "non"}:
            break
        if add in {"o", "y", "yes", "oui"}:
            start = get_time_input(TEXT[LANG]["pause_start"])
            end = get_time_input(TEXT[LANG]["pause_end"])
            if end > start:
                total_pause += (end - start)

    now = datetime.now()
    current = datetime.strptime(now.strftime("%H:%M"), "%H:%M")

    worked = (current - arrival) - total_pause
    remaining = work_goal - worked
    departure = arrival + work_goal + total_pause
    flex_time = worked - work_goal

    print(COLORS["info"] + "\n" + TEXT[LANG]["results"].center(60, "-") + COLORS["reset"])
    print(f"{TEXT[LANG]['now']:25}: {now.strftime('%H:%M')}")
    print(f"{TEXT[LANG]['worked']:25}: {format_td(worked)}")
    print(f"{TEXT[LANG]['pause_total']:25}: {format_td(total_pause)}")

    if remaining > timedelta(0):
        print(COLORS["warning"] + f"{TEXT[LANG]['remaining']:25}: {format_td(remaining)}")
        print(f"{TEXT[LANG]['departure']:25}: {departure.strftime('%H:%M')}" + COLORS["reset"])
    else:
        print(COLORS["success"] + TEXT[LANG]["done"])
        print(f"{TEXT[LANG]['departure']:25}: {departure.strftime('%H:%M')}")
        if flex_time > timedelta(0):
            print(f"{TEXT[LANG]['flex_gain']:25}: {format_td(flex_time)}")
        elif flex_time < timedelta(0):
            print(f"{TEXT[LANG]['flex_loss']:25}: {format_td(flex_time)}")
        print(COLORS["reset"], end="")

# ===============================
# LANCEMENT
# ===============================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + COLORS["warning"] + "👋 Bye !" + COLORS["reset"])
