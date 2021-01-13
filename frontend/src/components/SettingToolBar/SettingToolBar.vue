<template>
  <v-card color="grey lighten-4" flat height="48px" tile>
    <v-toolbar dense>
      <el-tooltip content="Undo" placement="bottom">
        <v-btn icon>
          <v-icon>undo</v-icon>
        </v-btn>
      </el-tooltip>
      <el-tooltip content="Redo" placement="bottom">
        <v-btn icon>
          <v-icon>redo</v-icon>
        </v-btn>
      </el-tooltip>

      <v-divider class="mx-4" inset vertical></v-divider>

      <el-tooltip content="Add text" placement="bottom">
        <v-btn icon @click="addNewText">
          <v-icon>format_shapes</v-icon>
        </v-btn>
      </el-tooltip>
      <el-tooltip content="Font size" placement="bottom">
        <v-btn icon>
          <v-icon>format_size</v-icon>
        </v-btn>
      </el-tooltip>
      <el-tooltip content="Bold" placement="bottom">
        <v-btn icon>
          <v-icon>format_bold</v-icon>
        </v-btn>
      </el-tooltip>
      <el-tooltip content="Italic" placement="bottom">
        <v-btn icon>
          <v-icon>format_italic</v-icon>
        </v-btn>
      </el-tooltip>
      <el-tooltip content="Underline" placement="bottom">
        <v-btn icon>
          <v-icon>format_underline</v-icon>
        </v-btn>
      </el-tooltip>

      <v-divider class="mx-4" inset vertical></v-divider>

      <el-col :span="6">
        <el-tooltip content="Import colors" placement="bottom">
          <el-input
            placeholder="Import colors"
            v-model="importedColorString"
          ></el-input>
        </el-tooltip>
      </el-col>

      <el-tooltip content="Import" placement="bottom">
        <v-btn icon @click="importColors">
          <v-icon>add_circle</v-icon>
        </v-btn>
      </el-tooltip>

      <v-divider class="mx-4" inset vertical></v-divider>

      <el-tooltip content="Download" placement="bottom">
        <v-btn icon @click="saveCurrentRecoloredInfo">
          <v-icon>save_alt</v-icon>
        </v-btn>
      </el-tooltip>

      <el-col :span="2">
        <el-tooltip content="Select a color" placement="bottom">
          <div>
            <el-color-picker
              v-model="userSpecificColor"
              @change="changeUserSpecificColor"
              :predefine="predefineColors"
            ></el-color-picker>
          </div>
        </el-tooltip>
      </el-col>

      <el-col :span="6">
        <el-tooltip content="Select a color term" placement="bottom">
          <el-autocomplete
            class="inline-input"
            v-model="userColorName"
            :fetch-suggestions="querySearch"
            placeholder="Vague Preference"
            @select="changeUserColorName"
          ></el-autocomplete>
        </el-tooltip>
      </el-col>
    </v-toolbar>
  </v-card>
</template>



<script>
import store from "../../service/store.js";
import { COLORNAMES, COLORPICKERPREDEFINED } from "../../service/variables.js";
/*global _*/
export default {
  name: "SettingToolBar",
  data() {
    return {
      colorNamesInput: COLORNAMES,

      userSpecificColor: null,
      userColorName: null,
      predefineColors: COLORPICKERPREDEFINED,

      importedColorString: null,
    };
  },
  methods: {
    querySearch(queryString, cb) {
      var links = this.colorNamesInput;
      var results = queryString
        ? links.filter(this.createFilter(queryString))
        : links;
      results = _.map(results, (d) => {
        let dict = {};
        dict.value = d;
        return dict;
      });
      cb(results);
    },
    createFilter(queryString) {
      return (link) => {
        return link.toLowerCase().indexOf(queryString.toLowerCase()) === 0;
      };
    },

    changeUserSpecificColor() {
      let curElementMS = store.getters.getCurElementsMultiSelected;
      if (curElementMS.length == 0) {
        this.$message.error(
          "No elements are selected to be assigned a color. Please first select elements in the preference panel."
        );
      } else {
        store.commit(`changeUserSpecificColor`, this.userSpecificColor);
      }
    },
    saveCurrentRecoloredInfo() {
      store.commit(`changeSaveRecoloredInfogState`, true);
    },

    changeUserColorName() {
      store.commit(`changeUserColorName`, this.userColorName);
    },
    addNewText() {
      store.commit(`changeNewTextToCreated`, true);
    },

    // import color palettes
    importColors() {
      let hexCodes = [];
      if (this.importedColorString.includes("<palette>")) {
        let temp = this.importedColorString.match(/rgb='[0-9a-f]{6}'/gi); // format: ["rgb='342E59'", "rgb='50B4BF'", "rgb='73D9CF'", "rgb='9BF2DA'", "rgb='D9A19C'"]
        for (let i = 0; i < temp.length; i++) {
          let c = temp[i].split("=")[1].replace(/'/g, "");
          hexCodes.push("#" + c);
        }
      } else {
        let temp = this.importedColorString.split(/[ ,]/); // format: ["#f7fcfd", "#e5f5f9", "#ccece6"] or ["f7fcfd", "e5f5f9", "ccece6"]
        console.log(temp);
        for (let i = 0; i < temp.length; i++) {
          let c = temp[i].replace(/#/g, ""); // remove "#" then add back
          hexCodes.push("#" + c);
        }
      }
      this.predefineColors = this.predefineColors.concat(hexCodes);
    },
  },
};
</script>

<style>
@import url("//unpkg.com/element-ui@2.13.1/lib/theme-chalk/index.css");
#object-properties {
  width: 100%;
  border-bottom: 1px solid #f8faf8;
  background-color: #eef1f6;
}
</style>