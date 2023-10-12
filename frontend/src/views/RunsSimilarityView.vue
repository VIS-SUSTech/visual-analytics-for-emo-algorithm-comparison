<template>
  <svg
    :id="`runs-similarity`"
    height="100%"
    width="100%"
    :viewBox="`0 0 ${VIEWSIZE} ${VIEWSIZE}`"
    preserveAspectRatio="xMidYMin meet"
    :ref="svgRef"
  >
    <defs>
      <clipPath id="runs-visible-zone">
        <rect :width="`${VIEWSIZE}`" :height="`${VIEWSIZE}`"></rect>
      </clipPath>
    </defs>
    <g id="runs-point-group" clip-path="url(#runs-visible-zone)">
      <g
        v-for="(pos, index) in data.projections[layoutMetric]"
        :key="`runs-${data.runs[index]}-group`"
        @click="() => emit('select', data.runs[index])"
        style="cursor: pointer"
      >
        <circle
          :cx="transform.rescaleX(scaleX)(pos[0])"
          :cy="transform.rescaleY(scaleY)(pos[1])"
          :stroke="`${colors[data.color[data.runs[index]]][2]}`"
          stroke-width="4"
          :r="radius"
          :fill="`${colors[data.color[data.runs[index]]][1]}`"
        ></circle>
        <text
          :key="`runs-${data.runs[index]}-text`"
          :x="transform.rescaleX(scaleX)(pos[0])"
          :y="transform.rescaleY(scaleY)(pos[1]) + radius + fontSize"
          text-anchor="middle"
          :fill="`${colors[data.color[data.runs[index]]][1]}`"
          :font-size="fontSize"
          font-weight="bold"
        >
          {{ data.runs[index] }}
        </text>
      </g>
    </g>
  </svg>
</template>
<script setup>
import { computed, watch, ref, onMounted } from "vue";
import _ from "lodash";
import * as d3 from "d3";

import { colors } from "../utils/ColorStyle";

const VIEWSIZE = 500;
const MARGIN = 50;
const radius = 8;
const fontSize = 16;

const props = defineProps(["data", "selectedAlgorithms", "layoutMetric"]);
const emit = defineEmits(["select"]);

const svgRef = ref(null);
const transform = ref(d3.zoomIdentity);

const scaleX = computed(() => {
  const x = _.map(props.data.projections[props.layoutMetric], (p) => p[0]);

  return d3
    .scaleLinear()
    .domain([_.min(x), _.max(x)])
    .range([MARGIN, VIEWSIZE - MARGIN]);
});

const scaleY = computed(() => {
  const y = _.map(props.data.projections[props.layoutMetric], (p) => p[1]);

  return d3
    .scaleLinear()
    .domain([_.min(y), _.max(y)])
    .range([VIEWSIZE - MARGIN, MARGIN]);
});

const onZoom = (event) => (transform.value = event.transform);

const draw = () =>
  d3
    .select("#runs-similarity")
    .call(
      d3
        .zoom()
        .scaleExtent([1, 10])
        .translateExtent([
          [0, 0],
          [VIEWSIZE, VIEWSIZE],
        ])
        .on("zoom", onZoom)
    )
    .on("dblclick.zoom", null);

onMounted(() => draw());

watch(
  () => props.data,
  () => draw()
);
</script>

<style scoped></style>
