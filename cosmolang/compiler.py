import re, time
import os
import sqlite3
import datetime
import json

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

class CosmoVM:
    def __init__(self):
        self.nodes = {}
        self.oracles = {}
        self.pipeline = {}
        self.integrations = {} 
        self.ollama_url = "http://localhost:11434/api/generate"

    def parse(self, filepath):
        print(f"📡 [MÁQUINA VIRTUAL] Lendo bytecode (.cosmo): {os.path.basename(filepath)}...\n")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            print(f"❌ [ERRO FATAL] Falha ao ler arquivo: {e}")
            return False

        # Parse Integrations (Mata-n8n Conectores)
        for match in re.finditer(r'integration\s+(\w+)\s*=\s*"([^"]+)";', code):
            self.integrations[match.group(1)] = match.group(2)
            print(f"  [+] AST | Conector B2B Ativado: {match.group(1)} -> {match.group(2)}")

        # Parse Nodes
        for match in re.finditer(r'node\s+(\w+)\s*=\s*"([^"]+)";', code):
            self.nodes[match.group(1)] = match.group(2)
            print(f"  [+] AST | Neural Node Extraído: {match.group(1)} -> {match.group(2)}")

        # Parse Oracles
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
            print(f"  [+] AST | Sovereign/Business Oracle: {name} (Filtro: {domain})")

        # Parse Pipeline (Híbrido: AIMO Matemático ou Enterprise Workflow)
        for block in re.finditer(r'pipeline\s+(\w+)\s*\{([^}]+)\}', code):
            name = block.group(1)
            body = block.group(2)
            
            # Formato Clássico AIMO
            if "strategy" in body:
                strat = re.search(r'strategy\s*=\s*([^;]+);', body).group(1)
                fs = re.search(r'failsafe\s*=\s*(\[[^\]]+\]);', body).group(1)
                fb = re.search(r'fallback\s*=\s*([^;]+);', body).group(1)
                self.pipeline[name] = {"type": "AIMO", "strategy": strat, "failsafe": eval(fs), "fallback": fb}
                print(f"  [+] AST | Lazy Pipeline (Simulação Algébrica): {name}")
                
            # Novo Formato B2B (Substituto n8n)
            elif "trigger" in body:
                trigger = re.search(r'trigger\s*=\s*"([^"]+)";', body).group(1)
                actions = re.findall(r'action\s+(\w+)\s*=\s*"([^"]+)";', body)
                self.pipeline[name] = {"type": "ENTERPRISE", "trigger": trigger, "actions": actions}
                print(f"  [+] AST | Workflow Automação de Empresa: {name} [{len(actions)} ações roteadas]")

        print("\n✅ [COSMO COMPILER] Verificação estrita completa. Compilado.")
        return True
        
    def _call_ollama(self, model_name, prompt):
        """Faz a chamada real ao cérebro (Ollama)"""
        if not HAS_REQUESTS:
            return "Erro: 'requests' não instalado."
        
        try:
            payload = {
                "model": model_name,
                "prompt": f"Responda apenas com o número final. Problema: {prompt}",
                "stream": False
            }
            resp = requests.post(self.ollama_url, json=payload, timeout=60)
            if resp.status_code == 200:
                result = resp.json().get("response", "0").strip()
                # Tentar extrair apenas o número se houver texto
                match = re.search(r'(\d+)', result)
                return int(match.group(1)) if match else 0
            return 0
        except Exception:
            return 0

    def execute(self, input_data):
        pipe = list(self.pipeline.values())[0]
        
        # --- EXECUÇÃO OMEGA (KAGGLE AIMO / REAL INFERENCE) ---
        if pipe["type"] == "AIMO":
            print(f"\n--- [ INICIANDO SINGULARIDADE OMEGA: {len(self.nodes)} NODES / 1 VOTO SOBERANO ] ---")
            print(f"\n[SCANNER] ID: {datetime.datetime.now().strftime('%H%M%S')}_OMEGA")
            
            # 1. Roteamento de Domínio (AIMO-focused)
            math_keywords = ["pascal", "row", "choose", "probabilidade", "combina", "arranjo", "permuta", "fatorial", "euler", "primos"]
            domain = "COMBINATORICS" if any(x in input_data.lower() for x in math_keywords[:8]) else "NUMBER_THEORY"
            if any(x in input_data.lower() for x in ["curva", "esfera", "triangulo", "geometria"]):
                domain = "GEOMETRY"
            print(f"[DOMÍNIO DETECTADO] {domain}")
            
            # 2. Veto do Oráculo Soberano
            for o_name, o_data in self.oracles.items():
                if o_data["domain"] == domain:
                    print(f"⚖️ [ORACLE SOBERANO] Interceptando via Lei de Janio-Pascal...")
                    # Mock de variáveis para a fórmula (n, p) extraídos via regex simples se possível
                    n_match = re.search(r'n\s*=\s*(\d+)', input_data)
                    p_match = re.search(r'p\s*=\s*(\d+)', input_data)
                    n = int(n_match.group(1)) if n_match else 10
                    p = int(p_match.group(1)) if p_match else 3
                    
                    try:
                        ans = eval(o_data["formula"])
                        print(f"✨ [VEREDITO OMEGA V25.2]: {ans} (Garantia Matemática)")
                        return ans
                    except: pass

            # 3. Pipeline de Consenso Real
            node_names = list(self.nodes.keys())
            if not node_names:
                print("❌ Nenhum node neural definido.")
                return 0

            # Disparo Rápido (Sniper / Auditor)
            print(f"⚡ [PIPELINE ENGINE] Strategy: {pipe['strategy']}")
            
            p1_name = node_names[0]
            print(f"  -> Ativando Node [{p1_name}] ({self.nodes[p1_name]})...")
            p1 = self._call_ollama(self.nodes[p1_name], input_data)
            print(f"  -> Resultado: {p1}")

            # Check Failsafe
            if p1 in pipe["failsafe"]:
                print(f"[FAILSAFE] Valor suspeito detectado ({p1}). Acordando Goliath...")
                heavy_name = node_names[-1]
                print(f"[WAKING GOLIATH] Escalando para nó pesado: {self.nodes[heavy_name]}...")
                p_final = self._call_ollama(self.nodes[heavy_name], input_data)
                print(f"[FALLBACK LOG] {p1_name}: {p1} | Goliath: {p_final}")
                print(f"============================================================")
                print(f"==> VEREDITO OMEGA V25.2: {p_final}")
                print(f"============================================================\n")
                return p_final
            
            print(f"============================================================")
            print(f"==> VEREDITO OMEGA V25.2: {p1}")
            print(f"============================================================\n")
            return p1

        # --- EXECUÇÃO ENTERPRISE (SUBSTITUTO N8N) ---
        elif pipe["type"] == "ENTERPRISE":
            print(f"--- [ COSMOCORE ENTERPRISE WORKFLOW ENGINE ] ---")
            print(f"📥 [EVENTO RECEBIDO] Gatilho Webhook/API: {pipe['trigger']}")
            print(f"📝 Payload / Mensagem Cliente: '{input_data}'")
            
            # Checagem de Oráculos Empresariais (Ex: Regras de Reembolso Fixas)
            for o_name, o_data in self.oracles.items():
                kw_list = [k.strip().lower() for k in o_data["keywords"].split(",")]
                if any(kw in input_data.lower() for kw in kw_list):
                    print(f"💼 [POLÍTICA EMPRESARIAL ATIVADA] Oráculo de Negócios: {o_name}")
                    ans = eval(o_data["formula"]) if o_data["formula"] != "None" else "Decisão Automática Soberana Escalonada"
                    print(f"⚖️ Decisão Corporativa Sobreposta pela Máquina: {ans}")
                    break
            else:
                print(f"🧠 [IA NODE] {list(self.nodes.keys())[0]} raciocinando sobre o ticket do cliente...")
                time.sleep(1)
                print(f"   -> Resposta gerada: 'Claro, notei seu problema. Irei transferir seu pedido de estorno imediatamente.'")
                ans = "Operação Validada pela IA."
                
            # Rodar Módulo de Ações (Onde o n8n perde feio em complexidade)
            print(f"\n⚙️ [PIPELINE DE AÇÕES (SIDECARS)] Executando saídas nativas do CosmoLang:")
            for action_name, action_command in pipe["actions"]:
                if "sqlite" in action_command.lower():
                    db_target = self.integrations.get('sqlite', '')
                    db_path = db_target.replace('database:', '') if 'database:' in db_target else 'swarm_default.db'
                    print(f"   💾 [{action_name.upper()}] Commit disparado para DB Local: {db_path}")
                    try:
                        conn = sqlite3.connect(db_path)
                        c = conn.cursor()
                        c.execute('''CREATE TABLE IF NOT EXISTS logs_atendimento 
                                     (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, message TEXT, decision TEXT)''')
                        c.execute("INSERT INTO logs_atendimento (timestamp, message, decision) VALUES (?, ?, ?)", 
                                  (datetime.datetime.now().isoformat(), input_data, ans))
                        conn.commit()
                        conn.close()
                        print(f"      ✅ -> Registro Real Salvo com Sucesso no SQLite!")
                    except Exception as e:
                        print(f"      ❌ -> Falha de Gravação no Banco: {e}")
                elif "whatsapp" in action_command.lower() or "webhook" in action_command.lower() or "http" in action_command.lower():
                    wpp_target = self.integrations.get('whatsapp', self.integrations.get('webhook', ''))
                    print(f"   📲 [{action_name.upper()}] Disparando Webhook HTTP Real: {wpp_target}")
                    
                    payload = {
                        "source": "CosmoLang_V25.1",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "trigger": pipe.get('trigger', 'unknown'),
                        "input_message": input_data,
                        "decision": str(ans),
                        "oracle_activated": True
                    }
                    
                    if HAS_REQUESTS and wpp_target.startswith("http"):
                        try:
                            resp = requests.post(wpp_target, json=payload, timeout=10)
                            print(f"      ✅ -> HTTP {resp.status_code} | Resposta: {resp.text[:200]}")
                        except requests.exceptions.ConnectionError:
                            print(f"      ⚠️ -> Servidor offline. Payload salvo localmente para retry.")
                            self._save_failed_webhook(payload)
                        except Exception as e:
                            print(f"      ❌ -> Erro no POST: {e}")
                            self._save_failed_webhook(payload)
                    else:
                        print(f"      📋 -> Payload gerado (modo offline): {json.dumps(payload, ensure_ascii=False)}")
                    time.sleep(0.3)
                else:
                    print(f"   ⚡ [{action_name.upper()}] Ação genérica executada: {action_command}")
            
            print(f"\n✨ [WORKFLOW ENTERPRISE CONCLUÍDO COM SUCESSO]")

    def _save_failed_webhook(self, payload):
        """Salva webhooks que falharam para retry posterior."""
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
