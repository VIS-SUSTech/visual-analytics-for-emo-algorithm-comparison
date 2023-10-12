<template>
  <div class="content">
    <div class="sub-content" style="flex-basis: 36%">
      <div
        class="sub-content"
        style="flex-basis: calc(40% - var(--title-height)); flex-direction: row"
      >
        <div class="sub-content" style="flex-basis: 50%">
          <div class="sub-content" style="flex-basis: var(--title-height)">
            <DiyCard class="view title" :float="true">
              <h4>Statistical Overview</h4>
              <n-config-provider
                :theme-overrides="themeOverrides"
                preflight-style-disabled
              >
                <n-space size="small" align="center">
                  Test Problem
                  <n-tooltip placement="bottom" trigger="hover">
                    <template #trigger>
                      <n-select
                        size="tiny"
                        v-model:value="selectedProblem"
                        :options="getNaiveSelectItems(PROBLEMS)"
                        :loading="loading"
                        :disabled="loading"
                        style="width: 5vw"
                      />
                    </template>
                    Change the Problem Set
                  </n-tooltip>
                </n-space>
              </n-config-provider>
            </DiyCard>
          </div>
          <div
            class="sub-content"
            style="flex-basis: calc(30% - var(--title-height))"
          >
            <DiyCard class="view" :float="true">
              <GeneralView :problem="selectedProblem" />
            </DiyCard>
          </div>
          <div class="sub-content" style="flex-basis: 70%">
            <DiyCard class="view" :float="true" style="position: relative">
              <InfoGridView
                v-if="!_.isEmpty(activeProblem)"
                :info-grid="infoGrid"
                :selected-algorithms="selectedAlgorithms"
                @select="selectAlgorithm"
              />
            </DiyCard>
          </div>
        </div>
        <div class="sub-content" style="flex-basis: 50%">
          <div class="sub-content" style="flex-basis: var(--title-height)">
            <DiyCard class="view title" :float="true">
              <h4>Algorithm Similarity View</h4>
              <n-config-provider
                :theme-overrides="themeOverrides"
                preflight-style-disabled
              >
                <n-space size="small" align="center">
                  Measure
                  <n-tooltip placement="bottom" trigger="hover">
                    <template #trigger>
                      <n-select
                        size="tiny"
                        :options="RUNS_SIM_METRICS"
                        :loading="loading"
                        :disabled="loading"
                        v-model:value="runsSimMetric"
                        placeholder="Select a Metric"
                        style="width: 5.5vw"
                      />
                    </template>
                    Change the Metric to Layout Algorithms
                  </n-tooltip>
                </n-space>
              </n-config-provider>
            </DiyCard>
          </div>
          <div
            class="sub-content"
            style="flex-basis: calc(100% - var(--title-height))"
          >
            <DiyCard
              class="view"
              :float="true"
              style="position: relative; flex-direction: column"
            >
              <RunsSimilarityView
                v-if="!_.isEmpty(RunsSimilarityData)"
                :data="RunsSimilarityData"
                :selected-algorithms="selectedAlgorithms"
                :layout-metric="runsSimMetric"
                @select="selectAlgorithm"
              />
            </DiyCard>
          </div>
        </div>
      </div>
      <div class="sub-content" style="flex-basis: var(--title-height)">
        <DiyCard class="view title" :float="true">
          <h4>Quality Measure View</h4>
          <n-config-provider
            :theme-overrides="themeOverrides"
            preflight-style-disabled
          >
            <n-space size="small" align="center">
              Select Generation by Hovering
              <n-tooltip placement="right" trigger="hover">
                <template #trigger>
                  <n-switch
                    size="small"
                    v-model:value="focusMode"
                    :disabled="loading"
                    :loading="loading"
                    :round="false"
                  />
                </template>
                {{ focusMode ? "Allow" : "Disallow" }} Focusing on Hovered Run
              </n-tooltip>
            </n-space>
          </n-config-provider>
        </DiyCard>
      </div>
      <div class="sub-content" style="flex-basis: 60%">
        <div
          v-for="({ full, info }, name) in METRICS"
          :key="name"
          class="sub-content"
          style="flex-basis: 25%; flex-direction: row"
        >
          <div
            class="sub-content"
            style="flex-basis: var(--title-height); width: 0"
          >
            <DiyCard class="view metric-name" :float="true">
              <h4>{{ name }}</h4>
              <n-config-provider
                :theme-overrides="themeOverrides"
                preflight-style-disabled
              >
                <n-popover
                  placement="right-end"
                  trigger="hover"
                  style="max-width: 10vw"
                >
                  <template #trigger>
                    <n-icon :component="InfoCircle" size="var(--font-size-l)" />
                  </template>
                  <div class="large-text">
                    <h4 style="margin: 0">{{ full }}</h4>
                    <br />
                    {{ info }}
                  </div>
                </n-popover>
              </n-config-provider>
            </DiyCard>
          </div>
          <div
            class="sub-content"
            style="flex-basis: calc(100% - var(--title-height))"
          >
            <DiyCard class="view" :float="true">
              <MetricsView
                v-if="!_.isEmpty(activeProblem)"
                @locate-frame="scrollToSN"
                :focus-mode="focusMode"
                :metrics="metricsData(name)"
                :name="name"
              />
            </DiyCard>
          </div>
        </div>
      </div>
    </div>
    <div class="sub-content" style="flex-basis: 64%">
      <div
        class="sub-content"
        style="flex-basis: calc(55% - var(--title-height)); flex-direction: row"
      >
        <div class="sub-content" style="flex-basis: 44%">
          <div class="sub-content" style="flex-basis: var(--title-height)">
            <DiyCard class="view title" :float="true">
              <h4>Generation Similarity View</h4>
              <n-config-provider
                :theme-overrides="themeOverrides"
                preflight-style-disabled
              >
                <n-space align="center" size="small">
                  <span v-if="!_.isEmpty(activeGraphs)">Curve</span>
                  <n-tooltip
                    v-for="name in activeGraphs"
                    :key="`time-curve-switch-${name}`"
                    trigger="hover"
                    placement="bottom"
                  >
                    <template #trigger>
                      <n-checkbox
                        :checked="_.includes(activeTimeCurve, name)"
                        :style="`
                          --n-color-checked: ${
                            colors[activeProblem[name].color][1]
                          };
                          --fill-color: ${colors[activeProblem[name].color][0]};
                          --border-color: ${
                            colors[activeProblem[name].color][2]
                          };
                        `"
                        :on-update:checked="() => showTimeCurve(name)"
                        size="small"
                      />
                    </template>
                    <span v-if="_.includes(activeTimeCurve, name)">
                      Hid the Time-Curve of {{ name }}
                    </span>
                    <span v-else> Show the Time-Curve of {{ name }} </span>
                  </n-tooltip>
                  <n-divider v-if="!_.isEmpty(activeGraphs)" vertical />
                  #Edge
                  <n-popover placement="bottom" trigger="hover">
                    <template #trigger>
                      <h4 style="width: 1vw; text-align: center">
                        {{ knnOption.limit }}
                      </h4>
                    </template>
                    <n-space size="small" vertical>
                      <div class="option-item">
                        <span style="flex-grow: 1">KNN Limit</span>
                        <n-slider
                          v-model:value="knnOption.limit"
                          :min="0"
                          :max="10"
                          :disabled="loading"
                          style="padding: 0; width: 3vw"
                        />
                      </div>
                      <div class="option-item">
                        <span style="flex-grow: 1">Neighbour Ring</span>
                        <n-switch
                          size="small"
                          v-model:value="knnOption.showArc"
                          :disabled="loading"
                          :loading="loading"
                          :round="false"
                        />
                      </div>
                    </n-space>
                  </n-popover>
                  <n-divider vertical />
                  Size
                  <n-tooltip placement="bottom" trigger="hover">
                    <template #trigger>
                      <n-select
                        size="tiny"
                        v-model:value="sizeAsMetric"
                        :options="getNaiveSelectItems(_.keys(METRICS))"
                        :loading="loading"
                        :disabled="loading"
                        style="width: 3vw"
                      />
                    </template>
                    Select a Metric Mapping to Node Size
                  </n-tooltip>
                  <n-divider vertical />
                  Cluster
                  <n-tooltip placement="right" trigger="hover">
                    <template #trigger>
                      <n-switch
                        size="small"
                        :value="layoutMode === 'cluster'"
                        :on-update:value="
                          (changed) =>
                            (layoutMode = changed ? 'cluster' : 'normal')
                        "
                        :disabled="loading"
                        :loading="loading"
                        :round="false"
                      />
                    </template>
                    {{ layoutMode === "cluster" ? "Enable" : "Disable" }}
                    Cluster Display
                  </n-tooltip>
                </n-space>
              </n-config-provider>
            </DiyCard>
          </div>
          <div
            class="sub-content"
            style="flex-basis: calc(100% - var(--title-height))"
          >
            <DiyCard class="view" :float="true">
              <CorrelationView
                v-if="!_.isEmpty(activeProblem)"
                @locate-frame="scrollToSN"
                :data="graphsData"
                :active-time-curve="activeTimeCurve"
                :metric-name="sizeAsMetric"
                :knn-option="knnOption"
                :layout-mode="layoutMode"
              />
            </DiyCard>
          </div>
        </div>
        <div class="sub-content" style="flex-basis: 56%">
          <div class="sub-content" style="flex-basis: var(--title-height)">
            <DiyCard class="view title" :float="true">
              <h4>Solution Set View</h4>
              <n-config-provider
                :theme-overrides="themeOverrides"
                preflight-style-disabled
              >
                <n-space align="center" size="small">
                  Scatter Sampling Rate
                  <n-slider
                    v-model:value="samplingRate"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    :disabled="loading"
                    style="
                      width: 3vw;
                      padding: 0;
                      --n-rail-color: var(--color-light);
                      --n-rail-color-hover: var(--color-light);
                    "
                  />
                  <h4 style="width: 1vw; text-align: center">
                    {{ samplingRate }}
                  </h4>
                  <n-divider vertical />
                  Reference Set Style
                  <n-tooltip
                    v-for="mode in ['scatter', 'contour', 'hull', 'none']"
                    :key="`${mode}-reference-style`"
                    placement="bottom-end"
                    trigger="hover"
                  >
                    <template #trigger>
                      <n-tag
                        size="small"
                        :checked="referenceStyle === mode"
                        :on-update:checked="() => (referenceStyle = mode)"
                        :loading="loading"
                        :disabled="loading"
                        checkable
                      >
                        {{ _.capitalize(mode) }}
                      </n-tag>
                    </template>
                    Switch to Display in {{ _.capitalize(mode) }} Style
                  </n-tooltip>
                </n-space>
              </n-config-provider>
            </DiyCard>
          </div>
          <div
            class="sub-content"
            style="
              flex-basis: calc(100% - var(--title-height));
              flex-direction: row;
            "
          >
            <div class="sub-content" style="flex-basis: 22%">
              <DiyCard
                class="view"
                :float="true"
                style="flex-direction: column; overflow-y: auto"
              >
                <div
                  v-for="({ image, iter, color, out }, name) in activeData"
                  class="selected-frame"
                  :key="`selected-frame-${name}`"
                  :style="`--frame-color: ${colors[color][1]}`"
                >
                  <div style="display: flex; align-items: center">
                    <span
                      style="
                        flex-grow: 1;
                        display: flex;
                        flex-direction: column;
                      "
                    >
                      <span style="font-weight: bold">{{ name }}</span>
                      Gen. Sample #{{
                        _.indexOf(_.keys(algorithmsData[name].frames), iter) + 1
                      }}
                    </span>
                    <n-config-provider
                      :theme-overrides="themeOverrides"
                      style="align-items: center; display: flex"
                      preflight-style-disabled
                    >
                      <n-tooltip v-if="out" placement="right" trigger="hover">
                        <template #trigger>
                          <n-icon :component="Exclamation" />
                        </template>
                        Solutions Out of Default Viewport Detected
                      </n-tooltip>
                      <n-tooltip placement="right" trigger="hover">
                        <template #trigger>
                          <n-button
                            size="small"
                            @click="() => cancelData(name)"
                            :style="`
                              --n-text-color: ${colors[color][1]};
                              --n-text-color-hover: ${colors[color][0]};
                              --n-text-color-pressed: ${colors[color][2]};
                              --n-text-color-focus: ${colors[color][1]};
                            `"
                            text
                          >
                            <template #icon>
                              <n-icon :component="TrashAltRegular" />
                            </template>
                          </n-button>
                        </template>
                        Remove this Solution Set
                      </n-tooltip>
                    </n-config-provider>
                  </div>
                  <img :src="image" style="width: 100%" />
                </div>
              </DiyCard>
            </div>
            <div class="sub-content" style="flex-basis: 78%">
              <DiyCard class="view" :float="true">
                <SolutionsView
                  v-if="!_.isEmpty(activeProblem)"
                  @frame-out-box="
                    (frames) =>
                      _.each(frames, (out, name) =>
                        _.set(activeData, [name, 'out'], out)
                      )
                  "
                  :data="activeData"
                  :PF="activeProblem.PF"
                  :reference-style="referenceStyle"
                  :sampling-rate="samplingRate"
                  :pf-cluster="pfCluster"
                  :problem="selectedProblem"
                />
              </DiyCard>
            </div>
          </div>
        </div>
      </div>
      <div class="sub-content" style="flex-basis: var(--title-height)">
        <DiyCard class="view title" :float="true">
          <h4>Timeline View</h4>
          <n-config-provider preflight-style-disabled>
            <n-config-provider
              :theme-overrides="themeOverrides"
              preflight-style-disabled
            >
              <n-space align="center" size="small">
                {{ METRIC_DIST.origin }} Distribution Scale
                <n-tooltip
                  v-for="mode in ['linear', 'sqrt']"
                  :key="`${mode}-scale-style`"
                  placement="bottom-end"
                  trigger="hover"
                >
                  <template #trigger>
                    <n-tag
                      size="small"
                      :checked="scaleXStyle === mode"
                      :on-update:checked="() => (scaleXStyle = mode)"
                      :loading="loading"
                      :disabled="loading"
                      checkable
                    >
                      {{ _.capitalize(mode) }}
                    </n-tag>
                  </template>
                  Use {{ _.capitalize(mode) }} Scaler for Axis X
                </n-tooltip>
              </n-space>
            </n-config-provider>
          </n-config-provider>
        </DiyCard>
      </div>
      <div class="sub-content" style="flex-basis: 45%">
        <DiyCard class="view" :float="true" style="overflow-y: auto">
          <SequentialView
            v-if="!_.isEmpty(activeProblem)"
            @select="selectData"
            @cancel="cancelData"
            @graph="selectGraph"
            :PF="activeProblem.PF"
            :algorithms="algorithmsData"
            :metrics="algorithmMetrics"
            :active-data="activeData"
            :graph-target="activeGraphs"
            :scale-x-style="scaleXStyle"
            :scrollControl="scrollControl"
          />
        </DiyCard>
      </div>
    </div>
  </div>
</template>

<script setup>
// Requirements
import { ref, watch, computed } from "vue";
import _ from "lodash";
import {
  NConfigProvider,
  NSelect,
  NTooltip,
  NPopover,
  NSlider,
  NSpace,
  NTag,
  NCheckbox,
  NButton,
  NSwitch,
  NDivider,
  NIcon,
} from "naive-ui";
import { InfoCircle, TrashAltRegular, Exclamation } from "@vicons/fa";

// Views
import GeneralView from "./views/GeneralView.vue";
import SolutionsView from "./views/SolutionsView.vue";
import MetricsView from "./views/MetricsView.vue";
import SequentialView from "./views/SequentialView.vue";
import CorrelationView from "./views/CorrelationView.vue";
import InfoGridView from "./views/InfoGridView.vue";
import RunsSimilarityView from "./views/RunsSimilarityView.vue";

// Components
import DiyCard from "./components/DiyCard.vue";

// Tools
import { getData, getGraph, getAttachment } from "./utils/Network";
import { initColorMap, colors } from "./utils/ColorStyle";
import {
  PROBLEMS,
  METRICS,
  METRIC_ND,
  METRIC_DIST,
  RUNS_SIM_METRICS,
  RUNS_SIM_DEFAULT,
} from "./utils/Constants";
import { getNaiveSelectItems } from "./utils/DataProcess";

const themeOverrides = {
  common: {
    fontSizeTiny: "var(--font-size-m)",
    fontSizeSmall: "var(--font-size-m)",
    fontSizeMedium: "var(--font-size-m)",
    heightSmall: "calc(2 * var(--font-size-m))",
    primaryColor: "#242424",
    primaryColorHover: "#595959",
    primaryColorPressed: "#1f1f1f",
    primaryColorSuppl: "#595959",
  },
  Switch: {
    buttonHeightSmall: "1.0vh",
    buttonWidthSmall: "1.0vh",
    railHeightSmall: "1.3vh",
    railWidthSmall: "2.4vh",
    railBorderRadiusSmall: "calc(0.5 * var(--radius))",
    buttonBorderRadiusSmall: "calc(0.5 * var(--radius))",
  },
  Select: {
    peers: {
      InternalSelection: {
        paddingSingle: "calc(0.5 * var(--font-size-m))",
        arrowSize: "var(--font-size-m)",
      },
    },
  },
  Popover: {
    fontSize: "var(--font-size-m)",
    padding: "calc(1.5 * var(--space))",
  },
  Slider: {
    railHeight: "calc(0.5 * var(--space)",
    handleSize: "calc(2 * var(--space)",
    railColor: "var(--color-gray)",
    railColorHover: "var(--color-gray)",
  },
  Tag: {
    padding: "calc(0.5 * var(--space))",
    fontSizeSmall: "var(--font-size-m)",
    heightSmall: "calc(var(--font-size-m) + var(--space)",
    borderRadius: "calc(0.5 * var(--radius))",
  },
  Checkbox: {
    sizeSmall: "var(--font-size-l)",
    color: "var(--fill-color)",
    borderRadius: "calc(0.5 * var(--radius))",
    boxShadowFocus: "0 0 0 0.1vh var(--border-color)",
    border: "0.1vh solid var(--border-color)",
    borderChecked: "0.1vh solid var(--border-color)",
    borderFocus: "0.1vh solid var(--border-color)",
    labelLineHeight: 0,
  },
  Button: {
    iconSizeSmall: "var(--font-size-l)",
  },
};

// Global Refs
const loading = ref(false);
const activeProblem = ref({});
const selectedProblem = ref(PROBLEMS[0]);
const colorUsage = ref(initColorMap());

// Solutions View Refs
const activeData = ref({});
const referenceStyle = ref("scatter"); // Scatter | Contour | None
const pfCluster = ref([]);

// Runs Similarity View Refs
const activeSimilarity = ref({});
const runsSimMetric = ref(RUNS_SIM_DEFAULT);

// Sequential View Refs
const selectedAlgorithms = ref([]);
const scaleXStyle = ref("linear"); // Sqrt | Linear
const scrollControl = ref({});

// Metrics View Refs
const focusMode = ref(true);

// Correlation View Refs
const activeGraphs = ref([]);
const graphsData = ref({});
const knnOption = ref({ limit: 0, showArc: false });
const samplingRate = ref(1);
const sizeAsMetric = ref(_.keys(METRICS)[0]);
const activeTimeCurve = ref([]);
const layoutMode = ref("normal"); // Normal | Cluster

const selectData = (name, data) =>
  _.assign(activeData.value, {
    [name]: {
      ...data,
      color: activeProblem.value[name].color,
      NDSet: activeProblem.value[name].metric[METRIC_ND][data.iter],
    },
  });
const cancelData = (name) => _.unset(activeData.value, name);
const selectGraph = (algorithm) => {
  if (_.isNull(algorithm)) {
    activeGraphs.value = [];
    return;
  }
  if (_.includes(activeGraphs.value, algorithm)) {
    _.pull(activeGraphs.value, algorithm);
  } else {
    activeGraphs.value.push(algorithm);
  }
};
const selectAlgorithm = (algorithm) => {
  if (_.includes(selectedAlgorithms.value, algorithm)) {
    _.pull(selectedAlgorithms.value, algorithm);
    cancelData(algorithm);
    colorUsage.value[activeProblem.value[algorithm].color] -= 1;
    activeProblem.value[algorithm].color = "none";
  } else {
    loading.value = true;
    getAttachment(selectedProblem.value, algorithm, (data) => {
      const minCount = _.min(_.values(colorUsage.value));
      const newColor = _.findKey(colorUsage.value, (c) => c === minCount);

      _.merge(activeProblem.value[algorithm], data);
      selectedAlgorithms.value.push(algorithm);
      activeProblem.value[algorithm].color = newColor;
      colorUsage.value[newColor] += 1;
      loading.value = false;
    });
  }
};
const showTimeCurve = (name) => {
  if (_.includes(activeTimeCurve.value, name)) {
    _.pull(activeTimeCurve.value, name);
  } else {
    activeTimeCurve.value.push(name);
  }
};
const scrollToSN = (algorithm, SN) => (scrollControl.value = { algorithm, SN });

const infoGrid = computed(() => {
  const res = {};

  _.forEach(activeProblem.value, ({ metric, color }, name) => {
    if (name === "PF") {
      return;
    }
    res[name] = { metrics: metric, color };
  });
  return res;
});

const metricsData = computed(() => (metricName) => {
  const res = {};

  _.forEach(activeProblem.value, ({ metric, color }, name) => {
    if (!_.includes(selectedAlgorithms.value, name)) {
      return;
    }
    res[name] = {
      values: _.map(_.values(metric[metricName]), (y, x) => [x + 1, y]),
      color,
    };
  });
  return res;
});

const algorithmMetrics = computed(() => {
  const res = {};

  _.forEach(activeProblem.value, ({ metric }, name) => {
    if (!_.includes(selectedAlgorithms.value, name)) {
      return;
    }
    res[name] = metric;
  });
  return res;
});

const algorithmsData = computed(() => {
  const res = {};

  _.forEach(activeProblem.value, ({ result, color }, name) => {
    if (!_.includes(selectedAlgorithms.value, name)) {
      return;
    }
    res[name] = {
      frames: _.assign(
        ..._.map(result.obj, (frame, iter) => ({
          [iter]: frame,
        }))
      ),
      color,
    };
  });
  return res;
});

const RunsSimilarityData = computed(() =>
  _.isEmpty(activeSimilarity.value) || _.isEmpty(activeProblem.value)
    ? {}
    : _.assign(activeSimilarity.value, {
        color: _.mapValues(_.omit(activeProblem.value, "PF"), "color"),
      })
);

watch(
  selectedProblem,
  (newSelectedProblem) => {
    loading.value = true;
    getData(newSelectedProblem, (res) => {
      const data = res.data;
      _.forEach(data, (d, name) => {
        if (name === "PF") {
          return;
        } else {
          _.assign(d, { color: "none" });
        }
      });
      activeProblem.value = data;
      activeData.value = {};
      activeGraphs.value = [];
      selectedAlgorithms.value = [];
      colorUsage.value = initColorMap();
      activeSimilarity.value = res.similarity;
      pfCluster.value = res.pfCluster;
      loading.value = false;
    });
  },
  { immediate: true }
);

watch(
  sizeAsMetric,
  (newSizeAsMetric) =>
    (graphsData.value.nodes = _.map(graphsData.value.nodes, (node) => ({
      ...node,
      metricValue:
        activeProblem.value[node.name].metric[newSizeAsMetric][node.frame],
    })))
);

watch(
  activeGraphs,
  (newActiveGraphs) => {
    if (_.isEmpty(newActiveGraphs)) {
      graphsData.value = {};
      activeTimeCurve.value = [];
      return;
    }
    loading.value = true;
    getGraph(selectedProblem.value, newActiveGraphs, (data) => {
      _.forEach(
        data.nodes,
        (node) =>
          (node.metricValue =
            activeProblem.value[node.name].metric[sizeAsMetric.value][
              node.frame
            ])
      );
      graphsData.value = {
        ...data,
        colorMap: _.fromPairs(
          _.map(newActiveGraphs, (name) => [
            name,
            activeProblem.value[name].color,
          ])
        ),
      };
      _.forEach(
        _.without(activeTimeCurve.value, ...newActiveGraphs),
        showTimeCurve
      );
      loading.value = false;
    });
  },
  { deep: true }
);
</script>

<style scoped>
.content {
  display: flex;
  padding: var(--space) 0 0 var(--space);
  height: calc(100vh - var(--space));
  width: calc(100vw - var(--space));
}

.title {
  background: var(--color-gray);
  color: var(--color-dark);
  align-items: center;
}

.metric-name {
  background: var(--color-light-gray);
  color: var(--color-dark);
  align-items: center;
  flex-direction: column;
}

.title h4,
.metric-name h4 {
  margin: 0;
}

.metric-name h4 {
  writing-mode: vertical-lr;
  text-align: right;
  transform: rotate(180deg);
  flex-grow: 1;
}

.title .n-config-provider {
  display: flex;
  flex-grow: 1;
  justify-content: end;
}

.sub-content {
  display: flex;
  flex-direction: column;
  flex-grow: 0;
  flex-shrink: 0;
}

.view {
  margin: 0 var(--space) var(--space) 0;
  flex-grow: 1;
  height: 0;
}

.option-item {
  display: flex;
  width: 6vw;
  align-items: center;
}

.selected-frame:not(:first-of-type) {
  margin-top: var(--space);
}

.selected-frame > div {
  color: var(--frame-color);
  border-top: 0.2vh solid var(--frame-color);
  border-bottom: 0.2vh solid var(--frame-color);
}

.n-space {
  gap: var(--space) calc(0.75 * var(--space));
}

.n-divider {
  margin: 0;
  height: var(--font-size-l);
}
</style>
