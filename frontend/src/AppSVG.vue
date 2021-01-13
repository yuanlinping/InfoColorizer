<template>
  <el-container id="app">
    <el-container style="height: 900px; background-color: #fff">
      <el-aside width="13%" style="border-right: 1px solid #dddfe5">
        <ContentPanelView></ContentPanelView>
      </el-aside>
      <el-main
        width="40%"
        style="
          padding: 0px;
          overflow-y: hidden;
          border-right: 1px solid #dddfe5;
        "
      >
        <SettingToolBar></SettingToolBar>
        <PaintingView></PaintingView>
      </el-main>
      <el-aside width="37%" style="overflow-y: hidden">
        <PaletteView></PaletteView>
        <!-- use for calculating the size of svg -->
        <InteractiveView></InteractiveView>
      </el-aside>
    </el-container>
  </el-container>
</template>

<script>
import PaintingView from "./components/PaintingView/PaintingView.vue";
import ContentPanelView from "./components/ContentPanelView/ContentPanelView.vue";
import SettingToolBar from "./components/SettingToolBar/SettingToolBar.vue";
import PaletteView from "./components/PaletteView/PaletteView.vue";
import InteractiveView from "./components/InteractiveView/InteractiveView.vue";

export default {
  name: "app",
  components: {
    PaintingView,
    ContentPanelView,
    SettingToolBar,
    PaletteView,
    InteractiveView,
  },
};
</script>


<style lang="scss">
html {
  height: 100%;
  font-family: "Roboto";
}

@font-face {
  font-family: "Roboto";
  src: url("assets/font/Roboto-Regular.ttf") format("truetype"); /* Chrome 4+, Firefox 3.5, Opera 10+, Safari 3—5 */
}

#app {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 10;
}
</style>
