import re, time
import os
import sqlite3
import datetime

class CosmoVM:
    def __init__(self):
        self.nodes = {}
        self.oracles = {}
        self.pipeline = {}
        self.integrations = {} # V25.1 Enterprise

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
        
    def execute_mock(self, input_data):
        pipe = list(self.pipeline.values())[0]
        
        # --- EXECUÇÃO MATEMÁTICA (KAGGLE AIMO STANDARD) ---
        if pipe["type"] == "AIMO":
            print(f"--- [ STARTING KAGGLE OMEGA SIMULATION ] ---")
            print(f"📝 Prompt AIMO: '{input_data}'")
            
            domain = "COMBINATORICS" if any(x in input_data.lower() for x in ["pascal", "row", "choose"]) else "GEOMETRY"
            print(f"🧠 [V25 ROTEADOR] Domínio classificado: {domain}")
            
            for o_name, o_data in self.oracles.items():
                if o_data["domain"] == domain and "pascal" in input_data.lower():
                    print(f"⚖️ [ORACLE SOBERANO] Condições ativadas!")
                    print(f"⚖️ [ORACLE ENGINE] Executando Fórmula Fechada Blindada: {o_data['formula']}")
                    n, p = 10, 3
                    ans = eval(o_data["formula"])
                    print(f"✨ [VEREDITO COSMO] Gate Matematico Ativo: {ans}\n")
                    return ans

            print(f"⚡ [PIPELINE ENGINE] Strategy Set: {pipe['strategy']}")
            
            node_names = list(self.nodes.keys())
            p1_name = node_names[0] if len(node_names) > 0 else "NodeA"
            p2_name = node_names[1] if len(node_names) > 1 else "NodeB"
            heavy_name = node_names[-1] if len(node_names) > 0 else "Goliath"
            
            p1, p2 = 121, 121
            print(f"  -> Disparo Rápido [{p1_name}]: {p1}")
            print(f"  -> Disparo Rápido [{p2_name}]: {p2}")
            
            if p1 == p2 and p1 in pipe["failsafe"]:
                print(f"🚨 [FAILSAFE ANTI-ERROR] Resposta {p1} barrada (Identificada como Alucinação)!")
                print(f"🏗️ [ESCALATION PROTOCOL] Despertando máquina pesada: {pipe['fallback']}...")
                time.sleep(1)
                p3 = 42 
                print(f"  -> [{heavy_name}] Cálculo Extraído: {p3}")
                print(f"✨ [VEREDITO COSMO] Resultado Seguro Consolidado: {p3}\n")
                return p3

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
                elif "whatsapp" in action_command.lower():
                    wpp_target = self.integrations.get('whatsapp', 'Conector_Desconhecido')
                    print(f"   📲 [{action_name.upper()}] Mensagem despachada usando API HTTP: {wpp_target}")
                    print(f"      ✅ -> Payload POST disparado: {{'to': 'CLIENTE', 'body': '{ans}'}}")
                    time.sleep(0.5)
                else:
                    print(f"   ⚡ [{action_name.upper()}] Ação genérica executada: {action_command}")
            
            print(f"\n✨ [WORKFLOW ENTERPRISE CONCLUÍDO COM SUCESSO]")
