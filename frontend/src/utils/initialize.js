export default function () {
    // import jquery and bootstrap
    var $ = require("jquery");
    window.jQuery = window.$ = $;
    require("bootstrap");

    // import lodash
    var _ = require("lodash");
    window._ = _;

    // import d3
    var d3 = require("d3");
    window.d3 = d3;

    d3.cvtColorXXX2Rgb = function (xxx) {
        let newColor = d3.rgb(xxx);
        return [newColor['r'], newColor['g'], newColor['b']];
    }

    d3.cvtColorXXX2Lab = function (xxx) { // xxx is in other color space
        let newColor = d3.lab(xxx)
        return [newColor['l'], newColor['a'], newColor['b']];
    }

    d3.geom = geom;

    d3.translate = function (x, y) {
        return geom.transform
            .begin()
            .translate(x, y)
            .end();
    };
}

var geom = {
    transform: {
        value: "",
        begin: function () {
            this.value = "";
            return this;
        },
        end: function () {
            return this.value;
        },
        translate: function (dx, dy) {
            this.value += "translate(" + dx + "," + dy + ")";
            return this;
        },
        rotate: function (theta, x0, y0) {
            this.value += "rotate(" + theta + "," + x0 + "," + y0 + ")";
            return this;
        },
        scale: function (s) {
            this.value += "scale(" + s + ")";
            return this;
        },
        scaleXY: function (fx, fy) {
            this.value += "scale(" + fx + "," + fy + ")";
            return this;
        }
    }
}
