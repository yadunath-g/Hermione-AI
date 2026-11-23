# Hermione — AI-Powered Linux Terminal Assistant

A lightweight command-line AI assistant built in Python, powered by Llama-3.1-8b via the Groq API, featuring local JSON context persistence and sentiment-mapped 24-bit ANSI terminal formatting.

## Current Features
- **LLM Inference:** Fast conversational responses using `llama-3.1-8b-instant` via the Groq Cloud API.
- **Aura Engine (Terminal UI):** Maps response sentiment to 24-bit TrueColor ANSI terminal styling with time-aware session greetings.
- **Persistent Context:** Stores conversation history and user context locally in a structured JSON file (`hermione_memory.json`).

## Tech Stack
- **Language:** Python 3
- **LLM API:** Groq Cloud API (`llama-3.1-8b-instant`)
- **Storage:** Local JSON

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yadunath-g/Hermione-AI.git
   cd Hermione-AI
