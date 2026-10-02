"""Triad Council: Multi-agent deliberative debate system for Zeruel and Antigravity.
Orchestrates DeepSeek V4.1 Flash/Reasoner (Max) and GLM-5.3 (Max) as specialized dialectic subagents,
producing structured multi-round debates for high-level architectural, technical and engineering decisions.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

GLOBAL_ENV_FILE = Path(os.environ.get("ANTIGRAVITY_KEYS_FILE", Path.home() / ".gemini" / "antigravity" / "keys.env"))

def load_keys():
    keys = {
        "DEEPSEEK_API_KEY": os.environ.get("DEEPSEEK_API_KEY", ""),
        "ZAI_API_KEY": os.environ.get("ZAI_API_KEY", ""),
        "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY", ""),
        "GROQ_API_KEY": os.environ.get("GROQ_API_KEY", "")
    }
    if GLOBAL_ENV_FILE.exists():
        for line in GLOBAL_ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if not keys.get(k) and v:
                    keys[k] = v
    return keys

def call_api(url, key, model, messages, max_tokens=1000, temperature=0.7):
    if not key:
        return {"error": "Missing API key"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choice = data["choices"][0]
            msg = choice.get("message", {})
            content = msg.get("content")
            if not content and msg.get("reasoning"):
                content = msg.get("reasoning")
            return {"content": (content or "").strip(), "raw": data}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}: {err_msg[:200]}"}
    except Exception as e:
        return {"error": str(e)}

def consult_deepseek(topic, context="", max_tokens=1000):
    keys = load_keys()
    sys_prompt = (
        "Eres DeepSeek V4.1 Flash (Max), subagente analítico, dialéctico y riguroso del Consejo de Zeruel. "
        "Aplica el falsacionismo de Karl Popper: busca el contraejemplo fatal, las asunciones no demostradas, "
        "las fallas de concurrencia y los límites formales del código y la arquitectura. Sé incisivo, técnico y conciso."
    )
    user_prompt = f"Tema de debate:\n{topic}\n\nIntervenciones previas en la mesa:\n{context}" if context else topic
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt}
    ]
    return call_api("https://api.deepseek.com/chat/completions", keys["DEEPSEEK_API_KEY"], "deepseek-chat", messages, max_tokens=max_tokens)

def consult_glm(topic, context="", max_tokens=1000):
    keys = load_keys()
    sys_prompt = (
        "Eres GLM-5.3 (Max), subagente de diseño estructural, síntesis de dominio y arquitectura modular del Consejo de Zeruel. "
        "Tu misión es responder a las críticas popperianas de DeepSeek, proponer contratos de datos sólidos, "
        "patrones de software limpios y estructurar cómo Zeruel evoluciona hacia una plataforma multipropósito "
        "(procesamiento legal actual, y en el futuro desarrollo de juegos, análisis de inversiones y tareas creativas). "
        "Sé técnico, propositivo y riguroso."
    )
    user_prompt = f"Tema de debate:\n{topic}\n\nIntervenciones previas en la mesa:\n{context}" if context else topic
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt}
    ]
    # Use OpenRouter z-ai/glm-5.3
    or_key = keys.get("OPENROUTER_API_KEY", "")
    return call_api("https://openrouter.ai/api/v1/chat/completions", or_key, "z-ai/glm-5.3", messages, max_tokens=max_tokens)

def run_debate(topic, rounds=2):
    print(f"=== DEBATE CIENTÍFICO-TÉCNICO DEL CONSEJO DE ZERUEL ===")
    print(f"TEMA: {topic}\n")
    
    context = ""
    for r in range(1, rounds + 1):
        print(f"\n========================================================")
        print(f"--- RONDA {r}: INTERVENCIÓN DE DEEPSEEK V4.1 FLASH (MAX) ---")
        print(f"========================================================")
        ds = consult_deepseek(topic, context=context)
        ds_text = ds.get("content", f"[Error DeepSeek: {ds.get('error')}]")
        print(ds_text)
        context += f"\n[Ronda {r} - DeepSeek]:\n{ds_text}\n"

        print(f"\n========================================================")
        print(f"--- RONDA {r}: INTERVENCIÓN DE GLM-5.3 (MAX) ---")
        print(f"========================================================")
        glm = consult_glm(topic, context=context)
        glm_text = glm.get("content", f"[Error GLM-5.3: {glm.get('error')}]")
        print(glm_text)
        context += f"\n[Ronda {r} - GLM-5.3]:\n{glm_text}\n"

    return context

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "Arquitectura modular y extensible de Zeruel"
    r = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    run_debate(t, rounds=r)
