import { tableviewConf } from "../../service/config.js";
import store from "../../service/store.js";
import helper from "../PaletteView/helper.js";
import { SPECIFICCOLORSUBTITUTION } from "../../service/variables.js"

/* global d3 $*/
export default class DrawPalette {
    constructor(canvas) {
        this.canvas = canvas;
    }

    width(val) {
        this.canvasWidth = val;
        return this;
    }

    height(val) {
        this.canvasHeight = val;
        return this;
    }

    setTreeSource(val) { //val: "img", "svg"
        this.treeSource = val;
        return this;
    }
    setDrawType(val) { //val: "editor", "original", "bookmark", "recommended"
        this.drawType = val;
        return this;
    }

    setPaletteData(val) {
        this.paletteData = val;
        return this;
    }

    initDraw() {
        this.tooltipDiv = d3.select("#tooltipContainer")
            .attr("class", "tooltip")
            .style('z-index', '10')
            .style('opacity', '1e-6')
        return this;
    }

    drawNestedPalette() { // for editor palette
        var self = this;
        let paletteData = this.paletteData;
        let subColor = SPECIFICCOLORSUBTITUTION;

        let legendGrid = self.canvasWidth / paletteData.length;
        let legendHeight = tableviewConf.legendHeight;
        let legendRect = this.canvas.selectAll("g").data(paletteData)
            .join(enter => enter.append("g").attr("class", "editorG")
                .attr("transform", (dd, ii) => d3.translate(ii * legendGrid, $("#userPreferenceSvg").height() * 1 / 2 - dd.depth * legendHeight)));
        legendRect.selectAll("rect.editorRect")
            .data(d => [d])
            .join(
                enter => enter.append("rect")
                    .attr("class", "editorRect")
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("width", legendGrid)
                    .attr("height", legendHeight),
            ).style("fill", dd => {

                if (self.treeSource == "svg") {
                    return dd.specificColor === undefined ? d3.rgb(subColor[0], subColor[1], subColor[2]) : (dd.specificColor.length == 3 ? d3.rgb(dd.specificColor[0], dd.specificColor[1], dd.specificColor[2]) : dd.specificColor);
                } else {
                    return dd.specificColor === undefined ? d3.rgb(subColor[0], subColor[1], subColor[2]) : d3.rgb(dd.specificColor[0], dd.specificColor[1], dd.specificColor[2]);
                }
            })

        legendRect.selectAll("line.editorLine")
            .data(d => [d])
            .join(enter => enter.append("line")
                .attr("class", "editorLine")
                .style("stroke", "#424242")
                .attr("x1", 0)
                .attr("y1", 0)
                .attr("x2", legendGrid)
                .attr("y2", legendHeight)
            ).style("visibility", (d) => {
                return d.specificColor === undefined ? "visible" : "hidden"
            })


        legendRect.selectAll("text.editorText")
            .data(d => [d])
            .join(enter => enter.append("text").attr("class", "editorText"))
            .style("fill", "#424242")
            .text(dd => {
                return dd.colorName == undefined ? "" : dd.colorName;
            })

        // binding indicator circles
        let bindG = this.canvas.append("g").attr("class", "bindG").attr("transform", d3.translate(0, $("#userPreferenceSvg").height() * 4 / 5));
        bindG.selectAll("circle").data(paletteData)
            .join(enter => enter.append("circle").attr("class", "bindCircle"))
            .attr("cx", (d, i) => i * legendGrid + legendGrid / 2)
            .attr("cy", 0)
            .attr("r", 8)
            .style("stroke", d => { d.strokeColor = d.strokeColor == undefined ? d3.rgb(subColor[0], subColor[1], subColor[2]) : d.strokeColor; return d.strokeColor })
            .style("stroke-width", 8).style("fill", "none")
        return this;
    }

