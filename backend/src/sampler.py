import numpy as np
from utils.sampling import *
from sklearn.neighbors import LocalOutlierFactor


def sampler(algoData, originData, sampling_rate):
    all_solutions_data = []
    all_solutions_class = []
    outlier = np.array([])
    for index, (_, data) in enumerate(originData.items()):
        outlier = np.concatenate(
            (outlier, LocalOutlierFactor().fit_predict(data)))
    for index, (_, data) in enumerate(algoData.items()):
        all_solutions_data += data
        all_solutions_class += [index] * len(data)
    outlier_indices = np.where(outlier == -1)[0]
    indices = np.zeros(len(all_solutions_data))
    if sampling_rate == 0:
        return indices
    if sampling_rate == 1:
        indices = np.ones(len(all_solutions_data))
        indices[outlier_indices] = -1
        return indices
    selected_indices = OutlierBiasedDensityBasedSampling(
        np.array(all_solutions_data),
        np.array(all_solutions_class),
        sampling_rate
    )
    indices[selected_indices] = 1
    indices[outlier_indices] = -1
    return indices
