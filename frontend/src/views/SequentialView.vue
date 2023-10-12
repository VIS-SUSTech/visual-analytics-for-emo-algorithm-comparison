<template>
  <div class="column" style="flex-basis: calc(1.5 * var(--frame-size))">
    <div
      v-for="{ color, name } in orderedAlgorithms"
      :key="name"
      class="cell meta"
      :style="`--bg-color: ${colors[color][2]}; --border-color: ${colors[color][0]};`"
    >
      <DiyCard class="algorithm-title">
        <span class="title-text">
          {{ name }}
        </span>
        <n-config-provider
          :theme-overrides="themeOverrides"
          style="display: flex; align-items: center"
          preflight-style-disabled
        >
          <n-tooltip trigger="hover" placement="bottom">
            <template #trigger>
              <n-button
                size="tiny"
                :style="`
                  --bg-color: ${colors[color][0]};
                  --bg-color-hover: ${colors[color][1]};
                  --bg-color-pressed: ${colors[color][2]};
                  --color-normal: ${colors[color][1]}
                `"
                @click="() => reorder(name, -1)"
                secondary
              >
                <template #icon>
                  <n-icon :component="ArrowUp" />
                </template>
              </n-button>
            </template>
            <span> Move Up </span>
          </n-tooltip>
          <n-tooltip trigger="hover" placement="bottom">
            <template #trigger>
              <n-button
                size="tiny"
                :style="`
                  --bg-color: ${colors[color][0]};
                  --bg-color-hover: ${colors[color][1]};
                  --bg-color-pressed: ${colors[color][2]};
                  --color-normal: ${colors[color][1]}
                `"
                @click="() => reorder(name, 1)"
                secondary
              >
                <template #icon>
                  <n-icon :component="ArrowDown" />
                </template>
              </n-button>
            </template>
            <span> Move Down </span>
          </n-tooltip>
          <n-tooltip trigger="hover" placement="right">
            <template #trigger>
              <n-switch
                class="timecurve-switch"
                size="small"
                :round="false"
                :rail-style="(props) => getSwitchStyle({ color, ...props })"
                :value="_.includes(props.graphTarget, name)"
                :on-update:value="() => emit('graph', name)"
              />
            </template>
            <span v-if="_.includes(props.graphTarget, name)">
              Cancel the selection of {{ name }} for comparison
            </span>
            <span v-else>
              Select {{ name }} for calculate comparison graph
            </span>
          </n-tooltip>
        </n-config-provider>
      </DiyCard>
      <DiyCard class="distribution">
        <MetircDetail
          :color="color"
          :id="name"
          :scaleXStyle="scaleXStyle"
          :bars="metricBars(name)"
          :area="metricArea(name)"
        />
      </DiyCard>
    </div>
  </div>
  <div class="column" style="flex-grow: 1; width: 0">
    <div
      v-for="{ frames, SN, color, name } in orderedAlgorithms"
      :key="name"
      :class="['cell', 'frame-container', name]"
      :style="`
        --active-color: ${colors[color][1]};
        --border-color: ${colors[color][0]};
        --hover-color: ${colors[color][2]};
      `"
    >
      <DiyCard
        v-for="(frame, iter) in frames"
        :key="iter"
        @click="() => onChange(name, iter, frame)"
        :class="['frame', { active: activeData[name]?.iter === iter }]"
      >
        <svg
          :id="`frame-plot-${name}-${iter}`"
          width="100%"
          height="100%"
          :viewBox="`0 0 ${viewSize + 2 * margin} ${viewSize + 2 * margin}`"
        >
          <!-- PF Reference -->
          <image
            v-if="!_.isNull(figurePF)"
            width="100%"
            height="100%"
            :href="figurePF"
          />
          <!-- Algorithm Frame -->
          <g
            :fill="colors[color][2]"
            fill-opacity="0.5"
            stroke="none"
            v-if="_.every([scalePF, scaleX, scaleY])"
          >
            <circle
              v-for="(pos, index) in _.map(frame, scalePF)"
              :key="`${name}-${index}`"
              :cx="scaleX(pos[0])"
              :cy="scaleY(pos[1])"
              r="4"
            />
          </g>
          <!-- Iteration Text -->
          <g
            id="iteration-text"
            :transform="`translate(${margin + viewSize}, ${4 * margin})`"
          >
            <text fill="var(--color-dark)" text-anchor="end" font-size="36">
              Gen. Sample #{{ SN[iter] }}
            </text>
          </g>
        </svg>
      </DiyCard>
    </div>
  </div>
  <div id="reference-plot">
    <svg
      id="reference-plot-svg"
      width="100%"
      height="100%"
      :viewBox="`0 0 ${viewSize + 2 * margin} ${viewSize + 2 * margin}`"
    >
      <g
        fill="var(--color-gray)"
        fill-opacity="0.5"
        stroke="none"
        v-if="_.every([scalePF, scaleX, scaleY])"
      >
        <circle
          v-for="(pos, index) in _.map(props.PF, scalePF)"
          :key="`PF-${index}`"
          :cx="scaleX(pos[0])"
          :cy="scaleY(pos[1])"
          r="4"
        />
      </g>
    </svg>
  </div>
</template>

<script setup>
import * as d3 from "d3";
import { onMounted, ref, watch, computed } from "vue";
import { NSwitch, NConfigProvider, NTooltip, NButton, NIcon } from "naive-ui";
import { ArrowUp, ArrowDown } from "@vicons/fa";
import { toPng } from "html-to-image";
import _ from "lodash";

import DiyCard from "../components/DiyCard.vue";
import MetircDetail from "../components/MetircDetail.vue";
import { getIndexSeries, getScalers } from "../utils/DataProcess";
import { colors } from "../utils/ColorStyle";
import { METRICS, METRIC_DIST } from "../utils/Constants";

const viewSize = 480;
const margin = 8;

const props = defineProps([
  "PF",
  "algorithms",
  "metrics",
  "activeData",
  "graphTarget",
  "scaleXStyle",
  "scrollControl",
]);
const emit = defineEmits(["select", "cancel", "graph"]);

const themeOverrides = {
  Switch: {
    buttonHeightSmall: "1.0vh",
    buttonWidthSmall: "1.0vh",
    railHeightSmall: "1.3vh",
    railWidthSmall: "2.4vh",
    railBorderRadiusSmall: "calc(0.5 * var(--radius))",
    buttonBorderRadiusSmall: "calc(0.5 * var(--radius))",
  },
  Popover: {
    fontSize: "var(--font-size-m)",
    padding: "calc(1.5 * var(--space))",
  },
  Button: {
    paddingTiny: "0.2vh",
    iconSizeTiny: "var(--font-size-m)",
    heightTiny: "1.3vh",
    borderRadiusTiny: "calc(0.5 * var(--radius))",
    colorOpacitySecondary: 0,
    colorSecondary: "var(--bg-color)",
    colorSecondaryHover: "var(--bg-color-hover)",
    colorSecondaryPressed: "var(--bg-color-pressed)",
    textColor: "var(--color-normal)",
  },
};

const [scaleX, scaleY] = [ref(null), ref(null)];
const scalePF = ref(null);
const order = ref([]);
const figurePF = ref(null);

const onChange = async (name, iter, data) => {
  if (iter === props.activeData[name]?.iter) {
    emit("cancel", name);
  } else {
    const image = await toPng(
      document.getElementById(`frame-plot-${name}-${iter}`),
      { filter: (node) => node.id !== "iteration-text" }
    );

    emit("select", name, { iter, data, image });
  }
};

const refreshCanvas = async (PF) => {
  const space = _.zip(...PF);
  const [scaler, axisScaleX, axisScaleY] = getScalers(
    d3.extent(space[0]),
    d3.extent(space[1]),
    margin,
    viewSize
  );

  scaleX.value = axisScaleX;
  scaleY.value = axisScaleY;
  scalePF.value = scaler;
  figurePF.value = await toPng(document.getElementById("reference-plot-svg"));
};

const getSwitchStyle = ({ color, focused, checked }) => {
  const style = {};

  if (checked) {
    style.background = colors[color][0];
    if (focused) {
      style.boxShadow = `0 0 0 0.15vh ${colors[color][0]}40`;
    }
  } else {
    style.background = colors[color][1];
    if (focused) {
      style.boxShadow = `0 0 0 0.15vh ${colors[color][1]}40`;
    }
  }
  return style;
};

watch(
  () => props.PF,
  (newPF) => refreshCanvas(newPF)
);

watch(
  () => props.algorithms,
  (newAlgorithms, oldAlgorithms) => {
    const newKeys = _.keys(newAlgorithms);
    const oldKeys = _.keys(oldAlgorithms);

    _.forEach(_.without(oldKeys, ...newKeys), (alg) => {
      _.pull(order.value, alg);
      if (_.includes(props.graphTarget, alg)) {
        emit("graph", alg);
      }
    });
    _.forEach(_.without(newKeys, ...oldKeys), (alg) => order.value.push(alg));
  }
);

watch(
  () => props.scrollControl,
  ({ algorithm, SN }) => {
    const row = document
      .getElementsByClassName(`cell frame-container ${algorithm}`)
      .item(0);
    const step = row.scrollWidth / _.size(props.algorithms[algorithm].frames);

    row.scrollTo({ behavior: "smooth", left: step * (SN - 1) });
  }
);

onMounted(() => refreshCanvas(props.PF));

const metricBars = computed(() => (algorithm) => {
  const bars = {};
  const SN = getIndexSeries(_.keys(props.algorithms[algorithm].frames));

  _.forEach(METRICS, ({ optimal }, metric) => {
    const best = optimal(_.values(props.metrics[algorithm][metric]));
    const bestSN =
      SN[
        _.findKey(props.metrics[algorithm][metric], (value) => value === best)
      ];
    const current =
      props.metrics[algorithm][metric][props.activeData[algorithm]?.iter];
    const currentSN = SN[props.activeData[algorithm]?.iter];

    bars[metric] = {
      range: d3.extent(
        _.flatten(_.map(props.metrics, (mets) => _.values(mets[metric])))
      ),
      best,
      bestSN,
      current,
      currentSN,
    };
  });
  return bars;
});

const areaRanges = computed(() => {
  const values = [];
  const { origin, target, bins } = METRIC_DIST;

  _.forEach(props.metrics, (mets) => {
    const bestValue = METRICS[origin].optimal(_.values(mets[origin]));
    const bestKey = _.findKey(mets[origin], (value) => value === bestValue);

    values.push(mets[target][bestKey]);
  });
  _.forEach(props.activeData, ({ iter }, alg) =>
    values.push(props.metrics[alg][target][iter])
  );

  const rangeX = d3.extent(_.flatten(values));
  const bin = d3.bin(rangeX).thresholds(bins);
  const rangeY = [
    0,
    _.max(_.flatten(_.map(values, (v) => _.map(bin(v), (b) => _.size(b))))),
  ];

  return { rangeX, rangeY };
});

const metricArea = computed(() => (algorithm) => {
  const area = { ...areaRanges.value };
  const { origin, target } = METRIC_DIST;
  const SN = getIndexSeries(_.keys(props.algorithms[algorithm].frames));
  const bestValue = METRICS[origin].optimal(
    _.values(props.metrics[algorithm][origin])
  );
  const bestKey = _.findKey(
    props.metrics[algorithm][origin],
    (value) => value === bestValue
  );

  area.best = props.metrics[algorithm][target][bestKey];
  area.bestSN = SN[bestKey];
  area.current =
    props.metrics[algorithm][target][props.activeData[algorithm]?.iter];
  area.currentSN = SN[props.activeData[algorithm]?.iter];
  return area;
});

const orderedAlgorithms = computed(() =>
  _.orderBy(
    _.map(props.algorithms, (alg, name) => ({
      ...alg,
      SN: getIndexSeries(_.keys(alg.frames)),
      name,
    })),
    ({ name }) => _.indexOf(order.value, name)
  )
);

const reorder = (name, bias) => {
  const selfPos = _.indexOf(order.value, name);
  const targetPos = selfPos + bias;

  if (!_.inRange(targetPos, 0, _.size(order.value))) {
    return;
  }
  [order.value[selfPos], order.value[targetPos]] = [
    order.value[targetPos],
    order.value[selfPos],
  ];
};
</script>

<style scoped>
#reference-plot {
  position: fixed;
  height: var(--frame-size);
  width: var(--frame-size);
  right: var(--space);
  bottom: var(--space);
  z-index: -128;
}

.column {
  display: flex;
  flex-direction: column;
}
.column:not(:first-of-type) {
  margin-left: var(--space);
}

.cell {
  flex: 0 0 auto;
}

.cell.frame-container {
  display: flex;
  overflow-x: overlay;
  height: auto;
}

.cell:not(:first-of-type) {
  margin-top: var(--space);
}

.cell.frame-container:not(:first-of-type) {
  margin-top: var(--space);
}

.cell.frame-container::-webkit-scrollbar-thumb {
  background: var(--border-color);
}

.cell.frame-container::-webkit-scrollbar-thumb:hover {
  background: var(--active-color);
}

.cell.frame-container::-webkit-scrollbar {
  height: calc(2 * var(--scrollbar-size));
}

.cell.meta {
  display: flex;
  flex-direction: column;
  height: var(--frame-size);
  padding: var(--space);
  border: 0.1vh solid transparent;
}

.algorithm-title {
  outline: 0.2vh solid var(--border-color);
  outline-offset: -0.1vh;
  border: none;
  margin: calc(-1 * var(--space));
  background-color: var(--bg-color);
  align-items: center;
  padding: calc(0.5 * var(--space)) var(--space);
}

.distribution {
  margin: calc(2 * var(--space)) calc(-1 * var(--space)) calc(-1 * var(--space));
  outline: 0.2vh solid var(--border-color);
  outline-offset: -0.1vh;
  border: none;
  flex-grow: 1;
  overflow-y: hidden;
}

.frame {
  height: var(--frame-size);
  width: var(--frame-size);
  flex: 0 0 auto;
  border-color: var(--border-color);
}

.frame:not(:first-of-type) {
  margin-left: var(--space);
}

.frame:hover {
  border-color: var(--hover-color);
  cursor: pointer;
}

.frame.active {
  box-shadow: inset 0 0 var(--space) 0 var(--active-color);
}

.title-text {
  font-weight: bold;
  color: var(--color-light);
  flex-grow: 1;
}

.n-button {
  margin-right: calc(0.5 * var(--space));
}

.n-button:hover {
  color: var(--color-light);
}

.n-button:active {
  color: var(--color-light);
}

.n-button:focus {
  color: var(--color-light);
}
</style>
