import sys
import argparse
from cosmolang.compiler import CosmoVM

def main():
    parser = argparse.ArgumentParser(description="CosmoLang CLI - Execução de Enxames AGI (CosmoCore V25)")
    parser.add_argument("command", choices=["build", "run", "version"], help="Comando a ser executado")
    parser.add_argument("file", nargs="?", help="Arquivo fonte .cosmo")
    parser.add_argument("--test", help="Texto do problema para simulação local", default="")

    args = parser.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')

    if args.command == "version":
        print("🚀 CosmoCore Engine V25.0 - Janio-Pascal Edition")
        sys.exit(0)

    if args.command in ["run", "build"]:
        if not args.file:
            print("❌ [ERRO] É necessário especificar um arquivo .cosmo. Exemplo: cosmo run script.cosmo")
            sys.exit(1)
            
        vm = CosmoVM()
        success = vm.parse(args.file)
        
        if success and args.test:
            print("\n" + "-"*60)
            print("🎯 [TESTE LOCAL AIMO INICIADO]")
            vm.execute_mock(args.test)
            print("-" * 60)
        elif success and args.command == "run":
            print("\n[AVISO] Compilação finalizada com sucesso. O bytecode está pronto para a Cloud.")
            print("[INFO]  Para injetar um prompt local interativo, use: cosmo run script.cosmo --test \"problema aqui\"")

if __name__ == "__main__":
    main()
