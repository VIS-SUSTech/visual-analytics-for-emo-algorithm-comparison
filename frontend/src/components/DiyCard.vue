<template>
  <div :class="['diy-card', { float: props.float }]">
    <slot></slot>
  </div>
</template>

<script setup>
const props = defineProps(["float"]);
</script>

<style scoped>
.diy-card {
  display: flex;
  padding: var(--space);
  border: 0.1vh solid var(--color-gray);
  border-radius: var(--radius);
  background-color: var(--color-light);
}

.diy-card.float {
  border: none;
  box-shadow: var(--shadow);
}
</style>
