import time
import multiprocessing as mp
import matplotlib.pyplot as plt

def partial_sum(start_end): # calcula a soma parcial do intervalo
    start, end = start_end

    return sum(range(start, end + 1))

def serial_sum(n):

    return sum(range(1, n + 1))

def parallel_sum(n, num_processes):
    if num_processes <= 1:

        return serial_sum(n)
    
    chunk_size = n // num_processes
    ranges = []
    
    for i in range(num_processes):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_processes - 1 else n
        ranges.append((start, end))

    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(partial_sum, ranges)
        
    return sum(results)

def print_table(results): # vai exibir os resultados em formato tabular
    headers = ["Processos (P)", "Tempo Médio (s)", "Speedup", "Eficiência"]
    
    # Tenta usar a biblioteca 'tabulate' se disponível, senão usa formatação nativa
    try:
        from tabulate import tabulate
        table_data = [
            [
                res["P"],
                f"{res['tempo']:.6f}",
                f"{res['speedup']:.2f}",
                f"{res['eficiencia']:.2f}"
            ]
            for res in results
        ]
        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
    except ImportError:
        print("\n" + "=" * 55)
        print(f"{headers[0]:<15} {headers[1]:<15} {headers[2]:<12} {headers[3]:<10}")
        print("=" * 55)
        for res in results:
            print(f"{res['P']:<15} {res['tempo']:<15.6f} {res['speedup']:<12.2f} {res['eficiencia']:<10.2f}")
        print("=" * 55)

def plot_graphs(results, n): # vai gerar os graficos
    processes = [r["P"] for r in results]
    times = [r["tempo"] for r in results]
    speedups = [r["speedup"] for r in results]
    
    # Tempo x Número de Processos
    plt.figure(figsize=(8, 5))
    plt.plot(processes, times, marker='o', color='b', linewidth=2, label='Tempo Observado')
    plt.title(f'Tempo de Execução vs. Número de Processos (N = {n:,})')
    plt.xlabel('Número de Processos (P)')
    plt.ylabel('Tempo de Execução (segundos)')
    plt.xticks(processes)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig('tempo_vs_processos.png')
    plt.close()
    print("[+] Gráfico 'tempo_vs_processos.png' gerado com sucesso.")

    # Speedup x Número de Processos
    plt.figure(figsize=(8, 5))
    plt.plot(processes, speedups, marker='s', color='g', linewidth=2, label='Speedup Observado')
    
    plt.plot(processes, processes, linestyle='--', color='r', label='Speedup Ideal (Linear)')
    plt.title(f'Speedup vs. Número de Processos (N = {n:,})')
    plt.xlabel('Número de Processos (P)')
    plt.ylabel('Speedup (T_serial / T_paralelo)')
    plt.xticks(processes)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig('speedup_vs_processos.png')
    plt.close()
    print("[+] Gráfico 'speedup_vs_processos.png' gerado com sucesso.")

def main():
    print("=== Atividade 01: Programação Distribuída, Paralela e Concorrente ===")
    
    try:
        n = int(input("Informe o valor de N (ex: 100000000): "))
        
        process_input = input("Informe a lista de processos separados por vírgula (padrão '1,2,4,8'): ").strip()
        if not process_input:
            process_list = [1, 2, 4, 8]
        else:
            process_list = [int(p.strip()) for p in process_input.split(",")]
            
        repetitions = int(input("Informe a quantidade de repetições do experimento (ex: 5): ") or 5)
    except ValueError:
        print("Erro: Por favor, insira valores inteiros válidos.")
        return

    # vai garantir que 1 (o serial) esteja no inicio da lista sem duplicar
    if 1 not in process_list:
        process_list = [1] + process_list
    else:
        # reordena para colocar o 1 sempre na primeira posicao
        process_list = [1] + [p for p in process_list if p != 1]

    print(f"\nIniciando experimentos com N = {n:,}, Repetições = {repetitions}...")
    
    results = []
    t_serial_mean = None

    # quantidade de processos
    for p in process_list:
        times = []
        print(f"\nTestando com P = {p} processo(s)...")
        
        for r in range(repetitions):
            start_time = time.perf_counter() # marca tempo inicial
            if p == 1:
                res_sum = serial_sum(n)
            else:
                res_sum = parallel_sum(n, p)
            end_time = time.perf_counter() # marca tempo final
            
            elapsed = end_time - start_time # calcula da duracao da execucao atual
            times.append(elapsed)

        t_mean = sum(times) / len(times) 
        
        # o tempo do P = 1 sempre define o t_serial_mean de refe
        if p == 1:
            t_serial_mean = t_mean
            
        speedup = t_serial_mean / t_mean
        eficiencia = speedup / p
        
        results.append({
            "P": p,
            "tempo": t_mean,
            "speedup": speedup,
            "eficiencia": eficiencia
        })
        print(f" -> Tempo médio: {t_mean:.6f}s | Speedup: {speedup:.2f} | Eficiência: {eficiencia:.2f}")

    print_table(results) # tabela comparativa
    
    plot_graphs(results, n) # gera gráficos

if __name__ == '__main__':
    main()