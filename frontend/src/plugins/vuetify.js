import Vue from 'vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'
import 'material-design-icons-iconfont/dist/material-design-icons.css'
// (note) icons are from: https://material.io/resources/icons/?style=baseline

Vue.use(Vuetify)

const opts = {
    icons: {
        iconfont: 'md',
    },
}

export default new Vuetify(opts)