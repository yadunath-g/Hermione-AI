import os
import json
import re
import datetime
import threading
import time
import sys
from groq import Groq

# --- CONFIGURATION ---
# Note: Keep your API Key secure. For long-term use, consider an environment variable.
API_KEY = "" 
MEMORY_FILE = "hermione_memory.json"

try:
    client = Groq(api_key=API_KEY)
except Exception as e:
    print(f"CRITICAL_ERROR: {e}")

# --- HEX COLOR ENGINE ---
def hex_to_ansi(hex_code):
    hex_code = hex_code.lstrip('#')
    r, g, b = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
    return f"\033[38;2;{r};{g};{b}m"

GOLD, GLOW_AMBER, IVORY = hex_to_ansi("#D4AF37"), hex_to_ansi("#E6C07B"), hex_to_ansi("#F5E6C8")
DIM_GOLD, MUTED_GREY, WARM_WHITE = hex_to_ansi("#C9A66B"), hex_to_ansi("#888888"), hex_to_ansi("#FFF3D1")
DIM_GREY, RESET, BOLD = hex_to_ansi("#777777"), "\033[0m", "\033[1m"
AGENT_COLOR = GLOW_AMBER 
RED, YELLOW, BLUE, PURPLE = hex_to_ansi("#FF0000"), hex_to_ansi("#FFFF00"), hex_to_ansi("#0000FF"), hex_to_ansi("#A020F0")
GREEN, ORANGE, NEUTRAL = hex_to_ansi("#00FF00"), hex_to_ansi("#FFA500"), hex_to_ansi("#00FFFF")

# --- UI REFRESH ENGINE (Real-Time Clock) ---
def update_header():
    while True:
        # Format: DD-MM-YYYY | HH:MM:SS AM/PM
        now = datetime.datetime.now().strftime('%d-%m-%Y | %I:%M:%S %p')
        # \033[s (save cursor), \033[H (top-left), \033[K (clear line), \033[u (restore cursor)
        sys.stdout.write(f"\033[s\033[H\033[K{DIM_GREY}LOG_INIT: {now} | STATION-01 | AUTH: YADU{RESET}\033[u")
        sys.stdout.flush()
        time.sleep(1)

# --- CORE LOGIC ---
def format_reply(text):
    def color_picker(match):
        act = match.group(0).lower()
        if any(w in act for w in ["beam", "laugh", "happy", "smile", "nods"]): color = YELLOW
        elif any(w in act for w in ["sigh", "sad", "frown", "down", "disappointed"]): color = BLUE
        elif any(w in act for w in ["slams", "glares", "snaps", "sharp", "narrows"]): color = RED
        elif any(w in act for w in ["recoils", "sneers", "winces", "dreadful", "disgust"]): color = GREEN
        elif any(w in act for w in ["pales", "worried", "fear", "anxious", "bites"]): color = ORANGE
        elif any(w in act for w in ["gasps", "widens eyes", "surprised", "merlin", "glancing"]): color = PURPLE
        else: color = NEUTRAL
        return f"{color}{match.group(0)}{RESET}{IVORY}"
    return f"{IVORY}{re.sub(r'(\*.*?\*)', color_picker, text)}{RESET}"

def get_dynamic_instructions(user_input, profile):
    vault_ctx = "\n".join([f"- {item}" for item in profile["vault"]])
    return (
        f"\n[PERSONA: HERMIONE V1 — LOYAL PARTNER]"
        f"\n- IDENTITY: Yadu's closest friend. Emma Watson portrayal."
        f"\n- ANTI-HALLUCINATION: Do NOT invent meetings, schedules, or events. If it isn't in the Vault, it didn't happen."
        f"\n- TONE: Intelligent, grounded, strict but loyal. 2-4 line replies."
        f"\n- MANDATORY ACTION: Start with an action (*...*)."
        f"\n\n[VAULT_DATA]:\n{vault_ctx}"
    )

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                data = json.load(f)
                return data.get("profile", {}), [m for m in data.get("history", []) if m.get("role") != "system"]
        except: pass
    return {"vault": ["Neural Link established."]}, []

def save_memory(profile, history):
    with open(MEMORY_FILE, 'w') as f:
        json.dump({"profile": profile, "history": [m for m in history if m.get("role") != "system"]}, f, indent=4)

# --- THE INTERFACE ---
def chat_with_hermione():
    profile, history = load_memory()
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # Start Real-Time Clock
    clock_thread = threading.Thread(target=update_header, daemon=True)
    clock_thread.start()

    # Vertical Alignment - Space for clock at top
    print("\n") 
    print(f"{IVORY}═" * 70)
    print(f"  {GOLD}{BOLD}HOGWARTS {DIM_GOLD}ARCHIVES: {GLOW_AMBER}THE PENSIEVE {MUTED_GREY}v2.2{RESET}")
    print(f"{IVORY}═" * 70 + "\n")

    try:
        current_time_str = datetime.datetime.now().strftime('%I:%M %p')
        instr = get_dynamic_instructions("", profile)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": instr}, {"role": "user", "content": f"It is {current_time_str}. Sharp greeting."}],
            temperature=0.1
        )
        greet = completion.choices[0].message.content
        print(f"{AGENT_COLOR}{BOLD}Hermione:{RESET} {format_reply(greet)}")
        history.append({"role": "assistant", "content": greet})
    except:
        print(f"{AGENT_COLOR}{BOLD}Hermione:{RESET} {YELLOW}*Nods*{RESET} {IVORY}I'm here. Let's not waste time.{RESET}")

    while True:
        try:
            user_input = input(f"\n{WARM_WHITE}{BOLD}Yadu:{RESET} ")
            if user_input.lower() in ["exit", "quit", "goodbye"]:
                save_memory(profile, history)
                break
            
            instr = get_dynamic_instructions(user_input, profile)
            history.append({"role": "user", "content": user_input})
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": instr}, *history[-10:]],
                temperature=0.1
            )
            
            reply = completion.choices[0].message.content
            if not reply.strip().startswith("*"): reply = "*looks at you* " + reply
            print(f"\n{AGENT_COLOR}{BOLD}Hermione:{RESET} {format_reply(reply)}")
            history.append({"role": "assistant", "content": reply})
            save_memory(profile, history)
        except Exception as e:
            print(f"{RED}ERROR: {e}{RESET}")
            break

if __name__ == "__main__":
    chat_with_hermione()
