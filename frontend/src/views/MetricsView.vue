<template>
  <svg
    :id="`metrics-${props.name}`"
    :viewBox="`0 0 ${viewSizeW + 6 * margin} ${viewSizeH + 3 * margin}`"
    width="100%"
    height="100%"
  >
    <defs>
      <clipPath id="metrics-zone">
        <!-- Height + 2 for No Conflict with Axis -->
        <rect
          :x="margin"
          :y="0"
          :width="viewSizeW"
          :height="margin + viewSizeH + 2"
        />
      </clipPath>
    </defs>
    <!-- Height + 2 for No Conflict with Paths -->
    <g
      class="x-axis"
      :transform="`translate(${3 * margin}, ${viewSizeH + margin + 2})`"
      font-size="12"
    />
    <g
      class="y-axis"
      :transform="`translate(${4 * margin}, 0)`"
      font-size="12"
    />
    <g
      class="paths"
      v-for="({ values, color }, name) in props.metrics"
      :key="name"
      fill="none"
      :stroke="isHoverPath(name) ? colors[color][2] : 'var(--color-gray)'"
      stroke-width="1.5"
      stroke-opacity="0.8"
      :transform="`translate(${3 * margin}, 0)`"
    >
      <path
        v-if="!_.isNull(line)"
        style="mix-blend-mode: multiply"
        clip-path="url(#metrics-zone)"
        :d="line(values)"
      />
    </g>
    <g
      v-if="!_.isNull(hoverFrame)"
      :transform="`translate(${hoverFrame.pos[0]}, ${hoverFrame.pos[1]})`"
    >
      <text
        :fill="colors[metrics[hoverFrame.name].color][1]"
        font-size="10"
        font-weight="bold"
        :text-anchor="hoverFrame.isAboveHalf[0] ? 'end' : 'start'"
        :x="hoverFrame.isAboveHalf[0] ? -4 : 4"
        :y="hoverFrame.isAboveHalf[1] ? -24 : 32"
      >
        {{ hoverFrame.name }} [Gen. Sample #{{
          SN[hoverFrame.name][hoverFrame.frame]
        }}]
      </text>
      <text
        :fill="colors[metrics[hoverFrame.name].color][1]"
        font-size="10"
        font-weight="bold"
        :text-anchor="hoverFrame.isAboveHalf[0] ? 'end' : 'start'"
        :x="hoverFrame.isAboveHalf[0] ? -4 : 4"
        :y="hoverFrame.isAboveHalf[1] ? -10 : 16"
      >
        {{ name }}: {{ hoverFrame.metric }}
      </text>
      <line
        style="mix-blend-mode: multiply"
        stroke="var(--color-gray)"
        stroke-width="2"
        stroke-opacity="0.8"
        :y1="-hoverFrame.pos[1]"
        :y2="viewSizeH - hoverFrame.pos[1] + margin"
      />
      <circle
        r="3"
        fill="var(--color-light)"
        :stroke="colors[metrics[hoverFrame.name].color][2]"
        stroke-width="1.5"
        stroke-opacity="0.8"
      />
    </g>
  </svg>
</template>

<script setup>
import * as d3 from "d3";
import { onMounted, watch, ref, computed } from "vue";
import _ from "lodash";

import {
  getDirectScalers,
  getIndexSeries,
  getLimitedNumber,
} from "../utils/DataProcess";
import { colors } from "../utils/ColorStyle";

const margin = 8;
const viewSizeH = 130;
const viewSizeW = 720;
const tickGapX = 100;
const tickGapY = 20;
const EPS = 1e-8;

const defaultSpace = [
  [0, 100],
  [0, 10],
];

const props = defineProps(["metrics", "name", "focusMode"]);
const emit = defineEmits(["locateFrame"]);

const line = ref(null);
const hoverFrame = ref(null);

const [dynamicAxisX, dynamicAxisY] = [
  (g, scaleX) =>
    g.call(
      d3
        .axisBottom(scaleX)
        .ticks(viewSizeW / tickGapX)
        .tickSizeOuter(0)
    ),
  (g, scaleY) =>
    g
      .call(
        d3
          .axisLeft(scaleY)
          .ticks(viewSizeH / tickGapY)
          .tickFormat(getLimitedNumber)
      )
      .call((g) => g.select(".domain").remove())
      .call((g) =>
        g
          .selectAll(".tick")
          .selectAll("text")
          .attr("dx", "4")
          .attr("dy", "-4")
          .attr("transform", "rotate(-45)")
      ),
];

