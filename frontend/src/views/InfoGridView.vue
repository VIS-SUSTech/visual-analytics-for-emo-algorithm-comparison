<template>
  <n-config-provider :theme-overrides="themeOverrides" preflight-style-disabled>
    <n-data-table
      flex-height
      style="height: 100%"
      :columns="tableColumns"
      :data="rowData"
      :bordered="false"
      :single-line="false"
      :scroll-x="`calc(4vw + ${_.size(columns)} * 3.3vw)`"
      size="small"
    />
  </n-config-provider>
</template>

<script setup>
import { computed, h } from "vue";
import {
  NConfigProvider,
  NDataTable,
  NTooltip,
  NEllipsis,
  NTag,
} from "naive-ui";
import _ from "lodash";

import { colors } from "../utils/ColorStyle";
import { getExponentialNumber } from "../utils/DataProcess";
import { METRICS } from "../utils/Constants";

const props = defineProps(["infoGrid", "selectedAlgorithms"]);
const emit = defineEmits(["select"]);

const themeOverrides = {
  common: {
    primaryColor: "#242424",
    primaryColorHover: "#595959",
    primaryColorPressed: "#1f1f1f",
    primaryColorSuppl: "#595959",
  },
  DataTable: {
    fontSizeSmall: "var(--font-size-m)",
    thPaddingSmall: "calc(0.5 * var(--space))",
    tdPaddingSmall: "calc(0.5 * var(--space))",
    sorterSize: "var(--font-size-m)",
  },
  Tag: {
    padding: "calc(0.5 * var(--space))",
    fontSizeSmall: "var(--font-size-m)",
    borderRadius: "var(--radius)",
  },
  Popover: {
    fontSize: "var(--font-size-m)",
    padding: "var(--space)",
  },
};

const columns = _.assign(
  ..._.map(METRICS, ({ optimal }, metric) => ({
    [`Best ${metric}`]: optimal,
    [`Last ${metric}`]: _.last,
  }))
);

const rowData = computed(() =>
  _.map(props.infoGrid, (value, key) =>
    _.assign(
      {
        algorithmName: key,
        color: value.color,
      },
      ..._.map(columns, (func, column) => ({
        [column]: func(_.values(value.metrics[_.split(column, " ")[1]])),
      }))
    )
  )
);

const tableColumns = computed(() => [
  {
    title: "Algorithm",
    key: "algorithmName",
    fixed: "left",
    render: ({ algorithmName, color }) =>
      h(
        NTag,
        {
          title: algorithmName,
          checkable: true,
          size: "small",
          style: {
            "--n-text-color-checkable": colors[color][1],
            "--n-color-checkable": "var(--color-light)",
            "--n-color-hover-checkable": colors[color][0],
            "--n-color-pressed-checkable": colors[color][2],
            "--n-text-color-checked": "var(--color-light)",
            "--n-color-checked": colors[color][1],
            "--n-color-checked-hover": colors[color][0],
            "--n-color-checked-pressed": colors[color][2],
          },
          "onUpdate:checked": () => emit("select", algorithmName),
          checked: _.includes(props.selectedAlgorithms, algorithmName),
        },
        {
          default: () => algorithmName,
        }
      ),
  },
  ..._.map(columns, (_, column) => ({
    title: ({ key }) =>
      h(
        NEllipsis,
        {
          expandTrigger: "hover",
          tooltip: { arrowPointToCenter: true },
        },
        {
          trigger: () => key,
          default: () => key,
        }
      ),
    key: column,
    sorter: (row1, row2) => row1[column] - row2[column],
    render: (rowData) =>
      h(
        NTooltip,
        {
          arrowPointToCenter: true,
        },
        {
          trigger: () => getExponentialNumber(rowData[column], 4),
          default: () => rowData[column],
        }
      ),
  })),
]);
</script>

<style scoped>
.n-config-provider {
  width: calc(100% - 2 * var(--space));
  height: calc(100% - 2 * var(--space));
  position: absolute;
  overflow: auto;
}

:deep(.n-data-table-td:first-of-type),
:deep(.n-data-table-th:first-of-type) {
  border-right: 0.2vh solid var(--color-gray);
  width: 4vw;
}

:deep(.n-data-table-th) {
  font-weight: bold;
  border-bottom: 0.2vh solid var(--color-gray);
}

:deep(.n-data-table-td:not(:first-of-type)),
:deep(.n-data-table-th:not(:first-of-type)) {
  width: 3.3vw;
}

:deep(.n-tag) {
  width: 100%;
  font-weight: bold;
}

:deep(.n-tag > span) {
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  word-break: break-all;
}
</style>
