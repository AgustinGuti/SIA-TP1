import json
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.ticker import FuncFormatter

def main():
    matplotlib.use('TkAgg')
    results = []
    for filename in glob.glob('results/*.json'):
        with open(filename, 'r') as f:
            results.append(json.load(f))

    df = pd.DataFrame(results)
    # Replace values in the 'algorithm' column
    # df['algorithm'] = df['algorithm'].replace({'a_star': 'A*', 'dfs': 'DFS', 'bfs': 'BFS', 'greedy': 'Greedy'})
    algorithms = []
    for algorithm in df['algorithm'].unique():
        if algorithm == 'a_star':
            algorithms.append('A*')
        elif algorithm == 'dfs':
            algorithms.append('DFS')
        elif algorithm == 'bfs':
            algorithms.append('BFS')
        elif algorithm == 'greedy':
            algorithms.append('Greedy')
        else:
            algorithms.append(algorithm)
    
    algorithms.reverse()

    # print(df)
    grouped = df.groupby(['name', 'algorithm'])
    ax = grouped['time'].mean().unstack().plot(kind='bar')
    ax.set_ylabel('Tiempo (s)')
    ax.set_title('Tiempo para resolver el problema')
    ax.legend(algorithms)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.2f}'))

    ax = grouped['cost'].mean().unstack().plot(kind='bar')
    ax.set_ylabel('Costo')
    ax.set_ylim(0, 150)
    ax.set_title('Costo para resolver el problema')
    ax.legend(algorithms)


    ax = grouped['expanded_nodes'].mean().unstack().plot(kind='bar')
    ax.set_ylabel('Nodos expandidos')
    ax.set_title('Nodos expandidos para resolver el problema')
    ax.legend(algorithms)

    # Now data relative with the "base case", taking the base case as the bfs equivalent
    # Filter the DataFrame and drop the columns
    base_case = df[df['algorithm'] == 'bfs']
    base_case = base_case.rename(columns={'cost': 'base_cost', 'time': 'base_time', 'expanded_nodes': 'base_expanded_nodes'})
    
    columns_to_keep = ['name', 'base_cost', 'base_time', 'base_expanded_nodes']
    base_case = base_case.drop(columns=base_case.columns.difference(columns_to_keep))

    df = df.merge(base_case, on='name')
    df['cost_relative'] = df['cost'] / df['base_cost']
    df['time_relative'] = df['time'] / df['base_time']
    df['expanded_nodes_relative'] = df['expanded_nodes'] / df['base_expanded_nodes']

    grouped_relative = df.groupby(['name', 'algorithm'])
    ax = grouped_relative['cost_relative'].mean().unstack().plot(kind='bar')
    ax.set_ylabel('Costo relativo')
    ax.set_ylim(0, 1.5)
    ax.legend(algorithms)
    ax.set_title('Costo en relación a BFS')

    ax = grouped_relative['time_relative'].mean().unstack().plot(kind='bar')
    ax.set_ylabel('Tiempo relativo')
    ax.legend(algorithms)
    ax.set_title('Tiempo en relación a BFS')

    ax = grouped_relative['expanded_nodes_relative'].mean().unstack().plot(kind='bar')
    ax.set_ylabel('Nodos expandidos')
    ax.legend(algorithms)
    ax.set_title('Nodos expandidos en relación a BFS')

    # relacion costo-tiempo
    df['cost_quality'] = 1 / ((df['cost'] * df['time']) )
    ax = df.groupby(['name', 'algorithm'])['cost_quality'].mean().unstack().plot(kind='bar')
    ax.set_ylabel('Calidad')
    ax.legend(algorithms)
    ax.set_title('Calidad del algoritmo')
    ax.set_yscale('log')


    plt.show()   
    

if __name__ == '__main__':
    main()