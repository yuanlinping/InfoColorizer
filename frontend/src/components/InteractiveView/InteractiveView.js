// import store from "../../service/store.js";
/* global $ _ */

export default {
    name: "palettesView",
    data() {
        return {};
    },
    computed: {
        imageUrl() {
            return this.$store.getters.getImageUrl;
        }
    },
    methods: {
        displayInputImage(imageUrl) { // used for computing areas of elements by using inputImageCanvas
            let img = new Image();
            img.src = imageUrl;
            console.log(img.src)
            img.onload = function () {
                let canv = $("#inputImageCanvas")[0];
                // canv.width = img.width;
                // canv.height = img.height;
                canv.width = 300;
                canv.height = 300;

                let ctx = canv.getContext('2d');
                console.log("before")
                console.log(ctx)
                ctx.drawImage(this, 0, 0)
                console.log("after")
                console.log(ctx)
                let imageData = ctx.getImageData(0, 0, canv.width, canv.height);
                imageData = imageData.data;
                imageData = _.chunk(imageData, 4);
                let white_count = _.reduce(imageData, function (count, ele) {
                    let sum = _.reduce(ele, function (s, e) { return s + e }, 0)
                    if (sum == 0) {
                        return count + 1;
                    } else {
                        return count;
                    }
                }, 0);
                console.log("ctx")
                console.log(imageData);
                console.log(white_count);
            }
        }
    },
    watch: {
        imageUrl(newImageUrl) {
            this.displayInputImage(newImageUrl)
        }
    }
}