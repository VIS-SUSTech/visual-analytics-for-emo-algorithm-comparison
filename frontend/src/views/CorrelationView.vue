<template>
  <n-config-provider :theme-overrides="themeOverrides" preflight-style-disabled>
    <n-popover
      v-if="!_.isNull(hoverNodeIndex)"
      :show="true"
      :x="hoverNodePos[0]"
      :y="hoverNodePos[1]"
      :animated="false"
      :show-arrow="false"
      placement="right-start"
      trigger="manual"
    >
      <div
        :style="`color: ${
          colors[data.colorMap[data.nodes[hoverNodeIndex].name]][1]
        }`"
      >
        <h4>
          {{ props.data.nodes[hoverNodeIndex].name }}
        </h4>
        <span> [ </span>
        <span> Gen. Sample </span>
        <span class="bold-item">
          #{{
            SN[data.nodes[hoverNodeIndex].name][
              data.nodes[hoverNodeIndex].frame
            ]
          }}
        </span>
        <span> ] </span>
      </div>
      <div>
        <span class="bold-item"> {{ props.metricName }}: </span>
        <span>{{ props.data.nodes[hoverNodeIndex].metricValue }}</span>
      </div>
      <div v-if="layoutMode === 'cluster'">
        <template v-if="data.clusters[hoverNodeIndex] !== -1">
          <span>Cluster Index: </span>
          <span class="bold-item"> {{ data.clusters[hoverNodeIndex] }} </span>
        </template>
        <template v-else>
          <span>Outlier</span>
        </template>
      </div>
      <template v-if="_.has(calcNeighbour, hoverNodeIndex)">
        <n-divider />
        <div>
          <span>KNNs (K=</span>
          <span class="bold-item">{{ knnOption.limit }}</span>
          <span>):</span>
        </div>
        <div
          v-for="index in calcNeighbour[hoverNodeIndex].nodes"
          :key="`knn-detail-${index}`"
          :style="`color: ${colors[data.colorMap[data.nodes[index].name]][1]}`"
        >
          <span class="bold-item">
            {{ props.data.nodes[index].name }}
          </span>
          <span> [ </span>
          <span> Gen. Sample </span>
          <span class="bold-item">
            #{{ SN[data.nodes[index].name][data.nodes[index].frame] }}
          </span>
          <template v-if="layoutMode === 'cluster'">
            <span> , </span>
            <template v-if="data.clusters[index] !== -1">
              <span> Cluster Index </span>
              <span class="bold-item">
                {{ data.clusters[index] }}
              </span>
            </template>
            <template v-else>
              <span> Outlier </span>
            </template>
          </template>
          <span> ] </span>
        </div>
      </template>
    </n-popover>
    <n-popover
      v-if="!_.isNull(hoverTimeCurve)"
      :show="true"
      :x="hoverTimeCurvePos[0]"
      :y="hoverTimeCurvePos[1]"
      :animated="false"
      :show-arrow="false"
      placement="right-start"
      trigger="manual"
    >
      <div :style="`color: ${colors[data.colorMap[hoverTimeCurve.name]][1]}`">
        <h4>
          {{ hoverTimeCurve.name }}
        </h4>
        <span> [ </span>
        <span> Samples on Route: </span>
        <span class="bold-item">
          {{ _.size(hoverTimeCurve.nodes) }}
        </span>
        <span> ] </span>
      </div>
      <div v-for="{ frame, index } in hoverTimeCurve.nodes" :key="index">
        <span
          v-if="_.first(hoverTimeCurve.nodes).frame === frame"
          class="bold-item"
        >
          From:
        </span>
        <span
          v-else-if="_.last(hoverTimeCurve.nodes).frame === frame"
          class="bold-item"
        >
          To:
        </span>
        <span
          v-else
          :style="`color: ${colors[data.colorMap[hoverTimeCurve.name]][1]}`"
        >
          ⭣
        </span>
        <span> Gen. Sample </span>
        <span class="bold-item"> #{{ SN[hoverTimeCurve.name][frame] }} </span>
        <span> , </span>
        <template v-if="data.clusters[index] !== -1">
          <span> Cluster Index </span>
          <span class="bold-item">
            {{ data.clusters[index] }}
          </span>
        </template>
        <template v-else>
          <span> Outlier </span>
        </template>
      </div>
    </n-popover>
  </n-config-provider>
  <svg
    id="correlation"
    width="100%"
    height="100%"
    :viewBox="`0 0 ${viewSize + 2 * margin} ${viewSize + 2 * margin}`"
  >
    <defs>
      <clipPath id="graph-zone">
        <rect
          :x="0"
          :y="0"
          :width="viewSize + 2 * margin"
          :height="viewSize + 2 * margin"
        />
      </clipPath>
      <template v-for="curves in calcTimeCurve">
        <marker
          v-for="({ arrowOffset, name }, index) in curves"
          :key="`arrow-${name}-${index}`"
          :id="`arrow-${name}-${index}`"
          markerUnits="userSpaceOnUse"
          markerWidth="12"
          markerHeight="12"
          :refX="12 + arrowOffset"
          refY="6"
          orient="auto"
        >
          <path
            stroke="none"
            d="M2,0 L12,6 L2,12 L4,6 L2,0"
            :fill="colors[props.data.colorMap[name]][1]"
          />
        </marker>
      </template>
    </defs>
    <!-- Active Graph -->
    <template v-if="_.every([scalePre, scaleX, scaleY])">
      <!-- HDBSCAN Clusters -->
      <g
        v-for="({ path }, tag) in clusterHulls"
        :key="`cluster-hull-${tag}`"
        stroke="none"
        fill="var(--color-gray)"
        fill-opacity="0.5"
        clip-path="url(#graph-zone)"
      >
        <path :d="hullBox(path ?? [])" :onclick="() => selectCluster(tag)" />
      </g>
      <!-- Active Cluster Hull -->
      <g
        v-if="!_.isNull(activeCluster)"
        stroke="var(--color-dark)"
        stroke-width="2"
        stroke-opacity="0.5"
        fill="none"
        clip-path="url(#graph-zone)"
      >
        <path :d="hullBox(clusterHulls[activeCluster].path)" />
      </g>
      <!-- Normal KNN Edges -->
      <g
        v-for="(pos, index) in calcEdge"
        :key="`knn-edge-${index}`"
        stroke="var(--color-gray)"
        stroke-opacity="0.7"
        stroke-width="1.5"
        fill="none"
        clip-path="url(#graph-zone)"
      >
        <line
          style="mix-blend-mode: multiply"
          :x1="scaleX(pos[0][0])"
          :y1="scaleY(pos[0][1])"
          :x2="scaleX(pos[1][0])"
          :y2="scaleY(pos[1][1])"
        />
      </g>
      <!-- Time Curves -->
      <g
        v-for="(curves, tcIndex) in calcTimeCurve"
        :key="`time-curve-${tcIndex}`"
        stroke-opacity="0.7"
        fill="none"
        stroke-width="2"
        clip-path="url(#graph-zone)"
      >
        <path
          v-for="({ path, name, nodes }, index) in curves"
          class="time-curve"
          :key="`time-curve-${name}-segment-${index}`"
          :stroke="colors[props.data.colorMap[name]][1]"
          style="mix-blend-mode: multiply"
          :d="timeCurve(path)"
          :marker-end="
            layoutMode === 'cluster' ? `url(#arrow-${name}-${index})` : 'none'
          "
          :onmouseenter="(e) => onHoverTimeCurve(e, name, nodes)"
          :onmouseleave="() => (hoverTimeCurve = null)"
        />
      </g>
      <!-- Hover KNN Edges -->
      <g
        v-for="(pos, index) in getHoverEdges"
        :key="`knn-hover-edge-${index}`"
        stroke="var(--color-dark)"
        stroke-opacity="0.7"
        stroke-width="3"
        fill="none"
        clip-path="url(#graph-zone)"
      >
        <line
          style="mix-blend-mode: multiply"
          :x1="scaleX(pos[0][0])"
          :y1="scaleY(pos[0][1])"
          :x2="scaleX(pos[1][0])"
          :y2="scaleY(pos[1][1])"
        />
      </g>
      <!-- Frame Nodes -->
      <g
        v-for="(nodes, name) in calcNode"
        :key="`nodes-${name}`"
        clip-path="url(#graph-zone)"
      >
        <template
          v-for="({ pos, size, index, color }, frame) in nodes"
          :key="`node-${name}-${frame}`"
        >
          <template v-if="knnOption.showArc && calcNeighbour[index]?.notPure">
            <!-- Neighbour Arcs -->
            <path
              v-for="(arc, aIndex) in calcNeighbour[index]?.arcRanges"
              :key="`neighbour-arc-${aIndex}`"
              :transform="`translate(${scaleX(pos[0])}, ${scaleY(pos[1])})`"
              :d="neighbourArc(size, ...arc.range)"
              :fill="
                isHoverNode(index) && isInActiveCluster(index)
                  ? arc.color
                  : 'var(--color-gray)'
              "
            />
          </template>
          <!-- Inner Circle -->
          <circle
            :fill="
              isHoverNode(index) && isInActiveCluster(index)
                ? color
                : 'var(--color-gray)'
            "
            :stroke="
              (!knnOption.showArc || !calcNeighbour[index]?.notPure) &&
              isHoverNode(index) &&
              isInActiveCluster(index)
                ? colors[props.data.colorMap[name]][1]
                : `var(--color-gray)`
            "
            stroke-width="1"
            :cx="scaleX(pos[0])"
            :cy="scaleY(pos[1])"
            :r="size"
          />
          <!-- Outer Circle -->
          <circle
            v-if="knnOption.showArc && calcNeighbour[index]?.notPure"
            fill="none"
            :stroke="
              isHoverNode(index) && isInActiveCluster(index)
                ? colors[props.data.colorMap[name]][1]
                : 'var(--color-gray)'
            "
            stroke-width="1"
            :cx="scaleX(pos[0])"
            :cy="scaleY(pos[1])"
            :r="arcOuterOffset + size"
          />
          <!-- Outlier Circle -->
          <circle
            v-if="
              layoutMode === 'cluster' &&
              data.clusters[index] === -1 &&
              isHoverNode(index) &&
              isInActiveCluster(index)
            "
            fill="none"
            stroke="var(--color-dark)"
            stroke-width="1"
            :cx="scaleX(pos[0])"
            :cy="scaleY(pos[1])"
            :r="
              size +
              2 +
              (knnOption.showArc && calcNeighbour[index]?.notPure
                ? arcOuterOffset
                : 0)
            "
          />
        </template>
      </g>
    </template>
    <!-- Legends -->
    <g
      v-for="(name, index) in _.keys(props.data.colorMap)"
      :key="`color-${name}`"
      :transform="`translate(${viewSize - 8 * margin}, ${
        (2 * index + 2) * margin
      })`"
    >
      <rect
        stroke="none"
        :fill="colors[props.data.colorMap[name]][1]"
        width="26"
        height="4"
        x="-30"
        y="-6"
      />
    </g>
    <g
      v-for="(name, index) in _.keys(props.data.colorMap)"
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
import * as d3 from "d3";
import { onMounted, ref, watch, computed } from "vue";
import { NConfigProvider, NDivider, NPopover } from "naive-ui";
import _ from "lodash";
import hull from "hull.js";

import { getIndexSeries, getScalers } from "../utils/DataProcess";
import { colors } from "../utils/ColorStyle";

const viewSize = 640;
const margin = 8;
const arcOuterOffset = 4;
const nodeSizeRange = [4, 8];
const hullConcavity = 16;

const themeOverrides = {
  Popover: {
    fontSize: "var(--font-size-m)",
    padding: "var(--space)",
  },
};

const defaultSpace = [
  [0, 10],
  [0, 10],
];

const timeCurve = d3
  .line()
  .x((p) => scaleX.value(p[0]))
  .y((p) => scaleY.value(p[1]))
  .curve(d3.curveNatural);

const hullBox = d3
  .line()
  .x((p) => scaleX.value(p[0]))
  .y((p) => scaleY.value(p[1]))
  .curve(d3.curveCatmullRomClosed.alpha(1));

const neighbourArc = (size, ...arcLength) =>
  d3
    .arc()
    .innerRadius(size)
    .outerRadius(arcOuterOffset + size)
    .startAngle(arcLength[0])
    .endAngle(arcLength[1])();

const calcColor = (vFrom, vTo, colorFrom, colorTo) => {
  const scaleColor = d3.scaleLinear().domain([vFrom, vTo]).range([0, 1]);
  const colorSeries = d3.interpolate(colorFrom, colorTo);

  return (v) => colorSeries(scaleColor(v));
};

const isHoverNode = (index) => {
  if (_.isNull(hoverNodeIndex.value)) {
    return true; // If No Hovering Node, Always Display
  } else if (index === hoverNodeIndex.value) {
    return true;
  }
  // Directed Edge: Neighbour -> Center
  return _.includes(calcNeighbour.value[hoverNodeIndex.value]?.nodes, index);
};

const selectCluster = (index) => {
  const numIndex = _.toNumber(index);

  if (numIndex === activeCluster.value) {
    activeCluster.value = null;
  } else {
    activeCluster.value = numIndex;
  }
};

const isInActiveCluster = (index) => {
  if (_.isNull(activeCluster.value)) {
    return true; // If No Active Cluster, Always Display
  }
  return props.data.clusters[index] === activeCluster.value;
};

const SN = computed(() =>
  _.fromPairs(
    _.map(calcNode.value, (frames, name) => [
      name,
      getIndexSeries(_.keys(frames)),
    ])
  )
);

const calcTimeCurve = computed(() =>
  _.map(props.activeTimeCurve, (algorithm) => {
    const nodes = _.map(calcNode.value[algorithm], (v) =>
      _.pick(v, ["index", "pos", "size"])
    );
    const res = [];

    if (props.layoutMode === "cluster") {
      let [curPath, curNodes] = [[], []];

      _.forEach(nodes, ({ index, pos }, it) => {
        if (it + 1 === _.size(nodes)) {
          return;
        }

        const tagNow = props.data.clusters[index];
        const tagNext = props.data.clusters[nodes[it + 1].index];

        if (tagNow === -1 || tagNext === -1 || tagNow !== tagNext) {
          curPath.push(pos, nodes[it + 1].pos);
          curNodes.push(index, nodes[it + 1].index);
        } else if (!_.isEmpty(curPath)) {
          res.push({
            path: _.uniq(curPath),
            nodes: _.map(_.uniq(curNodes), (n) => ({
              index: n,
              frame: props.data.nodes[n].frame,
            })),
            arrowOffset:
              nodes[it + 1].size +
              (props.knnOption.showArc &&
              calcNeighbour.value[nodes[it + 1].index]?.notPure
                ? arcOuterOffset
                : 0),
            name: algorithm,
          });
          curPath = [];
          curNodes = [];
        }
      });
    } else {
      res.push({
        path: _.map(nodes, ({ pos }) => pos),
        arrowOffset: 0,
        name: algorithm,
      });
    }
    return res;
  })
);

const calcNode = computed(() => {
  const res = {};
  const sizeMap = d3
    .scaleLinear()
    .domain(d3.extent(_.flatten(_.map(props.data.nodes, (n) => n.metricValue))))
    .range(nodeSizeRange);
  const simNodes = [];

  _.forEach(props.data.nodes, ({ frame, name, pos, metricValue }, index) => {
    const size = sizeMap(metricValue);
    const [x, y] = scalePre.value(pos);

    if (!_.has(res, name)) {
      res[name] = {};
    }
    simNodes.push({ index, size, x, y });
    res[name][frame] = {
      pos: index, // Temporary Link
      size,
      index,
    };
  });

  _.forEach(res, (nodes, name) => {
    if (_.isEmpty(nodes)) {
      return;
    }

    const colorMap = calcColor(
      0,
      _.size(nodes),
      colors[props.data.colorMap[name]][0],
      colors[props.data.colorMap[name]][2]
    );
    const order = _.fromPairs(
      _.map(
        _.sortBy(_.keys(nodes), (k) => _.toNumber(k)),
        (k, index) => [k, index]
      )
    );

    _.forEach(nodes, (v, k) => {
      const { x, y } = simNodes[v.pos];

      v.color = colorMap(order[k]);
      v.pos = [x, y];
    });
  });

  return res;
});

const calcEdge = computed(() =>
  _.map(
    _.filter(props.data.edges, ([, , k]) => k <= props.knnOption.limit),
    ([u, v]) => {
      const infoU = props.data.nodes[u];
      const infoV = props.data.nodes[v];

      return [
        calcNode.value[infoU.name][infoU.frame].pos,
        calcNode.value[infoV.name][infoV.frame].pos,
      ];
    }
  )
);

const calcNeighbour = computed(() => {
  const res = {};

  _.forEach(props.data.edges, ([u, v, k]) => {
    if (k > props.knnOption.limit) {
      return;
    }
    // Directed Edge: Neighbour -> Center
    if (_.isNil(res[v])) {
      res[v] = { notPure: false, nodes: [] };
    }
    res[v].nodes.push(u);
    if (props.data.nodes[u].name !== props.data.nodes[v].name) {
      res[v].notPure = true;
    }
  });
  _.forEach(res, ({ notPure, nodes }, curNode) => {
    if (!notPure) {
      return;
    }

    const arcLength = (2 * Math.PI) / _.size(nodes);
    const arcRanges = _.countBy(nodes, (n) => props.data.nodes[n].name);
    let angle = 0;

    res[curNode].arcRanges = _.map(arcRanges, (cnt, name) => ({
      range: [angle * arcLength, (angle += cnt) * arcLength],
      color: colors[props.data.colorMap[name]][1],
    }));
  });
  return res;
});

const getHoverEdges = computed(() => {
  if (_.isNull(hoverNodeIndex.value)) {
    return [];
  }
  // Directed Edge: Neighbour -> Center
  const v = hoverNodeIndex.value;
  const { name, frame } = props.data.nodes[v];
  const posV = calcNode.value[name][frame].pos;

  return _.map(calcNeighbour.value[v]?.nodes, (u) => {
    const { name, frame } = props.data.nodes[u];
    const posU = calcNode.value[name][frame].pos;

    return [posV, posU];
  });
});

const clusterHulls = computed(() => {
  const res = {};

  if (props.layoutMode !== "cluster") {
    return res;
  }
  _.forEach(props.data.clusters, (tag, index) => {
    if (!_.has(res, tag)) {
      _.set(res, tag, { nodes: [] });
    }
    res[tag].nodes.push(index);
  });
  _.forEach(
    res,
    ({ nodes }, tag) =>
      tag !== "-1" &&
      (res[tag].path = hull(
        _.map(nodes, (n) => {
          const { name, frame } = props.data.nodes[n];

          return calcNode.value[name][frame].pos;
        }),
        hullConcavity
      ))
  );
  return res;
});

const props = defineProps([
  "data",
  "activeTimeCurve",
  "metricName",
  "knnOption",
  "layoutMode",
]);
const emit = defineEmits(["locateFrame"]);

const [scaleX, scaleY] = [ref(null), ref(null)];
const scalePre = ref(null);
const [hoverNodeIndex, hoverNodePos] = [ref(null), ref([0, 0])];
const [hoverTimeCurve, hoverTimeCurvePos] = [ref(null), ref([0, 0])];
const activeCluster = ref(null);

const onHoverTimeCurve = (event, name, nodes) => {
  if (props.layoutMode !== "cluster" || _.isNil(nodes)) {
    return;
  }
  hoverTimeCurve.value = { name, nodes };
  hoverTimeCurvePos.value = [
    event.clientX - event.offsetX,
    event.clientY - event.offsetY,
  ];
};

const onMove = (event) => {
  if (_.isEmpty(props.data)) {
    return;
  }

  const dist = ([x1, y1], [x2, y2]) => Math.hypot(x1 - x2, y1 - y2);
  const curPos = d3.pointer(event);
  const { pos, index } = _.minBy(
    _.map(props.data.nodes, ({ name, frame }, index) => {
      const [x, y] = calcNode.value[name][frame].pos;

      return { index, pos: [scaleX.value(x), scaleY.value(y)] };
    }),
    ({ pos }) => dist(pos, curPos)
  );
  const { name, frame } = props.data.nodes[index];
  const totSize =
    calcNode.value[name][frame].size +
    (calcNeighbour.value[index]?.notPure ? arcOuterOffset : 0);

  if (dist(pos, curPos) > totSize || !isInActiveCluster(index)) {
    hoverNodeIndex.value = null;
  } else {
    hoverNodeIndex.value = index;
    hoverNodePos.value = [
      event.clientX - event.offsetX,
      event.clientY - event.offsetY,
    ];
  }
};

const onLeave = () => {
  hoverNodeIndex.value = null;
  hoverTimeCurve.value = null;
};

const onClick = () => {
  if (_.isNull(hoverNodeIndex.value)) {
    return;
  }

  const { name, frame } = props.data.nodes[hoverNodeIndex.value];

  emit("locateFrame", name, SN.value[name][frame]);
};

const onZoom = (dynamicScaleX, dynamicScaleY) => (event) => {
  scaleX.value = event.transform.rescaleX(dynamicScaleX);
  scaleY.value = event.transform.rescaleY(dynamicScaleY);
};

const refreshCanvas = (newData) => {
  const space = _.isEmpty(newData)
    ? defaultSpace
    : _.zip(..._.map(newData.nodes, (d) => d.pos));
  const [scaler, axisScaleX, axisScaleY] = getScalers(
    d3.extent(space[0]),
    d3.extent(space[1]),
    margin,
    viewSize
  );
  const svg = d3.select("#correlation");

  svg.call(d3.zoom().transform, d3.zoomIdentity);
  svg.call(
    d3
      .zoom()
      .scaleExtent([0.5, 10])
      .extent([
        [0, 0],
        [viewSize + 2 * margin, viewSize + 2 * margin],
      ])
      .translateExtent([
        [-0.25 * viewSize, -0.25 * viewSize],
        [1.25 * viewSize, 1.25 * viewSize],
      ])
      .on("zoom", onZoom(axisScaleX, axisScaleY))
  );
  svg.on("pointermove", onMove);
  svg.on("pointerleave", onLeave);
  svg.on("click", onClick);
  scaleX.value = axisScaleX;
  scaleY.value = axisScaleY;
  scalePre.value = scaler;
};

watch(
  () => props.data,
  (newData) => {
    activeCluster.value = null;
    hoverNodeIndex.value = null;
    refreshCanvas(newData);
  }
);

onMounted(() => refreshCanvas(props.data));
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

svg path.time-curve:hover {
  stroke-width: 3;
  stroke-opacity: 1;
}
</style>
