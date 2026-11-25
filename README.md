# Hermione — AI-Powered Linux Terminal Assistant

A lightweight command-line AI assistant built in Python, powered by `openai/gpt-oss-120b` via the Groq API, featuring local JSON context persistence, autonomous workspace actions, and sentiment-mapped 24-bit ANSI terminal formatting.

## Demo



https://github.com/user-attachments/assets/35b4ad4a-09a4-493e-b571-a4f40d7729cf



## Motivation

Switching from a Linux terminal workflow to a browser tab just to run a quick query breaks focus. I built **Hermione** to explore how fast and expressive a pure terminal-native assistant could feel—combining low-latency LLM inference via Groq, transparent local JSON memory, autonomous workspace actions, and sentiment-mapped 24-bit ANSI colors without heavy frontend overhead.

## Current Features
- **LLM Inference:** Fast conversational responses using `openai/gpt-oss-120b` (configurable via `HERMIONE_MODEL`) through the Groq Cloud API.
- **Autonomous `/agent` Mode:** Multi-step task execution inside a sandboxed workspace (`./hermione_workspace`) with `[y/N]` user confirmation prompts for file writes and app launches.
- **Aura Engine (Terminal UI):** Maps response sentiment to 24-bit TrueColor ANSI terminal styling with time-aware session greetings.
- **Persistent Context:** Stores conversation history, preferences, and `/remember` notes locally in a structured JSON file (`hermione_memory.json`).

## Tech Stack
- **Language:** Python 3
- **LLM API:** Groq Cloud API (`openai/gpt-oss-120b`)
- **Storage:** Local JSON (`hermione_memory.json`)

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yadunath-g/Hermione-AI.git
   cd Hermione-AI
