import networkx as nx
import numpy as np
import hdbscan
from sklearn.neighbors import NearestNeighbors


DataMatrix = list[list[dict]]


def dict_to_matrix(data: dict) -> np.ndarray:
  len_data = len(data)
  res = np.zeros((len_data, len_data))
  for i, k in enumerate(data.values()):
    for j, v in enumerate(k.values()):
      res[i, j] = v
  return res


def get_cluster(matrix) -> list[int]:
  clusterer = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=1)
  clusterer.fit(matrix)
  return clusterer.labels_.tolist()


def calc_graph(data: DataMatrix, name: list[str]) -> dict:
  mat_data = [[dict_to_matrix(j) for j in i] for i in data]
  mat_data = np.concatenate(tuple([np.concatenate(tuple(i), axis=1) for i in mat_data]), axis=0)

  nodes, edges = [], []

  for i in range(len(data)):
    for it in data[i][0].keys():
      nodes.append({ 'name': name[i], 'frame': it })

  old_edges = []
  nbrs = NearestNeighbors(n_neighbors=11).fit(mat_data)
  for k in range(2, 12):
    indices = nbrs.kneighbors(mat_data, n_neighbors=k, return_distance=False)
    for u in range(mat_data.shape[0]):
      for v in np.delete(indices[u], np.where(indices[u] == u)):
        v = int(v)
        if (v, u) not in old_edges:
          edges.append([v, u, k-1])
          old_edges.append((v, u))

  graph = nx.Graph()
  graph.add_nodes_from(np.arange(mat_data.shape[0]).tolist())
  graph.add_edges_from(old_edges)
  pos = nx.kamada_kawai_layout(graph)
  for i, p in enumerate(pos.values()):
    nodes[i]['pos'] = p.tolist()

  clusters = get_cluster(mat_data)

  return { 'nodes': nodes, 'edges': edges, 'clusters': clusters }