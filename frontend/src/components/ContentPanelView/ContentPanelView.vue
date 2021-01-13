<template>
  <el-menu :default-openeds="['5']">
    <el-submenu index="1">
      <template slot="title"> Shapes </template>
      <div class="contentContainer">
        <div
          v-for="(ele, key) in shapeNodeData"
          :key="key"
          class="iconContainer"
          @mousedown.stop.prevent="dragSvgNode(ele.icon)"
        >
          <img class="icon" :src="ele.icon" />
        </div>
      </div>
    </el-submenu>

    <el-submenu index="2">
      <template slot="title"> Icons </template>
      <div class="contentContainer">
        <div
          v-for="(ele, key) in iconNodeData"
          :key="key"
          class="iconContainer"
          @mousedown.stop.prevent="dragSvgNode(ele.icon)"
        >
          <img class="icon" :src="ele.icon" />
        </div>
      </div>
    </el-submenu>

    <el-submenu index="4">
      <template slot="title"> SVG </template>
      <div class="contentContainer_2">
        <div
          v-for="(ele, key) in templateData"
          :key="key"
          class="imageContainer"
          @mousedown.stop.prevent="dragSvgNode(ele.icon)"
        >
          <img class="icon" :src="ele.icon" />
        </div>
      </div>
    </el-submenu>
  </el-menu>
</template>

<script>
import shapeNodeData from "../../data/contentShape";
import iconNodeData from "../../data/contentIcon";
import templateData from "../../data/contentTemplate";
import imageData from "../../data/contentImage";
import store from "../../service/store.js";
export default {
  name: "ContentPanelView",
  data() {
    return {
      shapeNodeData: [],
      iconNodeData: [],
      templateData: [],
      imageData: [],
    };
  },
  components: {},
  methods: {
    dragSvgNode(url) {
      store.commit(`changeNewSvgToCreated`, url);
    },

    dragImageNode(url, numInImg) {
      store.commit(`changeNewImgToCreated`, [url, numInImg]);
    },
    initToolbarNodes() {
      this.shapeNodeData = shapeNodeData;
      this.iconNodeData = iconNodeData;
      this.templateData = templateData;
      this.imageData = imageData;
    },
  },
  mounted() {
    this.initToolbarNodes();
  },
  created() {},
};
</script>

<style scoped>
.el-menu {
  box-shadow: 0px 0px 2px -1px rgba(0, 0, 0, 0.2),
    1px 0px 6px 0 rgba(0, 0, 0, 0.14), -1px 0px 6px 0 rgba(0, 0, 0, 0.12);
  border: none;
  font-size: 20px;
}
.el-submenu__title {
  font-size: 18px;
}
.contentContainer {
  width: 95%;
  padding-left: 20px;
}

.iconContainer {
  display: inline-block;
  position: relative;
  width: 70px;
  height: 70px;
  padding: 5;
}

.contentContainer_2 {
  display: grid;
  justify-content: space-around;
  align-content: space-evenly;
}

.imageContainer {
  display: inline-block;
  position: relative;
  width: 200px;
  height: 200px;
  padding: 5;
}

.icon {
  max-width: 90%;
  max-height: 90%;
  min-width: 90%;
  max-height: 90%;
}
</style>