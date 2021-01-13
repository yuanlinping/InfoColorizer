import { fabric } from "fabric";

export default {
    getNewHightFilter(pixelArr) {
        fabric.Image.filters.Highlight = fabric.util.createClass(
            fabric.Image.filters.BaseFilter,
            {
                type: "Highlight",
                mask: [],
                applyTo2d: function (options) {
                    let imageData = options.imageData,
                        data = imageData.data,
                        len = data.length;

                    for (let i = 0; i < len; i += 4) {
                        data[i + 3] = 50;
                    }

                    for (let p = 0; p < this.mask.length; p++) {
                        let pixel = this.mask[p];
                        let startI = (pixel[0] * imageData.width + pixel[1]) * 4;
                        data[startI + 3] = 255;
                    }
                }
            }
        );

        fabric.Image.filters.Highlight.fromObject =
            fabric.Image.filters.BaseFilter.fromObject;

        return new fabric.Image.filters.Highlight({ mask: pixelArr })
    },

    getNewRecoloredFilter(pixelArr, targetColor, iid) {
        fabric.Image.filters.Recolor = fabric.util.createClass(
            fabric.Image.filters.BaseFilter,
            {
                type: "Recolor",
                newColor: [], // array
                mask: [],
                id: null,
                applyTo2d: function (options) {
                    let imageData = options.imageData,
                        data = imageData.data;

                    for (let p = 0; p < this.mask.length; p++) {
                        let pixel = this.mask[p];
                        let startI = (pixel[0] * imageData.width + pixel[1]) * 4;
                        data[startI + 0] = this.newColor[0];
                        data[startI + 1] = this.newColor[1];
                        data[startI + 2] = this.newColor[2];
                        data[startI + 3] = 255;
                    }
                }
            }
        );

        fabric.Image.filters.Recolor.fromObject =
            fabric.Image.filters.BaseFilter.fromObject;

        return new fabric.Image.filters.Recolor({ mask: pixelArr, newColor: targetColor, id: iid })
    }

}
