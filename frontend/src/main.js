import Vue from 'vue'
import AppSvg from './AppSVG.vue'
import Element from "element-ui";
import locale from 'element-ui/lib/locale/lang/en'
import vuetify from '@/plugins/vuetify'
import VueEasyCm from 'vue-easycm'
import store from "./service/store.js"

import init from "./utils/initialize";
import 'element-ui/lib/theme-chalk/index.css'

init();

Vue.config.productionTip = false

Vue.use(Element, { locale });
Vue.use(VueEasyCm);

new Vue({
  el: "#app",
  store,
  vuetify,
  render: h => h(AppSvg),
})