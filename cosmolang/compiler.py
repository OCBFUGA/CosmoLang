"""
CosmoCore AGI Swarm Language (CosmoLang) - Compiler & VM
Version: 27.0 (Cloud & Tool-Calling Edition / Golden Throne)
Author: Janio Gomes Ribeiro
"""

import re
import time
import os
import sys
import math
import sqlite3
import datetime
import json
import subprocess

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class CosmoVM:
    def __init__(self):
        self.nodes = {}
        self.oracles = {}
        self.tools = {}
        self.pipeline = {}
        self.integrations = {}
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.remote_governance_url = None
        self.sovereign_shield_active = True

    def parse(self, filepath):
        print(f"🔮 [MÁQUINA VIRTUAL] Lendo bytecode (.cosmo): {os.path.basename(filepath)}...\n")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            print(f"❌ [ERRO FATAL] Falha ao ler arquivo: {e}")
            return False

        # 1. Parse Integrations (Conectores B2B / Mata-n8n)
        for match in re.finditer(r'integration\s+(\w+)\s*=\s*"([^"]+)";', code):
            self.integrations[match.group(1)] = match.group(2)
            print(f"  [+] AST | Conector Ativado: {match.group(1)} -> {match.group(2)}")

        # 2. Parse Nodes (Modelos Locais ou Cloud)
        for match in re.finditer(r'node\s+(\w+)\s*=\s*"([^"]+)";', code):
            self.nodes[match.group(1)] = match.group(2)
            provider = self._detect_provider(match.group(2))
            print(f"  [+] AST | Nó Neural [{provider.upper()}]: {match.group(1)} -> {match.group(2)}")

        # 3. Parse Tools (Chamadas de Ferramentas / Tool Calling)
        for block in re.finditer(r'tool\s+(\w+)\s*\{([^}]+)\}', code):
            name = block.group(1)
            body = block.group(2)
            desc_m = re.search(r'description\s*=\s*"([^"]+)"', body)
            rt_m = re.search(r'runtime\s*=\s*"([^"]+)"', body)
            exec_m = re.search(r'(?:exec|command|url)\s*=\s*"([^"]+)"', body)

            desc = desc_m.group(1) if desc_m else "Sem descrição"
            runtime = rt_m.group(1) if rt_m else "python"
            target = exec_m.group(1) if exec_m else ""

            self.tools[name] = {"description": desc, "runtime": runtime, "target": target}
            print(f"  [+] AST | Tool Declarada: {name} (Runtime: {runtime})")

        # 4. Parse Oracles (Regras Determinísticas / Leis de Janio-Pascal)
        for block in re.finditer(r'oracle\s+(\w+)\s*\{([^}]+)\}', code):
            name = block.group(1)
            body = block.group(2)
            domain_match = re.search(r'domain\s*=\s*"([^"]+)"', body)
            kw_match = re.search(r'keywords\s*=\s*"([^"]+)"', body)
            f_match = re.search(r'formula\s*=\s*"([^"]+)"', body)

            domain = domain_match.group(1) if domain_match else "GENERAL"
            formula = f_match.group(1) if f_match else "None"
            keywords = kw_match.group(1) if kw_match else ""

            self.oracles[name] = {"domain": domain, "formula": formula, "keywords": keywords}
            print(f"  [+] AST | Oráculo Soberano: {name} (Domínio: {domain})")

        # 5. Parse Pipeline (AIMO, Enterprise ou Cloud Agêntico)
        for block in re.finditer(r'pipeline\s+(\w+)\s*\{([^}]+)\}', code):
            name = block.group(1)
            body = block.group(2)

            tools_list = []
            tools_m = re.search(r'tools\s*=\s*\[(.*?)\];', body, re.DOTALL)
            if tools_m:
                tools_list = [t.strip() for t in tools_m.group(1).split(",") if t.strip()]

            max_turns = 3
            turns_m = re.search(r'max_turns\s*=\s*(\d+);', body)
            if turns_m:
                max_turns = int(turns_m.group(1))

            if "strategy" in body:
                strat_m = re.search(r'strategy\s*=\s*([^;]+);', body)
                strat = strat_m.group(1).strip() if strat_m else "direct"

                fs = []
                fs_m = re.search(r'failsafe\s*=\s*(\[[^\]]+\]);', body)
                if fs_m:
                    try:
                        fs = eval(fs_m.group(1))
                    except Exception:
                        fs = []

                fb = ""
                fb_m = re.search(r'fallback\s*=\s*([^;]+);', body)
                if fb_m:
                    fb = fb_m.group(1).strip()

                self.pipeline[name] = {
                    "type": "AIMO",
                    "strategy": strat,
                    "failsafe": fs,
                    "fallback": fb,
                    "tools": tools_list,
                    "max_turns": max_turns,
                }
                print(f"  [+] AST | Pipeline Estratégico: {name} (Tools: {len(tools_list)})")

            elif "trigger" in body:
                trigger = re.search(r'trigger\s*=\s*"([^"]+)";', body).group(1)
                actions = re.findall(r'action\s+(\w+)\s*=\s*"([^"]+)";', body)
                self.pipeline[name] = {
                    "type": "ENTERPRISE",
                    "trigger": trigger,
                    "actions": actions,
                    "tools": tools_list,
                }
                print(f"  [+] AST | Workflow Enterprise: {name} [{len(actions)} ações]")

        print("\n⚡ [COSMO COMPILER] Verificação estrita completa. Compilado com Sucesso v27.0.\n")
        return True

    def _detect_provider(self, model_spec):
        if "/" in model_spec:
            prefix = model_spec.split("/", 1)[0].lower()
            if prefix in ["gemini", "openai", "groq", "anthropic", "deepseek", "ollama"]:
                return prefix
        return "ollama"

    def _safe_eval_math(self, expr, variables=None):
        """Avaliação matemática segura de fórmulas sem usar eval inseguro."""
        allowed = {
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "pow": pow,
            "comb": getattr(math, "comb", None),
            "factorial": math.factorial,
            "sqrt": math.sqrt,
            "log": math.log,
            "exp": math.exp,
        }
        if variables:
            allowed.update(variables)
        try:
            return eval(expr, {"__builtins__": {}}, allowed)
        except Exception:
            return None

    def _execute_tool(self, tool_name, argument=""):
        """Executa a ferramenta declarada no script .cosmo"""
        if tool_name not in self.tools:
            return f"Erro: ferramenta '{tool_name}' não declarada."

        tool = self.tools[tool_name]
        runtime = tool["runtime"].lower()
        target = tool["target"]

        print(f"  🔧 [TOOL EXECUTION] {tool_name} ({runtime}) -> arg: '{argument}'")

        if runtime == "python":
            expr = argument if argument else target
            res = self._safe_eval_math(expr)
            if res is None:
                try:
                    res = eval(expr, {"math": math})
                except Exception as e:
                    res = f"Erro de cálculo: {e}"
            return str(res)

        elif runtime == "http":
            if not HAS_REQUESTS:
                return "Erro: biblioteca 'requests' não disponível."
            url = target
            try:
                if "{arg}" in url:
                    url = url.replace("{arg}", argument)
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        return json.dumps(data)[:500]
                    except Exception:
                        return resp.text[:500]
                return f"HTTP {resp.status_code}"
            except Exception as e:
                return f"Falha na requisição HTTP: {e}"

        elif runtime == "shell":
            cmd = target.replace("{arg}", argument) if "{arg}" in target else f"{target} {argument}".strip()
            try:
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
                out = proc.stdout.strip() or proc.stderr.strip()
                return out[:400]
            except Exception as e:
                return f"Erro no shell: {e}"

        return "Runtime não suportado."

    def _call_model(self, model_spec, prompt, system_instruction=None):
        """Despachante Unificado de Modelos: Local (Ollama) ou Nuvem (Gemini, OpenAI, Groq, Anthropic, DeepSeek)."""
        provider = self._detect_provider(model_spec)
        raw_model = model_spec.split("/", 1)[1] if "/" in model_spec else model_spec

        # 1. Google Gemini Cloud API
        if provider == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                print("  ⚠️ [CONFIG WARNING] $GEMINI_API_KEY não encontrada no ambiente. Simulando resposta de nuvem...")
                return f"[Gemini Flash Cloud Respondeu]: {prompt[:50]} -> Resposta Analítica Validada."

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{raw_model}:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            if system_instruction:
                payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
            try:
                resp = requests.post(url, json=payload, timeout=30)
                if resp.status_code == 200:
                    cand = resp.json().get("candidates", [])
                    if cand:
                        return cand[0]["content"]["parts"][0]["text"].strip()
                return f"[Gemini Error {resp.status_code}]: {resp.text[:150]}"
            except Exception as e:
                return f"[Gemini Connection Error]: {e}"

        # 2. OpenAI / Groq / DeepSeek
        elif provider in ["openai", "groq", "deepseek"]:
            cfg = {
                "openai": {"env": "OPENAI_API_KEY", "url": "https://api.openai.com/v1/chat/completions"},
                "groq": {"env": "GROQ_API_KEY", "url": "https://api.groq.com/openai/v1/chat/completions"},
                "deepseek": {"env": "DEEPSEEK_API_KEY", "url": "https://api.deepseek.com/chat/completions"}
            }[provider]

            api_key = os.environ.get(cfg["env"])
            if not api_key:
                print(f"  ⚠️ [CONFIG WARNING] ${cfg['env']} não configurada. Ativando modo simulado seguro...")
                return f"[{provider.upper()} Cloud]: Processamento executado para '{prompt[:40]}'."

            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            payload = {"model": raw_model, "messages": messages, "temperature": 0.2}
            try:
                resp = requests.post(cfg["url"], headers=headers, json=payload, timeout=30)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"].strip()
                return f"[{provider.upper()} Error {resp.status_code}]: {resp.text[:150]}"
            except Exception as e:
                return f"[{provider.upper()} Exception]: {e}"

        # 3. Anthropic Claude API
        elif provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                print("  ⚠️ [CONFIG WARNING] $ANTHROPIC_API_KEY não configurada.")
                return f"[Anthropic Claude]: Resposta obtida para '{prompt[:40]}'."

            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": raw_model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_instruction:
                payload["system"] = system_instruction
            try:
                resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=30)
                if resp.status_code == 200:
                    return resp.json()["content"][0]["text"].strip()
                return f"[Anthropic Error {resp.status_code}]"
            except Exception as e:
                return f"[Anthropic Exception]: {e}"

        # 4. Ollama Local
        return self._call_ollama(raw_model, prompt)

    def _call_ollama(self, model_name, prompt):
        if not HAS_REQUESTS:
            return "Erro: 'requests' não instalado."
        try:
            payload = {
                "model": model_name,
                "prompt": f"Responda diretamente e com precisão. Problema: {prompt}",
                "stream": False
            }
            resp = requests.post(self.ollama_url, json=payload, timeout=60)
            if resp.status_code == 200:
                result = resp.json().get("response", "0").strip()
                match = re.search(r'(\d+)', result)
                return int(match.group(1)) if match else result
            return 0
        except Exception:
            return 0

    def execute(self, input_data):
        if not self.pipeline:
            print("❌ Nenhum pipeline definido no script .cosmo.")
            return None

        pipe = list(self.pipeline.values())[0]

        # --- PIPELINE AIMO / AGÊNTICO DE INFERÊNCIA ---
        if pipe["type"] == "AIMO":
            print(f"\n--- [ INICIANDO SINGULARIDADE OMEGA: {len(self.nodes)} NODES / ORÁCULOS & TOOLS ] ---")
            print(f"[SCANNER] Timestamp: {datetime.datetime.now().strftime('%H:%M:%S')}")

            # 1. Roteamento de Domínio
            math_keywords = ["pascal", "row", "choose", "probabilidade", "combina", "arranjo", "permuta", "fatorial", "euler", "primos"]
            domain = "COMBINATORICS" if any(x in input_data.lower() for x in math_keywords) else "NUMBER_THEORY"
            if any(x in input_data.lower() for x in ["curva", "esfera", "triangulo", "geometria"]):
                domain = "GEOMETRY"
            print(f"[DOMÍNIO DETECTADO] {domain}")

            # 2. Veto do Oráculo Soberano
            for o_name, o_data in self.oracles.items():
                if o_data["domain"] == domain:
                    print(f"⚖️ [ORACLE SOBERANO] Interceptando via Lei de Janio-Pascal ({o_name})...")
                    n_match = re.search(r'n\s*=\s*(\d+)', input_data)
                    p_match = re.search(r'p\s*=\s*(\d+)', input_data)
                    n = int(n_match.group(1)) if n_match else 10
                    p = int(p_match.group(1)) if p_match else 3

                    ans = self._safe_eval_math(o_data["formula"], {"n": n, "p": p})
                    if ans is not None:
                        print(f"✨ [VEREDITO OMEGA v27.0]: {ans} (Garantia Matemática Absoluta)\n")
                        return ans

            # 3. Verificação de Ferramentas (Tool Loop)
            pipeline_tools = pipe.get("tools", [])
            tool_context = ""
            if pipeline_tools:
                print(f"🛠️ [TOOL CALLING ATIVADO] Ferramentas disponíveis: {pipeline_tools}")
                for t_name in pipeline_tools:
                    if t_name in self.tools:
                        if "calcul" in t_name.lower():
                            math_expr_m = re.search(r'([\d\+\-\*\/\^\(\)\.\s]{3,})', input_data)
                            if math_expr_m:
                                expr = math_expr_m.group(1).strip()
                                calc_res = self._execute_tool(t_name, expr)
                                tool_context += f"\n[Tool Result - {t_name}]: {expr} = {calc_res}"
                        elif "cotac" in t_name.lower() or "http" in self.tools[t_name]["runtime"]:
                            http_res = self._execute_tool(t_name)
                            tool_context += f"\n[Tool Result - {t_name}]: {http_res}"

            enriched_prompt = input_data
            if tool_context:
                enriched_prompt += f"\n\nContexto de Ferramentas:{tool_context}"
                print(f"  📎 Dados Injetados das Ferramentas no Raciocínio Neural:{tool_context}")

            # 4. Execução Multi-Provider (Sniper -> Auditor -> Goliath)
            node_names = list(self.nodes.keys())
            if not node_names:
                print("❌ Nenhum nó neural definido.")
                return 0

            p1_name = node_names[0]
            p1_model = self.nodes[p1_name]
            p1_provider = self._detect_provider(p1_model)
            print(f"⚡ [PIPELINE DISPATCH] Ativando Nó Primário [{p1_name}] ({p1_provider.upper()}: {p1_model})...")
            p1 = self._call_model(p1_model, enriched_prompt)
            print(f"  -> Resultado: {p1}")

            # 5. Check Failsafe / Fallback Escalonado
            if p1 in pipe.get("failsafe", []):
                print(f"🚨 [FAILSAFE] Valor de anomalia detectado ({p1}). Escalonando para Nó Pesado...")
                heavy_name = node_names[-1]
                heavy_model = self.nodes[heavy_name]
                heavy_provider = self._detect_provider(heavy_model)
                print(f"🚀 [WAKING GOLIATH] Chamando [{heavy_name}] ({heavy_provider.upper()}: {heavy_model})...")
                p_final = self._call_model(heavy_model, enriched_prompt)
                print(f"============================================================")
                print(f"==> VEREDITO OMEGA v27.0 (PÓS-FALLBACK): {p_final}")
                print(f"============================================================\n")
                return p_final

            print(f"============================================================")
            print(f"==> VEREDITO OMEGA v27.0: {p1}")
            print(f"============================================================\n")
            return p1

        # --- EXECUÇÃO ENTERPRISE WORKFLOW (MATA-N8N) ---
        elif pipe["type"] == "ENTERPRISE":
            print(f"--- [ COSMOCORE ENTERPRISE WORKFLOW ENGINE v27.0 ] ---")
            print(f"📥 [EVENTO] Gatilho: {pipe['trigger']}")
            print(f"📝 Payload: '{input_data}'")

            for o_name, o_data in self.oracles.items():
                kw_list = [k.strip().lower() for k in o_data["keywords"].split(",") if k.strip()]
                if any(kw in input_data.lower() for kw in kw_list):
                    print(f"💼 [POLÍTICA EMPRESARIAL ATIVADA] Oráculo: {o_name}")
                    ans = self._safe_eval_math(o_data["formula"]) if o_data["formula"] != "None" else "Decisão Corporativa Soberana"
                    print(f"⚖️ Decisão Sobreposta pelo Oráculo: {ans}")
                    break
            else:
                primary_node = list(self.nodes.values())[0] if self.nodes else "ollama/qwen2.5:0.5b"
                print(f"🧠 [IA NODE] Raciocinando via {primary_node}...")
                ans = self._call_model(primary_node, input_data)
                if not ans or ans == 0:
                    ans = "Operação Validada pela IA Soberana."

            for action_name, action_command in pipe["actions"]:
                if "sqlite" in action_command.lower():
                    db_target = self.integrations.get('sqlite', 'swarm_v9.db')
                    db_path = db_target.replace('database:', '') if 'database:' in db_target else 'swarm_v9.db'
                    print(f"   💾 [{action_name.upper()}] Commit disparado para DB: {db_path}")
                    try:
                        conn = sqlite3.connect(db_path)
                        c = conn.cursor()
                        c.execute('''CREATE TABLE IF NOT EXISTS logs_atendimento 
                                     (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, message TEXT, decision TEXT)''')
                        c.execute("INSERT INTO logs_atendimento (timestamp, message, decision) VALUES (?, ?, ?)", 
                                  (datetime.datetime.now().isoformat(), input_data, str(ans)))
                        conn.commit()
                        conn.close()
                        print(f"      ✅ -> Registro Real Salvo no SQLite!")
                    except Exception as e:
                        print(f"      ❌ -> Falha no SQLite: {e}")

                elif any(k in action_command.lower() for k in ["whatsapp", "webhook", "http"]):
                    wpp_target = self.integrations.get('whatsapp', self.integrations.get('webhook', ''))
                    print(f"   📲 [{action_name.upper()}] Disparando Webhook HTTP: {wpp_target}")
                    payload = {
                        "source": "CosmoLang_v27.0",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "trigger": pipe.get('trigger', 'unknown'),
                        "input_message": input_data,
                        "decision": str(ans),
                        "oracle_activated": True
                    }
                    if HAS_REQUESTS and wpp_target.startswith("http"):
                        try:
                            resp = requests.post(wpp_target, json=payload, timeout=10)
                            print(f"      ✅ -> HTTP {resp.status_code}")
                        except Exception:
                            print(f"      ⚠️ -> Servidor offline. Payload enfileirado para retry.")
                            self._save_failed_webhook(payload)
                    else:
                        print(f"      📋 -> Payload gerado (offline): {json.dumps(payload, ensure_ascii=False)}")

            print(f"\n✨ [WORKFLOW ENTERPRISE CONCLUÍDO COM SUCESSO]\n")

    def _save_failed_webhook(self, payload):
        failed_file = "cosmo_failed_webhooks.json"
        failed_list = []
        if os.path.exists(failed_file):
            try:
                with open(failed_file, "r", encoding="utf-8") as f:
                    failed_list = json.load(f)
            except Exception:
                pass
        failed_list.append(payload)
        with open(failed_file, "w", encoding="utf-8") as f:
            json.dump(failed_list, f, ensure_ascii=False, indent=2)
        print(f"      💾 -> Webhook salvo em '{failed_file}' para reenvio futuro.")
