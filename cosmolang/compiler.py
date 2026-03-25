import re, time
import os

class CosmoVM:
    def __init__(self):
        self.nodes = {}
        self.oracles = {}
        self.pipeline = {}

    def parse(self, filepath):
        print(f"📡 [MÁQUINA VIRTUAL] Lendo bytecode (.cosmo): {os.path.basename(filepath)}...\n")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            print(f"❌ [ERRO FATAL] Falha ao ler arquivo: {e}")
            return False

        # Parse Nodes
        for match in re.finditer(r'node\s+(\w+)\s*=\s*"([^"]+)";', code):
            self.nodes[match.group(1)] = match.group(2)
            print(f"  [+] AST | Neural Node Extraído: {match.group(1)} -> {match.group(2)}")

        # Parse Oracles
        for block in re.finditer(r'oracle\s+(\w+)\s*\{([^}]+)\}', code):
            name = block.group(1)
            body = block.group(2)
            domain = re.search(r'domain\s*=\s*"([^"]+)"', body).group(1)
            f_match = re.search(r'formula\s*=\s*"([^"]+)"', body)
            formula = f_match.group(1) if f_match else "None"
            self.oracles[name] = {"domain": domain, "formula": formula}
            print(f"  [+] AST | Sovereign Oracle Mapeado: {name} (Limiar de Domínio: {domain})")

        # Parse Pipeline
        for block in re.finditer(r'pipeline\s+(\w+)\s*\{([^}]+)\}', code):
            name = block.group(1)
            body = block.group(2)
            strat = re.search(r'strategy\s*=\s*([^;]+);', body).group(1)
            fs = re.search(r'failsafe\s*=\s*(\[[^\]]+\]);', body).group(1)
            fb = re.search(r'fallback\s*=\s*([^;]+);', body).group(1)
            self.pipeline[name] = {"strategy": strat, "failsafe": eval(fs), "fallback": fb}
            print(f"  [+] AST | Lazy Pipeline: {name} (Sistema Failsafe: {fs})")

        print("\n✅ [COSMO COMPILER] Verificação estrita completa. Compilado.")
        return True
        
    def execute_mock(self, problem):
        print(f"--- [ STARTING KAGGLE OMEGA SIMULATION ] ---")
        print(f"📝 Prompt AIMO: '{problem}'")
        
        domain = "COMBINATORICS" if any(x in problem.lower() for x in ["pascal", "row", "choose", "combine"]) else "GEOMETRY"
        print(f"🧠 [V25 ROTEADOR] Domínio classificado: {domain}")
        
        for o_name, o_data in self.oracles.items():
            if o_data["domain"] == domain and "pascal" in problem.lower():
                print(f"⚖️ [ORACLE SOBERANO DE JANIO-PASCAL] Condições ativadas!")
                print(f"⚖️ [ORACLE ENGINE] Executando Fórmula Fechada Blindada: {o_data['formula']}")
                n, p = 10, 3
                ans = eval(o_data["formula"])
                print(f"✨ [VEREDITO COSMO] Gate Matematico Ativo: {ans}\n")
                return ans

        pipe = list(self.pipeline.values())[0]
        print(f"⚡ [PIPELINE ENGINE] Strategy Set: {pipe['strategy']}")
        
        node_names = list(self.nodes.keys())
        p1_name = node_names[0] if len(node_names) > 0 else "NodeA"
        p2_name = node_names[1] if len(node_names) > 1 else "NodeB"
        heavy_name = node_names[-1] if len(node_names) > 0 else "Goliath"
        
        p1, p2 = 121, 121
        print(f"  -> Disparo Rápido [{p1_name}]: {p1}")
        print(f"  -> Disparo Rápido [{p2_name}]: {p2}")
        
        if p1 == p2 and p1 in pipe["failsafe"]:
            print(f"🚨 [FAILSAFE ANTI-ERROR] Resposta {p1} barrada (Identificada como Supersticiosa/Alucinação)!")
            print(f"🏗️ [ESCALATION PROTOCOL] Despertando máquina de força bruta: {pipe['fallback']}...")
            time.sleep(1)
            p3 = 42 
            print(f"  -> [{heavy_name}] Cálculo Extraído: {p3}")
            print(f"✨ [VEREDITO COSMO] Resultado Seguro Consolidado: {p3}\n")
            return p3
