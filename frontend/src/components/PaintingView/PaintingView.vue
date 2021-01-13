<template>
  <div id="paintingDiv" @contextmenu="$easycm($event, $root, 1)">
    <canvas ref="paintingCanvas" style="height:100% width:100%"></canvas>
    <easy-cm
      :list="contextMenu"
      :tag="1"
      @ecmcb="contextMenuHandler"
      :underline="true"
      :arrow="true"
    ></easy-cm>
  </div>
</template>



<script src="./PaintingView.js"></script>

<style scoped>
#paintingDiv {
  width: 100%;
  height: 100%;
  background-color: #f0f0f0;
}
</style>