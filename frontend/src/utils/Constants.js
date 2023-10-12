import _ from "lodash";

export const PROBLEMS = ["DDMOP2", "DTLZ2", "DTLZ3", "DTLZ7", "WFG2"];
export const METRICS = {
  IGD: {
    full: "Inverted Generational Distance",
    info: "The IGD metric inverts the generational distance and measures the distance from any point in reference points set to the closest point in objective vector set.",
    optimal: _.min,
  },
  HV: {
    full: "Hypervolume",
    info: "The volume of the region in the objective space enclosed by the non-dominated solution set obtained by the algorithm and the reference point.",
    optimal: _.max,
  },
  MS: {
    full: "Maximum Spread",
    info: "Maximum spread (MS) measures the range of a solution set by considering the maximum extent on each objective.",
    optimal: _.max,
  },
  SP: {
    full: "Spacing",
    info: "Spacing (SP) reflects the variation of the distance between solutions in a set.",
    optimal: _.min,
  },
};

export const METRIC_ND = "VIS_ND_indices";
export const METRIC_DIST = {
  origin: "IGD",
  target: "VIS_IGD_distr",
  bins: 50,
};

export const RUNS_SIM_DEFAULT = "IGD_dtw";
export const RUNS_SIM_METRICS = [
  { label: "Euclidean (IGD)", value: "IGD_euclidean" },
  { label: "Euclidean (HV)", value: "HV_euclidean" },
  { label: "Best IGD", value: "IGD_best_frame_sinkhorn" },
  { label: "Best HV", value: "HV_best_frame_sinkhorn" },
  { label: "DTW (IGD)", value: "IGD_dtw" },
  { label: "DTW (HV)", value: "HV_dtw" },
];
