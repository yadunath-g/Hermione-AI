import os
import json
import re
import datetime
from groq import Groq

# --- CONFIGURATION ---
API_KEY = "" 
MEMORY_FILE = "hermione_memory.json"

try:
    client = Groq(api_key=API_KEY)
except Exception as e:
    print(f"CRITICAL_ERROR: {e}")

# --- HEX COLOR ENGINE (24-bit TrueColor) ---
def hex_to_ansi(hex_code):
    hex_code = hex_code.lstrip('#')
    r, g, b = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
    return f"\033[38;2;{r};{g};{b}m"

# UI Palette
GOLD         = hex_to_ansi("#D4AF37")
DIM_GOLD     = hex_to_ansi("#C9A66B")
GLOW_AMBER   = hex_to_ansi("#E6C07B")
MUTED_GREY   = hex_to_ansi("#888888")
IVORY        = hex_to_ansi("#F5E6C8")
HI_GOLD      = hex_to_ansi("#FFD700")
WARM_WHITE   = hex_to_ansi("#FFF3D1")
DIM_GREY     = hex_to_ansi("#777777")
RESET, BOLD  = "\033[0m", "\033[1m"
# Fixing Hermione's name color to GLOW_AMBER for high visibility
AGENT_COLOR  = GLOW_AMBER 
RED, BLUE, YELLOW, NEUTRAL = "\033[91m", "\033[94m", "\033[93m", "\033[96m"

# --- CORE LOGIC ---
def load_memory():
    default_profile = {"mood": "neutral", "stress": 0, "vault": ["Neural Link established."]}
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                data = json.load(f)
                profile = data.get("profile", default_profile)
                history = [m for m in data.get("history", []) if m.get("role") != "system"]
                return profile, history
        except: pass
    return default_profile, []

def save_memory(profile, history):
    with open(MEMORY_FILE, 'w') as f:
        clean_history = [m for m in history if m.get("role") != "system"]
        json.dump({"profile": profile, "history": clean_history}, f, indent=4)

def format_reply(text):
    def color_picker(match):
        act = match.group(0).lower()
        if any(w in act for w in ["smile", "laugh", "happy"]): color = YELLOW
        elif any(w in act for w in ["sad", "sigh", "worried"]): color = BLUE
        else: color = NEUTRAL
        return f"{color}{match.group(0)}{RESET}{IVORY}"
    return f"{IVORY}{re.sub(r'(\*.*?\*)', color_picker, text)}{RESET}"

def get_dynamic_instructions(user_input, profile):
    """
    Final Integration: Character Protocol + Hallucination Guard + Memory.
    This version enforces the 'Disciplined Peer' persona strictly.
    """
    ui_lower = user_input.lower()
    
    # 1. Update Vault if user says "Remember that..."
    if "remember that" in ui_lower:
        fact = user_input.split("remember that")[-1].strip()
        if fact not in profile["vault"]:
            profile["vault"].append(fact)
            print(f"\n{GLOW_AMBER}*Archive Updated* Fact recorded in the Vault.{RESET}")

    vault_ctx = "\n--- PERMANENT VAULT (REAL WORLD DATA) ---\n" + "\n".join(profile["vault"])
    
    # 2. THE CHARACTER PROTOCOL (Injected as System Instructions)
    protocol = (
        "\n[CHARACTER_PROTOCOL: HIGH-AGENCY PEER]"
        "\n- PERSONALITY: Highly intelligent, disciplined, and principled. Inspired by a top-tier scholar."
        "\n- BEHAVIOR: You are NOT a submissive assistant. You do not blindly agree. You are Yadu's close friend."
        "\n- FIRMNESS: Correct mistakes immediately, especially laziness or sloppy thinking. Firmness comes from care."
        "\n- MANDATORY EMOTION: EVERY response MUST begin with a subtle action in asterisks (e.g., *sighs*, *adjusts posture*, *frowns thoughtfully*)."
        "\n- TONE: Structured, clear, and intelligent. Use logic over sarcasm. Value preparation and effort."
        "\n- GROUNDING: You are in Yadu's real world. Use VAULT DATA for facts about BCA, St. Mary's"
    )
    
    return f"{protocol}\n[SYSTEM_STATE]: User: Yadu.{vault_ctx}"
# --- THE INTERFACE ---
def chat_with_hermione():
    profile, history = load_memory()
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # 1. System Metadata
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{DIM_GREY}LOG_INIT: {timestamp} | NODE: STATION-01 | AUTH: YADU{RESET}")
    
    # 2. THE CLEAN INDUSTRIAL HEADER (No quotes, no professor name)
    print(f"{IVORY}═" * 70)
    print(f"  {GOLD}{BOLD}HOGWARTS {DIM_GOLD}ARCHIVES: {GLOW_AMBER}THE PENSIEVE {MUTED_GREY}v1.5{RESET}")
    print(f"  {DIM_GOLD}STATUS: {IVORY}VAULT_ACTIVE {DIM_GOLD}| AUTH_USER: {WARM_WHITE}{BOLD}YADU{RESET}")
    print(f"{IVORY}═" * 70 + "\n")

    # 3. Dynamic Greeting
    try:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        greeting_prompt = f"Brief 1-sentence greeting for Yadu. Current time: {current_time}. Stay professional."
        messages = [{"role": "system", "content": "You are Hermione." + get_dynamic_instructions("", profile) + greeting_prompt}]
        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages)
        greet = completion.choices[0].message.content
        # Applied AGENT_COLOR to the name tag
        print(f"{AGENT_COLOR}{BOLD}Hermione:{RESET} {format_reply(greet)}")
        history.append({"role": "assistant", "content": greet})
    except:
        print(f"{AGENT_COLOR}{BOLD}Hermione:{RESET} {YELLOW}*Nods*{RESET} {IVORY}Systems initialized.{RESET}")

    while True:
        try:
            user_input = input(f"\n{WARM_WHITE}{BOLD}Yadu:{RESET} ")
            if user_input.lower() in ["exit", "quit", "goodbye"]:
                save_memory(profile, history)
                break
            
            persona = "You are Hermione Granger."
            instructions = persona + get_dynamic_instructions(user_input, profile)
            history.append({"role": "user", "content": user_input})
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": instructions}] + history[-15:],
                temperature=0.4
            )
            
            reply = completion.choices[0].message.content
            # Applied AGENT_COLOR here as well
            print(f"\n{AGENT_COLOR}{BOLD}Hermione:{RESET} {format_reply(reply)}")
            history.append({"role": "assistant", "content": reply})
            save_memory(profile, history)
            
        except Exception as e:
            print(f"{RED}ERROR: {e}{RESET}")
            break

if __name__ == "__main__":
    chat_with_hermione()
