import os
import json
import time

def rodar_experimento(intervalo_checkpoint, total_operacoes=100000, operacao_falha=73821, pasta_checkpoints="checkpoints"):
    # simulacao de rollbacks
    if not os.path.exists(pasta_checkpoints):
        os.makedirs(pasta_checkpoints)

    print(f"\n==================================================")
    print(f" Iniciando Experimento - Intervalo: {intervalo_checkpoint} ")
    print(f"==================================================")

    # salvamento ckpt
    estado_atual = 0
    checkpoints_salvos = {}
    
    tempo_inicio_checkpoint = time.perf_counter()
    qtd_checkpoints = 0

    for op in range(1, total_operacoes + 1):
        estado_atual = op  
        if op % intervalo_checkpoint == 0:
            qtd_checkpoints += 1
            arquivo_ckpt = os.path.join(pasta_checkpoints, f"ckpt_{intervalo_checkpoint}_{op}.json")
            dados = {"operacao": op, "estado": estado_atual}
            
            with open(arquivo_ckpt, "w") as f:
                json.dump(dados, f)
            
            checkpoints_salvos[op] = arquivo_ckpt

        if op == operacao_falha:
            print(f" [!] Processando operação {op} ... FALHA DETECTADA!")
            break

    tempo_fim_exec_inicial = time.perf_counter()
    overhead_checkpoints = tempo_fim_exec_inicial - tempo_inicio_checkpoint

    tempo_inicio_recuperacao = time.perf_counter()

    # vai identificar ckpt
    ultimo_ckpt_op = (operacao_falha // intervalo_checkpoint) * intervalo_checkpoint
    
    if ultimo_ckpt_op in checkpoints_salvos:
        arquivo_restaurar = checkpoints_salvos[ultimo_ckpt_op]
        with open(arquivo_restaurar, "r") as f:
            dados_restaurados = json.load(f)
        
        estado_restaurado = dados_restaurados["estado"]
        print(f" [->] Rollback executado: Restaurado estado do Checkpoint no passo {estado_restaurado}")
    else:
        estado_restaurado = 0
        print(" [->] Nenhum checkpoint disponível. Reiniciando do zero (0).")

    # retoma operacoes
    for op in range(estado_restaurado + 1, total_operacoes + 1):
        estado_atual = op

    tempo_fim_recuperacao = time.perf_counter()
    tempo_recuperacao = tempo_fim_recuperacao - tempo_inicio_recuperacao


    operacoes_perdidas = operacao_falha - estado_restaurado

    print("\n--- Resultados ---")
    print(f"• Quantidade de Checkpoints Criados: {qtd_checkpoints}")
    print(f"• Operações Perdidas: {operacoes_perdidas}")
    print(f"• Overhead dos Checkpoints: {overhead_checkpoints * 1000:.4f} ms")
    print(f"• Tempo de Recuperação (Rollback + Retomada): {tempo_recuperacao * 1000:.4f} ms")

    return {
        "intervalo": intervalo_checkpoint,
        "checkpoints": qtd_checkpoints,
        "ops_perdidas": operacoes_perdidas,
        "overhead_ms": overhead_checkpoints * 1000,
        "tempo_recuperacao_ms": tempo_recuperacao * 1000
    }

if __name__ == "__main__":
    intervalos = [100, 500, 1000, 5000]
    resultados = []

    for idx in intervalos:
        res = rodar_experimento(intervalo_checkpoint=idx)
        resultados.append(res)

    print("\n\n" + "="*60)
    print(" RESUMO FINAL DOS EXPERIMENTOS ")
    print("="*60)
    print(f"{'Intervalo':<10} | {'Checkpoints':<12} | {'Ops Perdidas':<13} | {'Overhead (ms)':<15} | {'Tempo Recup. (ms)'}")
    print("-" * 70)
    for r in resultados:
        print(f"{r['intervalo']:<10} | {r['checkpoints']:<12} | {r['ops_perdidas']:<13} | {r['overhead_ms']:<15.2f} | {r['tempo_recuperacao_ms']:.2f}")