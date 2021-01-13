<template>
  <div class="wrapper">
    <canvas id="inputImageCanvas"></canvas>
  </div>
</template>

<script src="./InteractiveView.js"></script>>
<style lang="scss">
.wrapper {
  display: none;
  position: relative;
  width: 400px;
  height: 400px;
}

.wrapper canvas {
  position: absolute;
  top: 0;
  left: 0;
}
</style>