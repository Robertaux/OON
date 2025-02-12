# Use this file to define your generic methods, e.g. for plots
from core.math_utils import lin2db
import pandas as pd
from core.elements import *
import os
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp

def values_computed(network, path, signal_power):
    total_latency=0.0
    total_noise_power=0.0
    snr=0
    for i in range(len(path)-1):
        current_label=path[i]
        next_label=path[i+1]
        line_label=current_label+next_label
        line=network.lines.get(line_label)
        if line:
            total_latency+=line.latency_generation()
            total_noise_power+=line.noise_generation(signal_power)
            snr=signal_power/total_noise_power
    total_snr_db=lin2db(snr)
    return total_latency, total_noise_power, total_snr_db

def create_dataframe(network, signal_power_w):
    results=[]
    for source_label in network.nodes:
        for destination_label in network.nodes:
            if source_label!=destination_label:
                paths=network.find_paths(source_label, destination_label)
                for path in paths:
                    path_string="->".join(path)
                    total_latency, total_noise_power, total_snr_db=values_computed(network, path, signal_power_w)
                    results.append([path_string, total_latency, total_noise_power, total_snr_db])
    columns=["Path"  , "      Total Latency (s)"  , "    Total Noise Power (W)  "  , "  SNR (dB)  "]
    paths_df=pd.DataFrame(results, columns=columns)
    return paths_df

def print_subplot(output_folder, transceiver_strategies, path, all_min, all_avg, all_max, label):
    fig1, axes1 = plt.subplots(3, 3, figsize=(24, 15))
    for i, strategy in enumerate(transceiver_strategies):
        df_min = pd.DataFrame(all_min[strategy][path],columns=[label])
        df_avg = pd.DataFrame(all_avg[strategy][path], columns=[label])
        df_max = pd.DataFrame(all_max[strategy][path], columns=[label])

        df_min_z = df_min[df_min[label] != 0.0]
        df_avg_z = df_avg[df_avg[label] != 0.0]
        df_max_z = df_max[df_max[label] != 0.0]

        axes1[i, 0].hist(df_min_z[label], bins=15, color='blue', alpha=1)
        axes1[i, 0].set_title(f'Distribution of minimum values of {label} for {strategy}')
        axes1[i, 0].set_xlabel(f'{label} minimum value')
        axes1[i, 0].set_ylabel('Frequency')
        axes1[i, 0].grid(True)

        axes1[i, 1].hist(df_avg_z[label], bins=15, color='yellow', alpha=1)
        axes1[i, 1].set_title(f'Distribution of average values of {label} for {strategy}')
        axes1[i, 1].set_xlabel(f'{label} average value')
        axes1[i, 1].set_ylabel('Frequency')
        axes1[i, 1].grid(True)

        axes1[i, 2].hist(df_max_z[label], bins=15, color='red', alpha=1)
        axes1[i, 2].set_title(f'Distribution of maximum values of {label}  for {strategy}')
        axes1[i, 2].set_xlabel(f'{label} maximum value')
        axes1[i, 2].set_ylabel('Frequency')
        axes1[i, 2].grid(True)

    fig1.suptitle(f'Distribution of Values of {label} in all the simulations ', fontsize=19)
    fig1.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(os.path.join(output_folder, f'distribution_{label}_{path}.png'))
    plt.close(fig1)


import os
import matplotlib.pyplot as plt


def plot_blocking_percentage(output_folder, transceiver_strategies, iters, blocking_percentuals, label):
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {
        'fixed-rate': 'blue',
        'flex-rate': 'green',  # Cambiato da giallo a verde per visibilità
        'shannon': 'red'
    }

    for strategy in transceiver_strategies:
        blocking_values = blocking_percentuals.get(strategy, {}).get(label, [])
        iterations = iters.get(strategy, {}).get(label, [])

        # Controllo che i dati esistano e abbiano la stessa lunghezza
        if not blocking_values or not iterations or len(blocking_values) != len(iterations):
            print(f"Errore nei dati per {strategy} ({label}): verificare lunghezza delle liste!")
            continue

        # Ordinare i dati per iterazioni
        sorted_data = sorted(zip(iterations, blocking_values))
        iterations, blocking_values = zip(*sorted_data)
        iterations = list(iterations)
        blocking_values = list(blocking_values)

        ax.plot(iterations, blocking_values, marker='o', linestyle='-', color=colors.get(strategy, 'black'),
                label=strategy)

    ax.set_title(f'Blocking Percentage Over Iterations ({label})', fontsize=14)
    ax.set_xlabel('Iterations', fontsize=12)
    ax.set_ylabel('Blocking Percentage (%)', fontsize=12)
    ax.legend(title="Transceiver Strategies", loc="upper right", fontsize=10, title_fontsize=12)
    ax.grid(True)

    # Creazione della cartella di output se non esiste
    os.makedirs(output_folder, exist_ok=True)

    # Salvataggio del grafico
    plt.savefig(os.path.join(output_folder, f'blocking_percentage_{label}.png'))
    plt.show()
    plt.close(fig)