const getScaleY = (domainX) =>
  d3
    .scaleLinear()
    .domain(
      _.isEmpty(props.metrics)
        ? defaultSpace[1]
        : d3.extent(
            _.flatten(
              _.map(props.metrics, ({ values }) =>
                _.map(
                  _.filter(values, (v) => _.inRange(v[0], ...domainX)),
                  (pos) => pos[1]
                )
              )
            )
          )
    )
    .range([margin + viewSizeH, margin]);

const drawHorizonTickLines = (g) =>
  g
    .call((g) => g.selectAll("#horizon-hint").remove())
    .call((g) =>
      g
        .selectAll(".tick line")
        .clone()
        .attr("id", "horizon-hint")
        .attr("x2", viewSizeW)
        .attr("stroke-opacity", 0.1)
    );

const isHoverPath = (name) => {
  if (_.isNull(hoverFrame.value)) {
    return true;
  }
  return hoverFrame.value.name === name;
};

const SN = computed(() =>
  _.fromPairs(
    _.map(props.metrics, ({ values }, name) => [
      name,
      getIndexSeries(_.map(values, (v) => v[0])),
    ])
  )
);

const onLeave = () => (hoverFrame.value = null);

const onMove = (scaleX, scaleY) => (event) => {
  if (!props.focusMode || _.isEmpty(props.metrics)) {
    hoverFrame.value = null;
    return;
  }

  const [xm, ym] = d3.pointer(event);
  const { name, pos } = d3.least(
    _.concat(
      ..._.map(props.metrics, (d, name) =>
        _.map(d.values, (v) => ({ name: name, pos: v }))
      )
    ),
    ({ pos }) =>
      Math.hypot(scaleX(pos[0]) + 3 * margin - xm, scaleY(pos[1]) - ym)
  );
  const [xt, yt] = [scaleX(pos[0]) + 3 * margin, scaleY(pos[1])];
  const [leftBound, rightBound] = scaleX.domain();

  if (!_.inRange(pos[0], leftBound, rightBound + EPS)) {
    hoverFrame.value = null;
    return;
  }
  hoverFrame.value = {
    name,
    frame: _.toString(pos[0]),
    metric: pos[1],
    pos: [xt, yt],
    isAboveHalf: [xt > viewSizeW / 2, yt > viewSizeH / 2],
  };
};

const onZoom = (scaleX) => (event) => {
  const svg = d3.select(`#metrics-${props.name}`);
  const reScaleX = event.transform.rescaleX(scaleX);
  const reScaleY = getScaleY(reScaleX.domain());

  svg.select(".x-axis").call(dynamicAxisX, reScaleX);
  svg.select(".y-axis").call(dynamicAxisY, reScaleY).call(drawHorizonTickLines);
  svg.on("pointermove", onMove(reScaleX, reScaleY));
  line.value = d3
    .line()
    .curve(d3.curveLinear)
    .x((pos) => reScaleX(pos[0]))
    .y((pos) => reScaleY(pos[1]));
  hoverFrame.value = null;
};

const onClick = () => {
  if (_.isNull(hoverFrame.value)) {
    return;
  }

  const { name, frame } = hoverFrame.value;

  emit("locateFrame", name, frame);
};

const refreshCanvas = (metrics) => {
  const svg = d3.select(`#metrics-${props.name}`);
  const space = _.zip(..._.concat(..._.map(metrics, (d) => d.values)));
  const [axisScaleX, axisScaleY] = getDirectScalers(
    d3.extent(_.isEmpty(metrics) ? defaultSpace[0] : space[0]),
    d3.extent(_.isEmpty(metrics) ? defaultSpace[1] : space[1]),
    margin,
    viewSizeW,
    viewSizeH
  );

  svg.select(".x-axis").call(dynamicAxisX, axisScaleX);
  svg
    .select(".y-axis")
    .call(dynamicAxisY, axisScaleY)
    .call(drawHorizonTickLines);
  svg
    .call(
      d3
        .zoom()
        .scaleExtent([1, 8])
        .extent([
          [margin, 0],
          [margin + viewSizeW, viewSizeH],
        ])
        .translateExtent([
          [margin, -Infinity],
          [margin + viewSizeW, Infinity],
        ])
        .on("zoom", onZoom(axisScaleX))
    )
    .on("pointermove", onMove(axisScaleX, axisScaleY));
  svg.on("click", onClick);
  svg.on("pointerleave", onLeave);
  line.value = d3
    .line()
    .curve(d3.curveLinear)
    .x((pos) => axisScaleX(pos[0]))
    .y((pos) => axisScaleY(pos[1]));
};

watch(
  () => props.metrics,
  (newMetrics) => refreshCanvas(newMetrics)
);

onMounted(() => refreshCanvas(props.metrics));
</script>

<style scoped></style>
