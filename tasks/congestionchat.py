import numpy as np
import os
import matplotlib.pyplot as plt

# Lista di valori di M (numero di richieste)
M_values = list(range(1, 35, 3))
print(M_values)

# Definizione delle strategie di transceiver e delle scelte di percorso
transceiver_strategies = ["fixed-rate", "flex-rate", "shannon"]
path_choices = ["shortest_path", "least_congested_path"]
num_iterations = 5  # Numero di iterazioni per ogni valore di M

# Dizionario per salvare i risultati medi per ogni valore di M
results = {}

# Creazione cartella per salvare output
OUTPUT_FOLDER = "output_images_congestion"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for M in M_values:
    print(f"\n===== Calcolando per M = {M} =====")

    # Dizionario per raccogliere dati
    means = {
        "latency_min": {},
        "latency_avg": {},
        "latency_max": {},
        "capacity_min": {},
        "capacity_avg": {},
        "capacity_max": {},
        "capacity_total": {},
        "gsnr_min": {},
        "gsnr_avg": {},
        "gsnr_max": {},
        "blocking_percentuals": {}
    }

    # Inizializzazione delle strutture dati per ogni strategia e path choice
    for metric in means:
        for strategy in transceiver_strategies:
            means[metric][strategy] = {}
            for path_choice in path_choices:
                means[metric][strategy][path_choice] = []

    for path_choice in path_choices:
        for iteration in range(num_iterations):

            print(f"Iterazione {iteration+1} - {path_choice}")

            for strategy in transceiver_strategies:
                # Simuliamo dati casuali (sostituire con i veri dati dalla rete)
                latencies = np.random.uniform(5, 20, size=10)  # Esempio: Latenze casuali
                bit_rates = np.random.uniform(1, 10, size=10)  # Capacità casuali
                gsns = np.random.uniform(10, 30, size=10)  # SNR casuali
                blocking = np.random.uniform(0, 50)  # Percentuale di blocking casuale

                # Salvataggio dei valori medi
                means["latency_min"][strategy][path_choice].append(np.min(latencies))
                means["latency_avg"][strategy][path_choice].append(np.mean(latencies))
                means["latency_max"][strategy][path_choice].append(np.max(latencies))
                means["capacity_min"][strategy][path_choice].append(np.min(bit_rates))
                means["capacity_avg"][strategy][path_choice].append(np.mean(bit_rates))
                means["capacity_max"][strategy][path_choice].append(np.max(bit_rates))
                means["capacity_total"][strategy][path_choice].append(np.sum(bit_rates))
                means["gsnr_min"][strategy][path_choice].append(np.min(gsns))
                means["gsnr_avg"][strategy][path_choice].append(np.mean(gsns))
                means["gsnr_max"][strategy][path_choice].append(np.max(gsns))
                means["blocking_percentuals"][strategy][path_choice].append(blocking)

    # Calcolo delle medie finali per ogni M
    final_means = {
        metric: {
            strategy: {
                path_choice: np.mean(values) if values else None
                for path_choice, values in means[metric][strategy].items()
            }
            for strategy in transceiver_strategies
        }
        for metric in means
    }

    # Salvataggio nel dizionario dei risultati
    results[M] = final_means

print("\nTutti i risultati sono stati calcolati!")

# ----- PLOTTAGGIO -----
def plot_metric(metric, ylabel):
    plt.figure(figsize=(10, 5))

    for strategy in transceiver_strategies:
        for path_choice in path_choices:
            values = [results[M][metric][strategy][path_choice] for M in M_values]
            plt.plot(M_values, values, marker='o', label=f"{strategy} - {path_choice}")

    plt.xlabel("M (Numero di richieste)")
    plt.ylabel(ylabel)
    plt.title(f"Variazione di {ylabel} al variare di M")
    plt.legend()
    plt.grid()
    plt.savefig(f"{OUTPUT_FOLDER}/{metric}_vs_M.png")
    plt.show()

# Esempio: Plottiamo la latenza media
plot_metric("latency_avg", "Latency (ms)")
