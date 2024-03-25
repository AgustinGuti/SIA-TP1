
# TP1 SIA - Métodos de Búsqueda

Trabajo práctico para la materia Sistemas de Inteligencia Artificial del ITBA con el objetivo de analizar distintos métodos de búsqueda y heurísticas para resolver el juegos Sokoban.

Alumnos: Agustín Andrés Gutiérrez, Ian Bernasconi y Jeremías Demián Feferovich
## Set up
Para ejecutar el motor de busquedas:
1. Instalación de librerias
 - ```pip install -r ./requirements.txt```
 - Correr `sudo apt-get install python3-tk` para instalar dependencias necesarias

1. Configuracion de mapas. Archivo `grid.json`
    - Se pueden especificar los mapas a resolver en una lista del atributo `active`, bajo elementos con el atributo `grid` como un arreglo de strings. Dentro de los strings, el `#` representa un obstaculo, el ` ` un espacio vacio, el `.` un objetivo, el `@` al jugador, el `$` a una caja y `:` a un objetivo con una caja arriba. Tambien requieren un atributo `name` para cada mapa.

2. Configuración. Archivo `config.json`
    - Elegir los algoritmos a correr editando el arreglo `algorithms`. Las opciones disponibles son `bfs`, `dfs`, `a_star` y `greedy`
    - Elegir la heurística a utilizar con el atributo `heuristic`. Los valores posibles son `1`, `2` y `3`
    - El atributo `repetitions` permite especificar el numero de iteraciones para cada algoritmo con cada mapa
    - El atributo `print_delta_time` permite configurar cada cuantos segundos se escribe por consola el tiempo que lleva ejecutando el algoritmo para el mapa actual.

3. Configuración de repeticion. Archivo `config.json`
    - Para activar las repeticiones, cambiar el atributo `enabled` de `replay`a `true`. 
    - El atributo `speed` indica la duración en segundos de cada paso.
    - El atributo `sequential` indica si las repeticiones se mostraran una detras de otra, o en paralelo en una grilla.
    - El atributo `paths` indica los archivos de los que se tomaran los resultados.

## Ejecución
- Para correr el código, ejecutar `python ./game.py`
- Para correr el análisis de resultados, ejecutar `python ./results.py`