def plot_capacities_total(output_folder, transceiver_strategies, capacities_total, label):
    fig, axes = plt.subplots(3, 1, figsize=(12, 15))

    colors = ['blue', 'yellow', 'red']

    for i, strategy in enumerate(transceiver_strategies):
        df = pd.DataFrame(capacities_total[strategy][label], columns=[label])
        df_clean = df[df[label] != 0.0].dropna()
        if df_clean.empty:
            print(f"Attenzione: nessun dato valido per la strategia {strategy} ({label})")
            continue

        axes[i].hist(df_clean[label], bins=15, color=colors[i], alpha=1, edgecolor='black')
        axes[i].set_title(f'Distribution of total capacity for {label} and for {strategy}', fontsize=14)
        axes[i].set_xlabel(f'{label} Total Capacity Value')
        axes[i].set_ylabel('Frequency')
        axes[i].grid(True)

    fig.suptitle(f'Distribution of total capacity for {label} Across Strategies', fontsize=18)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    plt.savefig(os.path.join(output_folder, f'distribution_total_capacity_{label}.png'))
    plt.show()
    plt.close(fig)

def plot_bit_rate_gsnr(output_folder, transceiver_strategies, bit_rates, gsnr, label):
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {
        'fixed-rate': 'blue',
        'flex-rate': 'yellow',
        'shannon': 'red'
    }

    for strategy in transceiver_strategies:
        bit_rates_used = (bit_rates.get(strategy, {}).get(label, []))
        gsnr_used = gsnr.get(strategy, {}).get(label, [])

        if not isinstance(bit_rates_used, list) or not isinstance(gsnr_used, list):
            print(f"Errore: dati non validi per {strategy} ({label})")
            continue

        bit_rates_used = [item / 1e9 for sublist in bit_rates_used for item in (sublist if isinstance(sublist, list) else [sublist])]
        gsnr_used = [item for sublist in gsnr_used for item in (sublist if isinstance(sublist, list) else [sublist])]

        if len(bit_rates_used) != len(gsnr_used):
            print(f"Errore: i dati per {strategy} non hanno la stessa lunghezza! ({len(bit_rates_used)} vs {len(gsnr_used)})")
            continue

        sorted_data = sorted(zip(gsnr_used, bit_rates_used), key=lambda x: x[0])
        gsnr_used, bit_rates_used = zip(*sorted_data) if sorted_data else ([], [])
        gsnr_used = list(gsnr_used)
        bit_rates_used = list(bit_rates_used)
        ax.plot(gsnr_used, bit_rates_used, linestyle='-', color=colors.get(strategy, 'black'), label=strategy)

        if gsnr_used and bit_rates_used:
            ax.text(gsnr_used[-1], bit_rates_used[-1], strategy, fontsize=12, color=colors[strategy],
                    verticalalignment='bottom', horizontalalignment='left')

    ax.set_title(f'Bit Rates vs GSNR for different transceivers ({label})', fontsize=14)
    ax.set_xlabel('GSNR (dB)', fontsize=12)
    ax.set_ylabel('Bit Rate (Gbps)', fontsize=12)
    ax.legend(title="Transceiver Strategies", loc="upper left", fontsize=10, title_fontsize=12)
    ax.grid(True)

    plt.savefig(os.path.join(output_folder, f'bit_rate_gsnr_{label}.png'))
    plt.show()
    plt.close(fig)

def has_converged(metric_history, threshold=0.05, min_iterations=5):
    if len(metric_history) < min_iterations:
        return False
    last_distribution = metric_history[-1]
    prev_distributions = metric_history[-min_iterations:]
    ks_values = [ks_2samp(last_distribution, prev)[1] for prev in prev_distributions]
    return all(p_value > threshold for p_value in ks_values)


