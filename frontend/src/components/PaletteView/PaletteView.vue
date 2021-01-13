<template>
  <div id="paletteview" class="paletteview">
    <div id="tooltipContainer"></div>
    <el-row :gutter="20" type="flex">
      <el-col :span="8">
        <v-btn class="ma-2 requestBtn" @click="requestTreeConstruction"
          >Analyze Infographic</v-btn
        >
      </el-col>
      <el-col :span="10" :offset="6">
        <v-btn class="ma-2 requestBtn" @click="requestRecommendationResults"
          >Get Recommendations</v-btn
        >
      </el-col>
    </el-row>

    <div id="userPreferenceDiv">
      <el-divider content-position="center">Color Preferences</el-divider>
      <el-row :gutter="20" type="flex" justify="center" align="middle">
        <el-col :span="4">
          <el-tooltip content="Bind elements" placement="bottom">
            <v-btn
              class="mx-2 editorBtn"
              small
              dark
              @click="bindMultiSelectedElements"
            >
              <v-icon dark>link</v-icon>
            </v-btn>
          </el-tooltip>
        </el-col>
        <el-col :span="4">
          <el-tooltip content="Unbind elements" placement="bottom">
            <v-btn
              class="mx-2 editorBtn"
              small
              dark
              @click="unbindMultiSelectedElements"
            >
              <v-icon dark>link_off</v-icon>
            </v-btn>
          </el-tooltip>
        </el-col>
        <el-col :span="4">
          <el-tooltip content="Clear One" placement="bottom">
            <v-btn
              class="mx-2 editorBtn"
              small
              dark
              @click="clearUserPreference"
            >
              <v-icon dark>format_color_reset</v-icon>
            </v-btn>
          </el-tooltip>
        </el-col>
        <el-col :span="4">
          <el-tooltip content="Reset All" placement="bottom">
            <v-btn
              class="mx-2 editorBtn"
              small
              dark
              @click="resetAllPreference"
            >
              <v-icon dark>clear</v-icon>
            </v-btn>
          </el-tooltip>
        </el-col>

        <el-col :span="4">
          <el-tooltip content="Copy origin" placement="bottom">
            <v-btn
              class="mx-2 editorBtn"
              small
              dark
              @click="keepColorsWithOriginal"
            >
              <v-icon dark>file_copy</v-icon>
            </v-btn>
          </el-tooltip>
        </el-col>
        <el-col :span="4">
          <el-tooltip content="Bookmark" placement="bottom">
            <v-btn
              class="mx-2 editorBtn"
              small
              dark
              @click="bookmarkARecommendation"
            >
              <v-icon dark>bookmark</v-icon>
            </v-btn>
          </el-tooltip>
        </el-col>
      </el-row>
      <svg id="userPreferenceSvg" class="paletteSvg" style="height: 150px" />
    </div>

    <div id="originalDiv">
      <el-divider content-position="center">Original Colors</el-divider>
      <svg id="originalSvg" class="paletteSvg" style="height: 40px" />
    </div>
    <div id="bookmarkDiv">
      <el-divider content-position="center">Bookmarks</el-divider>
      <div id="bookmarkSlideDiv">
        <svg id="bookmarkSvg" class="paletteSvg" />
      </div>
    </div>
    <div id="recommendDiv">
      <el-divider content-position="center">Recommendations</el-divider>
      <el-row :gutter="20" style="margin-bottom: 10px">
        <el-col :span="4">
          <v-btn
            class="recommendBtn"
            small
            @click="goToPreviousOrNextIteration(-1)"
          >
            <v-icon dark>navigate_before</v-icon>
          </v-btn>
        </el-col>
        <el-col :span="4" :offset="16">
          <v-btn
            class="recommendBtn"
            small
            @click="goToPreviousOrNextIteration(1)"
          >
            <v-icon dark>navigate_next</v-icon>
          </v-btn>
        </el-col>
      </el-row>
      <div id="recommendSlideDiv">
        <svg id="recommendSvg" class="paletteSvg" />
      </div>
    </div>
  </div>
</template>

<script src="./PaletteView.js"></script>
<style lang="scss">
#paletteview {
  margin: 10px;
  margin-top: 7px;

  .tooltip {
    position: absolute;
    text-align: center;
    width: 100px;
    height: 50px;
    padding: 8px;
    font: 10px sans-serif;
    background: #fff;
    border: solid 1px #aaa;
    border-radius: 8px;
    pointer-events: none;
  }

  .el-row {
    margin-bottom: 5px;
    &:last-child {
      margin-bottom: 0;
    }
  }

  .el-divider__text {
    font-size: 22px;
  }

  .el-button--primary.is-plain {
    color: #409eff;
    background: #ecf5ff;
    border-color: #b3d8ff;
    padding: 3px;
    width: 70px;
  }

  .requestBtn {
    // buttons for requesting network service
    background-color: #424242;
    color: #fff;
  }
  .editorBtn {
    // buttons in edior panel
    background-color: #424242;
    color: #fff;
  }
  .recommendBtn {
    // buttons in recommend panel
    background-color: #424242;
    color: #fff;
  }
  .clickedBtn {
    color: #fff;
    background-color: #409eff;
    border-color: #409eff;
    border: radius 4px;
    padding: 6px;
    width: 80px;
  }
  .paletteSvg {
    width: 100%;
  }
  #recommendDiv {
    height: 400px;
    width: 100%;

    #recommendSlideDiv {
      height: 100%;
      overflow-y: auto;
      #recommendSvg {
        height: 320%;
      }
    }
  }

  #bookmarkDiv {
    height: 120px;
    width: 100%;

    #bookmarkSlideDiv {
      height: 100%;
      overflow-y: auto;
      #bookmarkSvg {
        height: 800%;
      }
    }
  }

  .editorRect {
    stroke-width: 1px;
    stroke: #424242;
  }

  .hightlightedEditorRect {
    stroke-width: 4;
    stroke: #ab9382;
  }
}
</style>