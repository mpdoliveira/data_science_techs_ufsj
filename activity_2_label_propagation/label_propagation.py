import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def read_matrix(nome_arquivo):
    # carrega o grafo a partir do arquivo
    graph = nx.read_edgelist(
        nome_arquivo,
        delimiter=",",
        nodetype=int
    )

    vertices = sorted(graph.nodes())

    # converte o grafo para matriz de adjacência
    matrix = nx.to_numpy_array(
        graph,
        nodelist=vertices
    )

    return matrix


# inicializa os rótulos aleatoriamente
def init_label(matrix):
    n = len(matrix)

    labels = np.array([i for i in range(n)])

    return labels


# retorna uma ordem aleatória dos vértices
def rand_vertices(vertices):
    vertices = np.array(vertices)

    np.random.shuffle(vertices)

    return vertices


# retorna os vizinhos do vértice i
def get_neighbors(i, matrix):
    neighbors = np.where(matrix[i] == 1)[0]

    return neighbors


# retorna a moda dos rótulos mais frequente
def label_mode(labels):
    if len(labels) == 0:
        return None

    unique_labels, counts = np.unique(labels, return_counts=True)

    max_count = np.max(counts)

    # rótulos de maior frequência
    candidates = unique_labels[counts == max_count]

    # escolha aleatória em caso de empate
    return random.choice(candidates.tolist())


def label_propagation(matrix, max_iterations):
    vertices = len(matrix)

    labels = init_label(matrix)

    iteration = 0
    changed = True

    while iteration < max_iterations and changed:

        changed = False

        order_vertices = rand_vertices(range(vertices))

        for i in order_vertices:

            # obtém os vizinhos
            neighbors = get_neighbors(i, matrix)

            if len(neighbors) > 0:

                # obtém os rótulos dos vizinhos
                neighbor_labels = labels[neighbors]

                # encontra a moda
                new_label = label_mode(neighbor_labels)

                # atualiza o rótulo
                if new_label != labels[i]:
                    labels[i] = new_label
                    changed = True

        iteration += 1

    return labels


def print_matrix(matrix, labels):
    n = len(matrix)

    row_width = max(len(str(n - 1)), len(str(np.max(labels)))) + 5

    # cabeçalho
    print(" " * row_width, end="")

    for j in range(n):
        print(f"{j:>2}", end=" ")

    print()

    print(" " * row_width + "-" * (3 * n))

    # matriz
    for i in range(n):

        row_name = f"{i}({labels[i]})"

        print(f"{row_name:>{row_width}} |", end=" ")

        for j in range(n):
            print(f"{int(matrix[i, j])}", end="  ")

        print()

    print()

def plot_graph(matrix, labels):
    graph = nx.from_numpy_array(matrix)

    nx.draw(
        graph,
        nx.spring_layout(graph, seed=40),
        with_labels=True,
        node_color=labels,
        cmap="tab20",
        node_size=500,
        font_size=10
    )

    plt.show()


def run(path):
    matrix = read_matrix(path)

    labels = label_propagation(matrix, 100)


    print_matrix(matrix, labels)

    plot_graph(matrix, labels)

run("rede1_duas_comunidades.csv")
run("rede2.csv")
run("zachary.csv")