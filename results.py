import json
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

def main():
    matplotlib.use('TkAgg')
    results = []
    for filename in glob.glob('results/*_3.json'):
        with open(filename, 'r') as f:
            results.append(json.load(f))

    df = pd.DataFrame(results)
    # Replace values in the 'algorithm' column
    df['algorithm'] = df['algorithm'].replace({'a_star': 'A*', 'dfs': 'DFS', 'bfs': 'BFS', 'greedy': 'Greedy'})


    grouped = df.groupby(['algorithm'])

    # Plot mean values as points with error bars
    plt.errorbar(grouped['time'].mean().index, grouped['time'].mean(), yerr=grouped['time'].std(), fmt='o', capsize=6)
    plt.ylabel('Tiempo (s)')
    plt.title('Tiempo para resolver el problema')

    plt.figure()
    plt.errorbar(grouped['cost'].mean().index, grouped['cost'].mean(), yerr=grouped['cost'].std(), fmt='o', capsize=6)
    plt.ylabel('Costo')
    plt.yscale('log')
    plt.title('Costo para resolver el problema')

    plt.figure()
    plt.errorbar(grouped['expanded_nodes'].mean().index, grouped['expanded_nodes'].mean(), yerr=grouped['expanded_nodes'].std(), fmt='o', capsize=6)
    plt.ylabel('Nodos expandidos')
    plt.title('Nodos expandidos para resolver el problema')

    plt.figure()
    plt.errorbar(grouped['frontier_nodes'].mean().index, grouped['frontier_nodes'].mean(), yerr=grouped['frontier_nodes'].std(), fmt='o', capsize=6)
    plt.ylabel('Nodos en frontera')
    plt.title('Nodos en frontera al resolver el problema')
    
    # Plot function of cost vs time
    # plt.figure()
    

    # # Now data relative with the "base case", taking the base case as the bfs equivalent
    # # Filter the DataFrame and drop the columns
    base_case = df[df['algorithm'] == 'BFS']
    base_case = base_case.rename(columns={'cost': 'base_cost', 'time': 'base_time', 'expanded_nodes': 'base_expanded_nodes'})
    
    columns_to_keep = ['name', 'base_cost', 'base_time', 'base_expanded_nodes']
    base_case = base_case.drop(columns=base_case.columns.difference(columns_to_keep))

    df = df.merge(base_case, on='name')
    df['cost_relative'] = df['cost'] / df['base_cost']
    df['time_relative'] = df['time'] / df['base_time']
    df['expanded_nodes_relative'] = df['expanded_nodes'] / df['base_expanded_nodes']

    grouped = df.groupby(['algorithm'])


    # relacion costo-tiempo
    df['cost_quality'] = 1 / ((df['cost'] * df['time'] * df['frontier_nodes']/100))
    plt.figure()    
    for algorithm in df['algorithm'].unique():
        plt.plot(df['name'].unique(), df[df['algorithm'] == algorithm]['cost_quality'], label=algorithm)
    plt.legend()
    plt.ylabel('Calidad')
    plt.title('Calidad del algoritmo')
    # grouped = df.groupby(['algorithm'])
    # plt.figure()
    # plt.errorbar(grouped['cost_quality'].mean().index, grouped['cost_quality'].mean(), yerr=grouped['cost_quality'].std(), fmt='o', capsize=6)
    # plt.ylabel('Calidad')
    # plt.title('Calidad del algoritmo')

    grouped = df.groupby(['algorithm'])
    plt.figure()
    plt.errorbar(grouped['cost_quality'].mean().index, grouped['cost_quality'].mean(), yerr=grouped['cost_quality'].std(), fmt='o', capsize=6)
    plt.ylabel('Calidad')
    plt.xlabel('Complejidad del mapa')
    plt.gca().set_xticklabels([])
    plt.title('Calidad del algoritmo')

    # Costo de la solucion en funcion de la cantidad de objetivos en una grilla
    plt.figure()
    # I want to drop columns that dont start with A-
    # df = df[(df['algorithm'] != 'DFS')]
    df = df[df['name'].str.startswith('A-')]
    df['objectives_qty'] = df['name'].apply(lambda x: int(x.split('-')[1]))
    df = df.sort_values(by='objectives_qty')
    for algorithm in df['algorithm'].unique():
        plt.plot(df['objectives_qty'].unique(), df[df['algorithm'] == algorithm]['cost'], '-o', label=algorithm)
    plt.ylabel('Costo')
    plt.xlabel('Cantidad de objetivos en la grilla')
    plt.xticks(df['objectives_qty'].unique())
    plt.yscale('log')
    plt.legend()
    plt.title('Costo en funcion de la cantidad de objetivos en la grilla')

    # Tiempo de ejecucion en funcion de la cantidad de objetivos en una grilla
    plt.figure()
    for algorithm in df['algorithm'].unique():
        plt.plot(df['objectives_qty'].unique(), df[df['algorithm'] == algorithm]['time'], '-o', label=algorithm)
    plt.ylabel('Tiempo (s)')
    plt.xlabel('Cantidad de objetivos en la grilla')
    plt.xticks(df['objectives_qty'].unique())
    plt.legend()
    plt.title('Tiempo en funcion de la cantidad de objetivos en la grilla')



    # comparing the quality of the heuristics
    results = []
    for filename in glob.glob('results/replay_*_greedy_*.json'):
        with open(filename, 'r') as f:
            results.append(json.load(f))

    df = pd.DataFrame(results)
    df = df[(df['algorithm'] != 'dfs') & (df['algorithm'] != 'bfs')]

    df['algorithm'] = df['algorithm'].replace({'a_star': 'A*', 'greedy': 'Greedy'})

    plt.figure()
    grouped = df.groupby(['heuristic'])
    plt.errorbar(grouped['cost'].mean().index, grouped['cost'].mean(), yerr=grouped['cost'].std(), fmt='o', capsize=6)
    plt.ylabel('Costo')
    plt.xlabel('Heuristica')
    plt.xticks([1,2,3])
    plt.title('Costo para resolver el problema')

    plt.figure()
    plt.errorbar(grouped['time'].mean().index, grouped['time'].mean(), yerr=grouped['time'].std(), fmt='o', capsize=6)
    plt.ylabel('Tiempo (s)')
    plt.xlabel('Heuristica')
    plt.xticks([0,1,2,3,4])
    plt.title('Tiempo para resolver el problema')

    df['cost_quality'] = 1 / ((df['cost'] * df['time']) * df['frontier_nodes']/100)

    plt.figure()
    plt.errorbar(grouped['cost_quality'].mean().index, grouped['cost_quality'].mean(), yerr=grouped['cost_quality'].std(), fmt='o', capsize=6)
    plt.ylabel('Calidad')
    plt.xlabel('Heuristica')
    plt.xticks([0,1,2,3,4])
    plt.title('Calidad del algoritmo')

    # Conclusion parcial: una heuristica no adecuada es mejor que una adecuada en algunos casos
    # CUIDADO, en A y B muestran una tendencia, pero C y D son distintas. Ver de graficar distinto
    
    plt.show()   
    

if __name__ == '__main__':
    main()