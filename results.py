import json
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os

def main():
    matplotlib.use('TkAgg')
    results = []
    for filename in glob.glob('results/*.json'):
        with open(filename, 'r') as f:
            results.append(json.load(f))

    df = pd.DataFrame(results)
    # Replace values in the 'algorithm' column
    df['algorithm'] = df['algorithm'].replace({'a_star': 'A*', 'dfs': 'DFS', 'bfs': 'BFS', 'greedy': 'Greedy'})

    algorithms = df['algorithm'].unique()
    algorithms.sort()
    os.makedirs("images", exist_ok=True)

    for name in df['name'].unique():
        df.loc[df['name'] == name, 'base_time'] = df[(df['algorithm'] == 'BFS') & (df['name'] == name)]['time'].mean()
        df.loc[df['name'] == name, 'base_cost'] = df[(df['algorithm'] == 'BFS') & (df['name'] == name)]['cost'].mean()
        df.loc[df['name'] == name, 'base_expanded_nodes'] = df[(df['algorithm'] == 'BFS') & (df['name'] == name)]['expanded_nodes'].mean()
        df.loc[df['name'] == name, 'base_frontier_nodes'] = df[(df['algorithm'] == 'BFS') & (df['name'] == name)]['frontier_nodes'].mean()

    for algorithm in algorithms:
        for name in df['name'].unique():
            df.loc[(df['algorithm'] == algorithm) & (df['name'] == name), 'time_relative'] = df[(df['algorithm'] == algorithm) & (df['name'] == name)]['time'].mean() / df[df['name'] == name]['base_time']
            df.loc[(df['algorithm'] == algorithm) & (df['name'] == name), 'cost_relative'] = df[(df['algorithm'] == algorithm) & (df['name'] == name)]['cost'].mean() / df[df['name'] == name]['base_cost']
            df.loc[(df['algorithm'] == algorithm) & (df['name'] == name), 'expanded_nodes_relative'] = df[(df['algorithm'] == algorithm) & (df['name'] == name)]['expanded_nodes'].mean() / df[df['name'] == name]['base_expanded_nodes']
            df.loc[(df['algorithm'] == algorithm) & (df['name'] == name), 'frontier_nodes_relative'] = df[(df['algorithm'] == algorithm) & (df['name'] == name)]['frontier_nodes'].mean() / df[df['name'] == name]['base_frontier_nodes']


    grouped = df.groupby(['algorithm'])

    #using grid A-2
    filtered = df[df['name'].str.startswith('A-2')]
    filtered = filtered[filtered['heuristic'] == 2]
    grouped = filtered.groupby(['algorithm'])

    plt.figure()
    plt.errorbar(grouped['expanded_nodes'].mean().index, grouped['expanded_nodes'].mean(), yerr=grouped['expanded_nodes'].std(), fmt='o', capsize=6)
    plt.ylabel('Nodos expandidos')
    plt.title('Nodos expandidos para resolver el problema en el mapa A-2')
    plt.savefig('images/expanded_nodes.png')

    plt.figure()
    plt.errorbar(grouped['frontier_nodes'].mean().index, grouped['frontier_nodes'].mean(), yerr=grouped['frontier_nodes'].std(), fmt='o', capsize=6)
    plt.ylabel('Nodos en frontera')
    plt.title('Nodos en frontera al resolver el problema en el mapa A-2')
    plt.savefig('images/frontier_nodes.png')

    # plt.figure()
    fig, ax = plt.subplots()
    for algorithm in algorithms:
        plt.errorbar(filtered[filtered['algorithm'] == algorithm]['cost'].mean(), 
             filtered[filtered['algorithm'] == algorithm]['time'].mean(), 
             yerr=filtered[filtered['algorithm'] == algorithm]['time'].std(), 
             fmt='o', label=algorithm, capsize=6)    
        
    plt.legend()
    ax.grid(which = "both")
    ax.minorticks_on() 
    plt.xlabel('Costo')
    plt.ylabel('Tiempo (s)')
    plt.title('Costo vs Tiempo para resolver el mapa A-2')
    plt.savefig('images/time_vs_cost.png')

    filtered = df[df['heuristic'] == 2]
    grouped = filtered.groupby(['algorithm'])

    fig, ax = plt.subplots()
    for algorithm in algorithms:
        plt.errorbar(filtered[filtered['algorithm'] == algorithm]['cost_relative'].mean(), 
             filtered[filtered['algorithm'] == algorithm]['time_relative'].mean(), 
             fmt='o', label=algorithm, capsize=6)    
    plt.legend()
    ax.grid(which = "both")
    ax.minorticks_on() 
    plt.xlabel('Costo relativo')
    plt.ylabel('Tiempo relativo')
    plt.title('Promedio del costo relativo vs Tiempo relativo para resolver el problema en todos los mapas')
    plt.savefig('images/time_vs_cost_relative.png')


    plt.figure()
    mean = grouped['frontier_nodes_relative'].mean()
    plt.errorbar(mean.index, mean, fmt='o', capsize=6)
    plt.ylabel('Nodos en frontera relativos')
    plt.title('Promedio de nodos en frontera relativos al resolver el problema en todos los mapas')
    plt.savefig('images/frontier_nodes_average.png')

    plt.figure()
    mean = grouped['expanded_nodes_relative'].mean()
    plt.errorbar(mean.index, mean, fmt='o', capsize=6)
    plt.ylabel('Nodos expandidos relativos')
    plt.title('Promedio de nodos expandidos relativos al resolver el problema en todos los mapas')
    plt.savefig('images/expanded_nodes_average.png')

    
    k = 1
    m = 1
    p_values = [_ for _ in range(1, 100)]

    plt.figure()
    quality_values = {}
    for algorithm in algorithms:
        for p_val in p_values:
            filtered.loc[(filtered['algorithm'] == algorithm), 'quality'] = (k*(1-filtered['cost_relative']) + p_val*(1-filtered['time_relative']) + m*(1-filtered['frontier_nodes_relative']))
            if algorithm not in quality_values:
                quality_values[algorithm] = []
            quality_values[algorithm].append(filtered[filtered['algorithm'] == algorithm]['quality'].mean())

    for algorithm, values in quality_values.items():
        plt.plot(p_values, values, '-', label=algorithm)

    plt.xlabel('Importancia del tiempo')
    plt.ylabel('Calidad')
    plt.legend()
    plt.title('Calidad de los algoritmos al aumentar la importancia del tiempo')
    plt.savefig('images/quality_time.png')

    p = 1
    m = 1
    k_values = [_ for _ in range(1,10)]

    plt.figure()
    quality_values = {}
    for algorithm in algorithms:
        for k_val in k_values:
            filtered.loc[(filtered['algorithm'] == algorithm), 'quality'] = (k_val*(1-filtered['cost_relative']) + p*(1-filtered['time_relative']) + m*(1-filtered['frontier_nodes_relative']))
            if algorithm not in quality_values:
                quality_values[algorithm] = []
            quality_values[algorithm].append(filtered[filtered['algorithm'] == algorithm]['quality'].mean())

    for algorithm, values in quality_values.items():
        plt.plot(k_values, values, '-', label=algorithm)

    plt.xlabel('Importancia del costo')
    plt.ylabel('Calidad')
    plt.ylim(-50, 1)
    plt.legend()
    plt.title('Calidad de los algoritmos al aumentar la importancia del costo')
    plt.savefig('images/quality_cost.png')

    p = 1
    k = 1
    m_values = [_ for _ in range(1,10)]

    plt.figure()
    quality_values = {}
    for algorithm in algorithms:
        for m_val in m_values:
            filtered.loc[(filtered['algorithm'] == algorithm), 'quality'] = (k*(1-filtered['cost_relative']) + p*(1-filtered['time_relative']) + m_val*(1-filtered['frontier_nodes_relative']))
            if algorithm not in quality_values:
                quality_values[algorithm] = []
            quality_values[algorithm].append(filtered[filtered['algorithm'] == algorithm]['quality'].mean())
        
    for algorithm, values in quality_values.items():
        plt.plot(m_values, values, '-', label=algorithm)

    plt.xlabel('Importancia de la memoria necesaria')
    plt.ylabel('Calidad')
    plt.legend()
    plt.title('Calidad de los algoritmos al aumentar la importancia de la memoria necesaria')
    plt.savefig('images/quality_memory.png')

    # Now only greedy algorithm
    filtered = df[df['algorithm'] == 'Greedy']

    # Only map A-2
    filtered = filtered[filtered['name'].str.startswith('A-3')]

    fig, ax = plt.subplots()
    # TODO change labels?
    labels = {
        1: "Mas cercano",
        2: "Asignados",
        3: "Mas lejano"
    }
    for heuristic in filtered['heuristic'].unique():
        plt.errorbar(filtered[filtered['heuristic'] == heuristic]['cost'].mean(), 
             filtered[filtered['heuristic'] == heuristic]['time'].mean(), 
             yerr=filtered[filtered['heuristic'] == heuristic]['time'].std(), 
             fmt='o', label=labels[heuristic], capsize=6)    
        
    plt.legend()
    ax.grid(which = "both")
    ax.minorticks_on()
    plt.xlabel('Costo')
    plt.ylabel('Tiempo (s)')
    plt.title('Costo vs Tiempo según heuristica para resolver el mapa A-3 con algoritmo Greedy')
    plt.savefig('images/cost_time_heuristic.png')

    
    plt.show()   
    

if __name__ == '__main__':
    main()