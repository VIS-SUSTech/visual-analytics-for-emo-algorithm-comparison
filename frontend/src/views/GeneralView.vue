<template>
  <div class="container">
    <h4>{{ problem }}</h4>
    <div class="spacer" />
    <div class="description">
      {{ problemInfo.desc ?? "Loading..." }}
    </div>
  </div>
  <div class="spacer" />
  <div class="container" style="font-size: var(--font-size-l)">
    <div class="item">
      Dimensions of Object
      <span class="detail">
        {{ problemInfo.obj ?? "Loading..." }}
      </span>
    </div>
    <div class="item">
      Dimensions of Decision
      <span class="detail">
        {{ problemInfo.dec ?? "Loading..." }}
      </span>
    </div>
    <div class="item">
      Available Algorithms
      <span class="detail">
        {{ problemInfo.algorithms ?? "Loading..." }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

import { getInfo } from "../utils/Network";

const props = defineProps(["problem"]);

const problemInfo = ref({});

watch(
  () => props.problem,
  (newProblem) => getInfo(newProblem, (info) => (problemInfo.value = info)),
  { immediate: true }
);
</script>

<style scoped>
.container {
  display: flex;
  flex: 0 0 calc(50% - 0.5 * var(--space));
  flex-direction: column;
}

.spacer {
  flex: 0 0 var(--space);
}

.description {
  overflow: auto;
  flex: 0 0 calc(100% - var(--font-size-l) - var(--space));
}

.item {
  display: flex;
  align-items: center;
}

.item:not(:first-of-type) {
  margin-top: var(--space);
}

.detail {
  display: flex;
  flex-grow: 1;
  font-weight: bold;
  justify-content: flex-end;
}

h4 {
  margin: 0;
  flex: 0 0 var(--font-size-l);
}
</style>
