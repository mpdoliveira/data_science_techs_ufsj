import random
import math
import copy

# Carrega os dados
def load_data(path):
    data = []
    with open(path, "r") as file:
        next(file)
        for line in file:
            point_data = line.strip().split(",")
            point = [float(i) for i in point_data]
            data.append(point)
    return data

# Centroides iniciados aleatoriamente
def rand_centroids(data, K):
    centroids = []
    max_index = len(data) - 1
    while len(centroids) < K:
        rand = random.randint(0, max_index)
        if not rand in centroids:
            centroids.append(data[rand])
    return centroids

# Calculo de distancia ponto-centroide
def distance(pt1, pt2):
    result = 0
    for i in range(len(pt1)):
        result += (pt1[i] - pt2[i]) ** 2
    result = math.sqrt(result)

    return result

#Atualiza centroides 
def update_centroids(clusters, centroids):
    new_centroids = copy.deepcopy(centroids)
    for i in range(len(clusters)):
        if len(clusters[i]) != 0: 
            new = []

            #Calcula media geral
            for j in range(0, len(clusters[i][0])):
                sum = 0
                #Calcula media coordenada a coordenada
                for point in clusters[i]:
                    sum += point[j]
                sum /= len(clusters[i])

                new.append(round(sum, 2))

            new_centroids[i] = new
    return new_centroids

def KMeans(data, K, maxIterations):
    centroids = rand_centroids(data, K)
    iteration = 0
    updated = True

    # Itera até max ou até não haver melhora
    while iteration < maxIterations and updated:
        clusters = []
        for i in range(0, K):
            clusters.append([])

        # calcula centroid mais próximo e atribui ao respectivo cluster
        for point in data:
            shortest = math.inf
            cluster = -1

            for i in range(0, K):
                new_distance = distance(point, centroids[i])

                if new_distance < shortest:
                    shortest = new_distance
                    cluster = i

            clusters[cluster].append(point)

        # Atualiza centroides
        new_centroids = update_centroids(clusters, centroids)

        # Condição de parada caso não haja melhora
        if new_centroids == centroids:
            updated = False
        else:
            centroids = new_centroids
            iteration += 1

    return clusters, centroids

# Testes
print()
print("Teste 1.0")
data = load_data("dados_1_simples.csv")
clusters, centroids = KMeans(data, 5, 100)
print("Centroids - Clusters")
for i in range(len(clusters)):
    print(f"{centroids[i]} - {clusters[i]}")

print()
print("Teste 1.1")
data = load_data("dados_1_simples.csv")
clusters, centroids = KMeans(data, 3, 100)
print("Centroids - Clusters")
for i in range(len(clusters)):
    print(f"{centroids[i]} - {clusters[i]}")

print()
print("Teste 2.0")
data = load_data("dados_2_3clusters.csv");
clusters, centroids = KMeans(data, 5, 100)
print("Centroids - Clusters")
for i in range(len(clusters)):
    print(f"{centroids[i]} - {clusters[i]}")

print()
print("Teste 2.1")
data = load_data("dados_2_3clusters.csv");
clusters, centroids = KMeans(data, 3, 100)
print("Centroids - Clusters")
for i in range(len(clusters)):
    print(f"{centroids[i]} - {clusters[i]}")

print()
print("Teste 3.0")
data = load_data("dados_3_3d.csv")
clusters, centroids = KMeans(data, 5, 100)
print("Centroids - Clusters")
for i in range(len(clusters)):
    print(f"{centroids[i]} - {clusters[i]}")

print()
print("Teste 3.1")
data = load_data("dados_3_3d.csv")
clusters, centroids = KMeans(data, 3, 100)
print("Centroids - Clusters")
for i in range(len(clusters)):
    print(f"{centroids[i]} - {clusters[i]}")

print()
print("Teste 4.0")
data = load_data("dados_5_4d_120entradas.csv")
clusters, centroids = KMeans(data, 10, 100)
for i in range(len(clusters)):
    print()
    print(f"Centroids: {centroids[i]}")
    print(clusters[i])

print()
print("Teste 4.1")
data = load_data("dados_5_4d_120entradas.csv")
clusters, centroids = KMeans(data, 20, 100)
for i in range(len(clusters)):
    print()
    print(f"Centroids: {centroids[i]}")
    print(clusters[i])
    



