import numpy as np
from sklearn.neighbors import NearestNeighbors


def OutlierBiasedDensityBasedSampling(data, category, sampling_rate):
    np.random.seed(0)
    alpha = 1
    beta = 1
    outlier_score = get_default_outlier_scores(data, category)
    X = np.array(data.tolist(), dtype=np.float64)
    n, d = X.shape
    m = round(n * sampling_rate)
    k = 50
    dist, _ = NearestNeighbors(n_neighbors=k + 2, p=2).fit(X).kneighbors(X)
    radius_of_k_neighbor = dist[:, -1]
    maxD = np.max(radius_of_k_neighbor)
    minD = np.min(radius_of_k_neighbor)
    for i in range(len(radius_of_k_neighbor)):
        radius_of_k_neighbor[i] = (
            (radius_of_k_neighbor[i] - minD) * 1.0 / (maxD - minD)) * 0.5 + 0.5
    prob = alpha * radius_of_k_neighbor + beta * outlier_score
    prob = prob / prob.sum()
    selected_indexes = np.random.choice(n, m, replace=False, p=prob)
    return selected_indexes


def get_default_outlier_scores(data, category, k=50):
    X = np.array(data.tolist(), dtype=np.float64)
    n, d = X.shape
    if k + 1 > n:
        k = int((n - 1) / 2)
    _, neighbor = NearestNeighbors(n_neighbors=k + 2, p=2).fit(X).kneighbors(X)
    neighbor_labels = category[neighbor]
    outlier_score = [sum(neighbor_labels[i] != category[i])
                     for i in range(data.shape[0])]
    outlier_score = np.array(outlier_score) / k
    return outlier_score