    drawFlatPalette() {
        var self = this;
        var tbody = this.canvas;
        let paletteData = []
        if (this.drawType == "original") {
            paletteData.push([...this.paletteData]);  // 1d to 2d
        } else if (this.drawType == "recommended" || this.drawType == "bookmark") {
            paletteData = this.paletteData;
        }
        tbody.selectAll(".itemG").remove();
        tbody
            .selectAll(".itemG")
            .data(paletteData)
            .join(enter => enter.append("g")
                .attr("class", "itemG"),
            )
            .attr("transform", (d, i) => {
                return d3.translate(
                    0,
                    i * tableviewConf.tableRowHeight_two
                );
            })
            .each(function (d) {
                var itemG = d3.select(this);
                let legendGrid = self.canvasWidth / d.length;
                let legendHeight = tableviewConf.legendHeight;
                let legendRect = itemG.selectAll("rect").data(d);
                legendRect.enter().append("rect")
                    .attr("x", (dd, ii) => ii * legendGrid)
                    .attr("y", 0)
                    .attr("width", legendGrid)
                    .attr("height", legendHeight)
                    .style("stroke", "#424242")
                    .style("stroke-width", "1px")
                    .merge(legendRect)
                    .style("fill", dd => {
                        if (self.drawType == "original") {
                            return self.treeSource == "svg" ? dd.color : d3.rgb(dd.color[0], dd.color[1], dd.color[2]);
                        } else if (self.drawType == "recommended" || self.drawType == "bookmark") {
                            return d3.rgb(dd[0], dd[1], dd[2]);
                        }

                    })
            })
        return this;
    }

    addInteractionOnRectNode() {
        let self = this;
        if (self.drawType == "original") {
            let rects = this.canvas.selectAll("rect");
            rects.on("mouseover", function (d) {
                store.commit(`changeHoverTreeObjID`, d.id);
                let construcedTree = store.getters.getConstructedTree;
                let curNode = helper.getTreeNodeInContructredTreeGivenId(construcedTree, d.id);
                let tooltipText = "height: " + curNode.relative_height.toFixed(3) + "</br>"
                    + "width: " + curNode.relative_width.toFixed(3) + "</br>"
                    + "area: " + curNode.relative_pixel_area.toFixed(3) + "</br>"

                self.tooltipDiv
                    .transition()
                    .duration(100)
                    .style("opacity", 0.9)
                    .style("left", (d3.event.pageX) + "px")
                    .style("top", (d3.event.pageY) + "px");
                self.tooltipDiv.html(tooltipText);
            })
                .on("mouseout", () => {
                    self.tooltipDiv.transition()
                        .duration(100)
                        .style("opacity", 1e-6);
                }).on("click", () => {
                    store.commit(`changeRemoveAllHightlightFilter`, true);
                })
        } else if (self.drawType == "recommended") {
            let itemG = this.canvas.selectAll(".itemG");
            itemG.on("click", function (d, i) {
                store.commit(`changeSelectedColorPaletteIndex`, "");
                setTimeout(() => { store.commit(`changeSelectedColorPaletteIndex`, i); }, 50)
                itemG.attr("style", tableviewConf.normalColorPalette);
                d3.select(this).attr("style", tableviewConf.selectedColorPalette);
            })
        } else if (self.drawType == "bookmark") {
            let itemG = this.canvas.selectAll(".itemG");
            itemG.on("click", function (d, i) {
                store.commit(`changeSelectedBookmarkIndex`, "");
                setTimeout(() => { store.commit(`changeSelectedBookmarkIndex`, i); }, 50)
                itemG.attr("style", tableviewConf.normalColorPalette);
                d3.select(this).attr("style", tableviewConf.selectedColorPalette);
            })

        }
    }

    addInteractionOnEditorRectNode() {
        let editorRects = this.canvas.selectAll(".editorRect");
        editorRects.on("click", function (d, i) {
            let curElementMS = store.getters.getCurElementsMultiSelected;
            let bindInfoArr = store.getters.getElementBindInfoArray;
            if (d["selected"] == undefined) { d["selected"] = true; } else { d["selected"] = !d["selected"] }
            let msstate = d3.event.shiftKey;
            let siblingOfCurEle = bindInfoArr[i] == -1 ? [i] : helper.findIndexOfBindedElementGivenAFlag(bindInfoArr, bindInfoArr[i]);
            if (msstate) {
                if (d["selected"]) {
                    curElementMS = curElementMS.concat(siblingOfCurEle);
                } else {
                    curElementMS = curElementMS.filter(x => !siblingOfCurEle.includes(x))
                }
            } else {
                if (d["selected"]) {
                    curElementMS = siblingOfCurEle;
                } else {
                    curElementMS = curElementMS.filter(x => !siblingOfCurEle.includes(x))
                }
            }
            store.commit(`changeHoverTreeObjID`, d.id);
            store.commit(`changeCurElementsMultiSelected`, curElementMS);
        })
    }
}