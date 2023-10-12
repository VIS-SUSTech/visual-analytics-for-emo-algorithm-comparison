<template>
  <n-config-provider
    class="container"
    :themeOverrides="themeOverrides"
    preflight-style-disabled
  >
    <div class="bars-side">
      <div
        v-for="(
          { scaleX, isAboveHalf, best, bestSN, current, currentSN }, name
        ) in calcBars"
        :key="name"
      >
        <span>{{ _.truncate(name, { length: 5, omission: "." }) }}</span>
        <n-tooltip placement="left" trigger="hover">
          <template #trigger>
            <svg
              :id="`bar-${props.id}-${name}`"
              :viewBox="`0 0 ${viewSizeBarsW + 2 * margin} ${
                viewSizeBarsH + 2 * margin
              }`"
            >
              <g class="best" :transform="`translate(1, ${margin})`">
                <rect
                  :fill="colors[props.color][1]"
                  :height="viewSizeBarsH / (_.isNil(current) ? 1 : 2)"
                  :width="scaleX(best)"
                />
                <text
                  font-size="24"
                  :x="scaleX(best)"
                  :y="margin + viewSizeBarsH / (_.isNil(current) ? 2 : 4)"
                  :text-anchor="isAboveHalf(best) ? 'end' : 'start'"
                  :dx="isAboveHalf(best) ? -margin : margin"
                  :fill="
                    isAboveHalf(best) ? colors[color][0] : colors[color][1]
                  "
                >
                  {{ getExponentialNumber(best, 3) }}
                </text>
              </g>
              <g
                v-if="!_.isNil(current)"
                class="current"
                :transform="`translate(1, ${margin + viewSizeBarsH / 2})`"
              >
                <rect
                  :fill="colors[props.color][0]"
                  :height="viewSizeBarsH / 2"
                  :width="scaleX(current)"
                />
                <text
                  font-size="24"
                  :x="scaleX(current)"
                  :y="margin + viewSizeBarsH / 4"
                  :text-anchor="isAboveHalf(current) ? 'end' : 'start'"
                  :dx="isAboveHalf(current) ? -margin : margin"
                  :fill="
                    isAboveHalf(current) ? colors[color][2] : colors[color][1]
                  "
                >
                  {{ getExponentialNumber(current, 3) }}
                </text>
              </g>
              <g class="axis" :transform="`translate(1, 0)`">
                <line
                  :stroke="colors[props.color][2]"
                  stroke-width="2"
                  :y2="2 * margin + viewSizeBarsH"
                />
              </g>
            </svg>
          </template>
          <div>
            <span class="bold-item">Best </span>
            {{ best }}
            <span>(@ </span>
            <span class="bold-item">#{{ bestSN }}</span>
            <span>): </span>
          </div>
          <div v-if="!_.isNil(current)">
            <span class="bold-item">Current </span>
            {{ current }}
            <span>(@ </span>
            <span class="bold-item">#{{ currentSN }}</span>
            <span>): </span>
          </div>
        </n-tooltip>
      </div>
    </div>
    <div class="area-side">
      <n-tooltip placement="right" trigger="hover">
        <template #trigger>
          <svg
            :id="`area-${props.id}`"
            :viewBox="`0 0 ${viewSizeAreaW + 2 * margin} ${
              viewSizeAreaH + 2 * margin
            }`"
          >
            <defs>
              <pattern
                :id="`diagonal-${id}`"
                width="8"
                height="8"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M-2,2 l4,-4 M0,8 l8,-8 M6,10 l4,-4"
                  :stroke="colors[props.color][1]"
                  stroke-width="4"
                />
              </pattern>
            </defs>
            <g
              v-for="(v, i) in area(props.area.best)"
              :key="i"
              class="best"
              :transform="`translate(${margin}, ${margin})`"
              style="mix-blend-mode: multiply"
            >
              <path
                v-if="i === 0"
                :stroke="colors[props.color][2]"
                stroke-width="2"
                :fill="colors[props.color][1]"
                :fill-opacity="0.5"
                :d="v"
              />
              <line
                v-if="i === 1"
                :stroke="colors[props.color][2]"
                stroke-width="2"
                :x1="v[1]"
                :x2="v[1]"
                :y2="viewSizeAreaH"
              />
              <text
                v-if="i === 1"
                :fill="colors[props.color][2]"
                :x="v[1]"
                :text-anchor="v[2] ? 'end' : 'start'"
                :dx="v[2] ? -margin : margin"
                y="16"
                font-size="20"
              >
                {{ getExponentialNumber(v[0], 3) }}
              </text>
            </g>
            <template v-if="!_.isNil(props.area.current)">
              <g
                v-for="(v, i) in area(props.area.current)"
                :key="i"
                class="current"
                :transform="`translate(${margin}, ${margin})`"
                style="mix-blend-mode: multiply"
              >
                <path
                  v-if="i === 0"
                  :stroke="colors[props.color][1]"
                  stroke-width="2"
                  :fill="`url(#diagonal-${id})`"
                  :fill-opacity="0.5"
                  :d="v"
                />
                <line
                  v-if="i === 1"
                  :stroke="colors[props.color][1]"
                  stroke-width="2"
                  :x1="v[1]"
                  :x2="v[1]"
                  :y1="32"
                  :y2="viewSizeAreaH"
                />
                <text
                  v-if="i === 1"
                  :fill="colors[props.color][1]"
                  :x="v[1]"
                  :text-anchor="v[2] ? 'end' : 'start'"
                  :dx="v[2] ? -margin : margin"
                  y="48"
                  font-size="20"
                >
                  {{ getExponentialNumber(v[0], 3) }}
                </text>
              </g>
            </template>
            <g class="axis" :transform="`translate(${margin}, ${margin})`">
              <line
                :stroke="colors[props.color][2]"
                stroke-width="2"
                :y1="viewSizeAreaH"
                :y2="viewSizeAreaH"
                :x2="viewSizeAreaW"
              />
            </g>
          </svg>
        </template>
        <h4 style="margin: 0">{{ METRIC_DIST.origin }} Distribution</h4>
        <br />
        <div>
          <span class="bold-item">Best Average</span>
          {{ area(props.area.best)[1][0] }}
          <span> (@ </span>
          <span class="bold-item">#{{ props.area.bestSN }}</span>
          <span>): </span>
        </div>
        <div v-if="!_.isNil(props.area.current)">
          <span class="bold-item">Current Average</span>
          {{ area(props.area.current)[1][0] }}
          <span> (@ </span>
          <span class="bold-item">#{{ props.area.currentSN }}</span>
          <span>): </span>
        </div>
      </n-tooltip>
    </div>
  </n-config-provider>
</template>

<script setup>
import { computed } from "vue";
import * as d3 from "d3";
import _ from "lodash";
import { NConfigProvider, NTooltip } from "naive-ui";

import { colors } from "../utils/ColorStyle";
import { getExponentialNumber } from "../utils/DataProcess";
import { METRIC_DIST } from "../utils/Constants";

const props = defineProps(["color", "id", "bars", "area", "scaleXStyle"]);

const margin = 8;
const viewSizeBarsH = 64;
const viewSizeBarsW = 192;
const viewSizeAreaH = 224;
const viewSizeAreaW = 192;

const themeOverrides = {
  Popover: {
    fontSize: "var(--font-size-m)",
    padding: "calc(1.5 * var(--space))",
  },
};

const calcBars = computed(() => {
  const bars = {};
  const { origin } = METRIC_DIST;

  _.forEach(props.bars, (bar, name) => {
    if (name === origin) {
      return;
    }
    bars[name] = { ...bar };
    bars[name].scaleX = d3.scaleLinear(bar.range, [
      margin,
      margin + viewSizeBarsW,
    ]);
    bars[name].isAboveHalf = (value) =>
      bars[name].scaleX(value) > viewSizeBarsW / 2;
  });
  return bars;
});

const area = computed(() => (data) => {
  const scaleX = (
    props.scaleXStyle === "sqrt" ? d3.scaleSqrt : d3.scaleLinear
  )()
    .domain(props.area.rangeX)
    .range([0, viewSizeAreaW]);
  const bins = d3.bin(scaleX.domain()).thresholds(METRIC_DIST.bins)(data);
  const scaleY = d3
    .scaleLinear()
    .domain(props.area.rangeY)
    .range([viewSizeAreaH, 0]);
  const res = _.map(bins, (b) => [_.mean([b.x0, b.x1]), _.size(b)]);
  const avg = _.mean(data);
  const scaledAvg = scaleX(avg);

  return [
    d3
      .area()
      .curve(d3.curveStep)
      .x((d) => scaleX(d[0]))
      .y0(scaleY(0))
      .y1((d) => scaleY(d[1]))(res),
    [avg, scaledAvg, scaledAvg > viewSizeAreaW / 2],
  ];
});
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: row;
  width: 100%;
}

.bars-side {
  display: flex;
  overflow-y: auto;
  flex-direction: column;
  justify-content: space-between;
  flex: 0 0 50%;
}

.bars-side > div {
  display: flex;
}

.bars-side span {
  writing-mode: vertical-lr;
  text-align: center;
  transform: rotate(180deg);
  flex: 0 0 10%;
}

.bars-side svg {
  height: calc(1.25 * var(--title-height));
  flex: 1 0 85%;
}

.area-side {
  flex-direction: column;
  flex: 0 0 50%;
}

.area-side svg {
  height: 100%;
  width: 100%;
}

.area-metric {
  position: relative;
  top: 0;
  left: 0;
}

.bold-item {
  font-weight: bold;
}
</style>
