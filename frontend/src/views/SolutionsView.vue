<template>
  <n-config-provider :theme-overrides="themeOverrides" preflight-style-disabled>
    <n-popover
      v-if="!_.isNull(hoverIndex)"
      :show="true"
      :x="hoverPos[0]"
      :y="hoverPos[1]"
      :animated="false"
      :show-arrow="false"
      placement="right-start"
      trigger="manual"
    >
      <div :style="`color: ${colors[data[hoverIndex.name].color][1]}`">
        <h4>{{ hoverIndex.name }}</h4>
        <span> [ </span>
        <span
          v-if="sampledData[hoverIndex.name].sampled[hoverIndex.index] === 1"
        >
          Inlier
        </span>
        <span v-else> Outlier </span>
        <span v-if="_.includes(data[hoverIndex.name].NDSet, hoverIndex.index)">
          , Non-dominated
        </span>
        <span> ] </span>
      </div>
      <n-divider />
      <span>Vector in Objective Space:</span>
      <div
        v-for="(value, index) in objVectors[
          getObjPath(hoverIndex.name, data[hoverIndex.name].iter)
        ][hoverIndex.index]"
        :key="`obj-${index}`"
      >
        <span class="bold-item">Obj #{{ index }}</span>
        <span>: {{ value }}</span>
      </div>
    </n-popover>
  </n-config-provider>
  <svg
    id="solutions"
    :viewBox="`0 0 ${viewSize + 2 * margin} ${viewSize + 2 * margin}`"
    width="100%"
    height="100%"
  >
    <defs>
      <clipPath id="solutions-zone">
        <rect
          :x="0"
          :y="0"
          :width="viewSize + 2 * margin"
          :height="viewSize + 2 * margin"
        />
      </clipPath>
      <pattern
        id="crossPattern"
        width="16"
        height="16"
        patternUnits="userSpaceOnUse"
      >
        <path
          d="M-4,4 l8,-8 M0,16 l16,-16 M12,20 l8,-8 M20,4 l-8,-8 M16,16 l-16,-16 M4,20 l-8,-8"
          stroke="var(--color-gray)"
          stroke-width="2"
        />
      </pattern>
    </defs>
    <g id="solution-data-area" clip-path="url(#solutions-zone)">
      <!-- PF Reference -->
      <template v-if="_.every([scalePF, scaleX, scaleY])">
        <g
          id="PF-reference"
          fill="var(--color-gray)"
          fill-opacity="0.5"
          stroke="none"
          v-if="props.referenceStyle === 'scatter'"
        >
          <circle
            v-for="(pos, index) in _.map(props.PF, scalePF)"
            :key="`PF-${index}`"
            :cx="scaleX(pos[0])"
            :cy="scaleY(pos[1])"
            r="2"
          />
        </g>
        <g
          id="PF-reference"
          stroke="black"
          stroke-width="0.1"
          stroke-opacity="0.5"
          :transform="transform"
          v-if="props.referenceStyle === 'contour'"
        >
          <path
            v-for="({ path, fill }, index) in contourPF"
            :key="`PF-${index}`"
            :fill="fill"
            :d="path"
          />
        </g>
        <g
          id="PF-reference"
          stroke="var(--color-gray)"
          fill="url(#crossPattern)"
          fill-opacity="0.5"
          stroke-width="1"
          :transform="transform"
          v-if="props.referenceStyle === 'hull'"
        >
          <path
            v-for="(hull, index) in hullPF"
            :key="`pf-hull-${index}`"
            :d="hull"
          />
        </g>
      </template>
      <!-- Active Algorithms -->
      <template v-if="!_.isEmpty(contourData)">
        <template
          v-for="({ color }, name) in data"
          :key="`data-${name}-contours`"
        >
          <g
            :id="`solution-algorithm-${name}-contours`"
            v-if="_.every([scalePF, originScaleX, originScaleY])"
            :stroke="colors[color][1]"
            stroke-opacity="0.8"
            :transform="transform"
          >
            <path
              v-for="({ path, dashArray, width, fill }, index) in contourData[
                name
              ]"
              :key="`contour-${name}-${index}`"
              :d="path"
              :stroke-dasharray="dashArray"
              :stroke-width="width"
              :fill="fill"
            />
          </g>
        </template>
      </template>
      <template v-if="!_.isEmpty(sampledData)">
        <template
          v-for="({ data, color, sampled }, name) in sampledData"
          :key="`data-${name}-points`"
        >
          <g
            :id="`solution-algorithm-${name}-points`"
            v-if="_.every([scalePF, scaleX, scaleY])"
            :fill="colors[color][1]"
            fill-opacity="0.8"
            stroke="var(--color-gray)"
            stroke-opacity="1"
            stroke-width="1.2"
          >
            <template v-for="(pos, index) in _.map(data, scalePF)">
              <circle
                v-if="sampled[index] === 1"
                :id="`inlier-${name}-${index}`"
                :key="`inlier-${name}-${index}`"
                :cx="scaleX(pos[0])"
                :cy="scaleY(pos[1])"
                :onmouseenter="(e) => onHover(e, name, index)"
                :onmouseleave="onLeave"
                :r="
                  hoverIndex?.index === index && hoverIndex?.name === name
                    ? 6
                    : 4
                "
              />
              <path
                v-else-if="sampled[index] === -1"
                :id="`outlier-${name}-${index}`"
                :key="`outlier-${name}-${index}`"
                :d="
                  outlierPoint(
                    (hoverIndex?.index === index && hoverIndex?.name === name
                      ? 2
                      : 1) * symbolSize
                  )
                "
                :transform="`translate(${scaleX(pos[0])}, ${scaleY(pos[1])})`"
                :onmouseenter="(e) => onHover(e, name, index)"
                :onmouseleave="onLeave"
              />
            </template>
          </g>
        </template>
      </template>
    </g>
    <!-- Legends -->
    <g
      v-for="({ color }, name, index) in props.data"
      :key="`color-${name}`"
      :transform="`translate(${viewSize - 8 * margin}, ${
        (2 * index + 2) * margin
      })`"
    >
      <rect
        stroke="none"
        :fill="colors[color][1]"
        width="26"
        height="4"
        x="-30"
        y="-6"
      />
    </g>
    <g
      v-for="(_, name, index) in props.data"
      :key="`legend-${name}`"
      :transform="`translate(${viewSize - 8 * margin}, ${
        (2 * index + 2) * margin
      })`"
    >
      <text fill="var(--color-dark)" text-anchor="start" font-size="12">
        {{ name }}
      </text>
    </g>
  </svg>
</template>

<script setup>
import { onMounted, watch, ref } from "vue";
import { NConfigProvider, NPopover, NDivider } from "naive-ui";
import _ from "lodash";
import * as d3 from "d3";
import hull from "hull.js";

import { getScalers } from "../utils/DataProcess";
import { colors } from "../utils/ColorStyle";
import { getSampling, getObjVector } from "../utils/Network";

const viewSize = 640;
const margin = 8;
const hullConcavity = 10;
const contourPFParams = [8, 8, 50];
const contourDataParams = [4, 12, 4];
const contourPFColorRange = [
  d3.interpolateGreys(0.05),
  d3.interpolateGreys(0.8),
];
const contourDataColorRange = (color) => [`${color[0]}50`, `${color[1]}50`];
const symbolSize = 60;

const outlierPoint = (size) => d3.symbol().type(d3.symbolCross).size(size)();

const getObjPath = (name, index) => `${name}|${index}`;

const themeOverrides = {
  Popover: {
    fontSize: "var(--font-size-m)",
    padding: "var(--space)",
  },
};

const props = defineProps([
  "data",
  "PF",
  "referenceStyle",
  "samplingRate",
  "pfCluster",
  "problem",
]);
const emit = defineEmits(["frameOutBox"]);

const [scaleX, scaleY] = [ref(null), ref(null)];
const [originScaleX, originScaleY] = [ref(null), ref(null)];
const sampledData = ref({});
const contourData = ref({});
const scalePF = ref(null);
const contourPF = ref([]);
const hullPF = ref([]);
const transform = ref(d3.zoomIdentity);
const [hoverIndex, hoverPos] = [ref(null), ref([0, 0])];
const objVectors = ref({});

const calContour = (
  scaleX,
  scaleY,
  scalePF,
  data,
  colorRange,
  [cellSize, bandwidth, thresholds]
) => {
  const xRange = d3.extent(_.map(data, scalePF), (d) => scaleX(d[0]));
  const yRange = d3.extent(_.map(data, scalePF), (d) => scaleY(d[1]));
  let translateX = 0;
  let xLimit = 0;
  let translateY = 0;
  let yLimit = 0;
  let outBox = false;
  if (
    xRange[0] < 0 ||
    yRange[0] < 0 ||
    xRange[1] > viewSize ||
    yRange[1] > viewSize
  )
    outBox = true;
  if (
    xRange[0] <= margin - viewSize ||
    yRange[0] <= margin - viewSize ||
    xRange[1] >= 2 * viewSize + margin ||
    yRange[1] >= 2 * viewSize + margin
  ) {
    translateX = viewSize;
    xLimit = 3 * viewSize - margin;
    translateY = viewSize;
    yLimit = 3 * viewSize - margin;
  } else {
    translateX = margin - xRange[0];
    xLimit = xRange[1] + translateX + margin;
    translateY = margin - yRange[0];
    yLimit = yRange[1] + translateY + margin;
  }
  const contour = d3
    .contourDensity()
    .x((d) => scaleX(d[0]) + translateX)
    .y((d) => scaleY(d[1]) + translateY)
    .size([xLimit, yLimit])
    .cellSize(cellSize)
    .bandwidth(bandwidth)
    .thresholds(thresholds)(_.map(data, scalePF));
  const scaleColor = (value) =>
    d3
      .scaleLinear()
      .domain([0, 1])
      .range([colorRange[0], colorRange[1]])
      .interpolate(d3.interpolateHcl)(
      d3
        .scaleLinear()
        .domain(d3.extent(contour, (d) => d.value))
        .range([0, 1])(value)
    );
  const scaleDash = d3
    .scaleLinear()
    .domain(d3.extent(contour, (d) => d.value))
    .range([1, 10]);
  const scaleWidth = d3
    .scaleLinear()
    .domain(d3.extent(contour, (d) => d.value))
    .range([0.2, 0.8]);
  const path = d3.geoPath();
  _.forEach(contour, (d) => {
    _.forEach(d.coordinates, (c1) => {
      _.forEach(c1, (c2) => {
        _.forEach(c2, (p) => {
          p[0] -= translateX;
          p[1] -= translateY;
        });
      });
    });
  });

  return [
    _.map(contour, (d) => ({
      path: path(d),
      fill: scaleColor(d.value),
      dashArray: `${scaleDash(d.value)} 1`,
      width: scaleWidth(d.value),
    })),
    outBox,
    contour,
  ];
};

const calHullPF = (scaleX, scaleY, scalePF, PF) =>
  d3
    .line()
    .x((p) => scaleX(p[0]))
    .y((p) => scaleY(p[1]))
    .curve(d3.curveCatmullRomClosed.alpha(1))(
    hull(_.map(PF, scalePF), hullConcavity)
  );

const onHover = (event, name, index) => {
  hoverIndex.value = { name, index };
  hoverPos.value = [
    event.clientX - event.offsetX,
    event.clientY - event.offsetY,
  ];
};

const onLeave = () => (hoverIndex.value = null);

const onZoom = (dynamicScaleX, dynamicScaleY) => (event) => {
  const reScaleX = event.transform.rescaleX(dynamicScaleX);
  const reScaleY = event.transform.rescaleY(dynamicScaleY);

  transform.value = event.transform;
  scaleX.value = reScaleX;
  scaleY.value = reScaleY;
};

const refreshCanvas = async (PF) => {
  const space = _.zip(...PF);
  const [scaler, axisScaleX, axisScaleY] = getScalers(
    d3.extent(space[0]),
    d3.extent(space[1]),
    margin,
    viewSize
  );
  const svg = d3.select("#solutions");

  svg.call(d3.zoom().transform, d3.zoomIdentity);
  svg.call(
    d3
      .zoom()
      .scaleExtent([0.01, 10])
      .extent([
        [0, 0],
        [viewSize + 2 * margin, viewSize + 2 * margin],
      ])
      .translateExtent([
        [-Infinity, -Infinity],
        [Infinity, Infinity],
      ])
      .on("zoom", onZoom(axisScaleX, axisScaleY))
  );
  svg.on("pointerleave", onLeave);
  contourPF.value = calContour(
    axisScaleX,
    axisScaleY,
    scaler,
    PF,
    contourPFColorRange,
    contourPFParams
  )[0];
  hullPF.value = _.map(
    _.groupBy(_.zip(PF, props.pfCluster), (d) => d[1]),
    (group) =>
      calHullPF(
        axisScaleX,
        axisScaleY,
        scaler,
        _.map(group, (d) => d[0])
      )
  );
  transform.value = d3.zoomIdentity;
  scaleX.value = axisScaleX;
  scaleY.value = axisScaleY;
  originScaleX.value = axisScaleX;
  originScaleY.value = axisScaleY;
  scalePF.value = scaler;
};

watch(
  () => props.PF,
  (newPF) => refreshCanvas(newPF)
);

watch(
  () => props.data,
  (newData) => {
    const algorithms = [];

    _.forEach(newData, ({ iter }, name) => {
      const path = getObjPath(name, iter);

      algorithms.push(path);
      if (_.has(objVectors.value, path)) {
        return;
      }
      getObjVector(props.problem, name, iter, (vectors) =>
        _.set(objVectors.value, path, vectors)
      );
    });
    _.forEach(_.keys(objVectors.value), (path) => {
      if (!_.includes(algorithms, path)) {
        _.unset(objVectors.value, path);
      }
    });
  },
  { deep: true }
);

watch(
  () => [props.data, props.samplingRate],
  ([newData, newSamplingRate], [, oldSamplingRate]) => {
    if (
      _.isEmpty(newData) ||
      !_.every([scalePF.value, originScaleX.value, originScaleY.value])
    ) {
      contourData.value = {};
      sampledData.value = {};
    }
    if (newSamplingRate === oldSamplingRate) {
      const estimatedResult = _.mapValues(newData, ({ data, color }) =>
        calContour(
          originScaleX.value,
          originScaleY.value,
          scalePF.value,
          data,
          contourDataColorRange(colors[color]),
          contourDataParams
        )
      );
      const estimatedMax = _.maxBy(
        _.concat(
          _.map(estimatedResult, (singleResult) =>
            _.map(singleResult[2], (d) => d.value)
          )
        ),
        (d) => _.last(d)
      );
      emit(
        "frameOutBox",
        _.mapValues(estimatedResult, (d) => d[1])
      );
      if (!_.isUndefined(estimatedMax) && !_.isEmpty(estimatedMax)) {
        contourData.value = _.mapValues(
          newData,
          ({ data, color }) =>
            calContour(
              originScaleX.value,
              originScaleY.value,
              scalePF.value,
              data,
              contourDataColorRange(colors[color]),
              [contourDataParams[0], contourDataParams[1], estimatedMax]
            )[0]
        );
      }
    }
    const payload = {
      data: _.mapValues(newData, ({ data }) =>
        _.map(_.map(data, scalePF.value), ([x, y]) => [
          originScaleX.value(x),
          originScaleY.value(y),
        ])
      ),
      iteration: _.mapValues(newData, ({ iter }) => iter),
      problem: props.problem,
      sampling_rate: newSamplingRate,
    };
    getSampling(payload, (data) => {
      sampledData.value = _.mapValues(newData, (d, algoName) => ({
        ...d,
        sampled: data[algoName],
      }));
    });
  },
  { deep: true }
);

onMounted(() => refreshCanvas(props.PF));
</script>

<style scoped>
h4 {
  margin: 0;
  display: inline-block;
}

.n-divider {
  margin-top: var(--space);
  margin-bottom: var(--space);
}

.bold-item {
  font-weight: bold;
}
</style>
