/*global _ d3 $*/
import { fabric } from "fabric";
import store from "../../service/store.js";
import helper from "./helper.js";
import fabricImageFilter from "./fabricImageFilter.js";
import { canvasConf } from "../../service/config.js";
import { contextMenuInCanvas } from "../../service/variables.js";
import dataService from "../../service/dataService.js";
import { Loading } from "element-ui";
export default {
    data() {
        return {
            canvas: new fabric.Canvas(),
            objID: 1,
            constructedTree: {},
            contextMenu: contextMenuInCanvas,
            pixelArrayOfNodeInImage: {}
        };
    },
    computed: {
        /***
         * create new object (svg, img, text)
         ***/

        newSvgToCreated() {
            return store.getters.getNewSvgToCreated;
        },
        newImgToCreated() {
            return store.getters.getNewImgToCreated;
        },
        newTextToCreated() {
            return store.getters.getNewTextToCreated;
        },

        /***
         * tree construction
         */
        RequestTreeConstruction() {
            return store.getters.getRequestTreeConstruction;
        },

        /***
         * user color preference input
         ***/

        userSpecificColor() {
            return store.getters.getUserSpecificColor;
        },

        /***
         * interaction between tree and paintingView
         ***/
        // for svg template
        hoverTreeObjID() {
            return store.getters.getHoverTreeObjID;
        },

        RemoveAllHightlightFilter() {
            return store.getters.getRemoveAllHightlightFilter;
        },

        /***
         * recolor, after getting imputation result
         ***/
        selectedRecommendedColorPaletteIndex() {
            return store.getters.getSelectedColorPaletteIndex;
        },
        selectedBookmarkIndex() {
            return store.getters.getSelectedBookmarkIndex;
        },

        //save recolored img
        SaveRecoloredInfogState() {
            return store.getters.getSaveRecoloredInfogState;
        }
    },

    mounted() {
        const ref = this.$refs.paintingCanvas;
        this.canvas.initialize(ref, canvasConf);
        window.addEventListener("resize", resizeCanvas(this.canvas), false);
        function resizeCanvas(canvas) {
            canvas.setDimensions({
                width: $("#paintingDiv").width(),
                height: $("#paintingDiv").height()
            });
            canvas.renderAll();
        }
        // resize on init
        resizeCanvas(this.canvas);
    },

    methods: {
        /***
         * create new object (svg, img, text)
         ***/

        createANewObject(type, newObj = null) {
            newObj.id = this.objID;
            this.objID = this.objID + 1;
            this.canvas.add(newObj);
            this.canvas.setActiveObject(newObj);
        },

        listenCanvas() {
            this.canvas.on({
                "mouse:down": e => console.log("canvas:mouse:down", e),
                "mouse:up": e => console.log("canvas:mouse:up", e)
            });
        },

        createANewSvg(url) {
            let group = [];
            let containOnlyOneObject = false;
            fabric.loadSVGFromURL(
                url,
                (objects, options) => {
                    console.log(options);
                    if (objects.length == 1) {
                        containOnlyOneObject = true;
                    }
                    var loadedObjects = new fabric.Group(group);
                    this.canvas.add(loadedObjects);
                    this.canvas.setActiveObject(loadedObjects);
                    this.canvas.renderAll();
                },
                (item, object) => {
                    object.set("id", this.objID);
                    // object.category = "shape/icon";
                    this.objID = this.objID + 1;
                    group.push(object);
                }
            );
            setTimeout(() => {
                if (containOnlyOneObject) {
                    let target = this.canvas.getActiveObject();
                    target.toActiveSelection();
                    this.canvas.discardActiveObject(); // after transferring to single object, need to reselect before change colors.
                }
            }, 100);
        },

        createANewImg(urlInfo) {
            let url = urlInfo[0];
            let numInImg = urlInfo[1];
            fabric.Image.fromURL(url, img => {
                this.canvas.add(img);
                img.id = this.objID;
                this.objID = this.objID + 1;
                img.category = "img";
                img.numInImg = numInImg;
            });
        },

        createANewText() {
            var text = new fabric.IText("Please input text", {
                fontFamily: "Comic Sans"
            });
            text.id = this.objID;
            this.objID = this.objID + 1;
            text.category = "text";
            this.canvas.add(text);
        },

        /**
         * construct a tree
         */
        constructATree() {
            let targetObj = this.canvas.getActiveObject();
            if (!targetObj) {
                this.$message.error(
                    "No SVG or image selected. Please first click a SVG or image."
                );
                return;
            }
            // construct tree for grouped svg
            if (targetObj.type === "group") {
                let objsInTheGroup = targetObj.toActiveSelection();
                objsInTheGroup = objsInTheGroup._objects;
                /** calculate height, width, area **/
                // picture size
                let pictureWidth = 300,
                    pictureHeight = 300;
                for (let i = 0; i < objsInTheGroup.length; i++) {
                    let curObj = objsInTheGroup[i];
                    let fill = curObj.get("fill");
                    if (fill === "#FFFFFF") {
                        curObj.set("fill", "#00FFFF");
                    }
                    let dataUrlForCurObj = curObj.toDataURL({ multiplier: 1 });
                    if (fill === "#FFFFFF") {
                        curObj.set("fill", "#FFFFFF");
                    }
                    helper.calculateRelativePixelArea(
                        dataUrlForCurObj,
                        pictureWidth,
                        pictureHeight,
                        curObj
                    );
                }
                setTimeout(() => {
                    this.constructedTree = helper.getPureTreeStructureFromSvg(
                        objsInTheGroup,
                        pictureHeight,
                        pictureWidth
                    );

                    let constructedTreeFromSvg = helper.getTreeInD3Format(
                        this.constructedTree
                    );
                    constructedTreeFromSvg = helper.getTreeWithLightRightNumber(
                        constructedTreeFromSvg
                    );
                    store.commit(`changeConstructedTree`, constructedTreeFromSvg);
                    store.commit(`changeTreeSource`, "svg");
                }, 100);

                // add click event listener to each object for selecting it and its binded siblings
                let allObjects = this.canvas.getObjects();
                for (let i = 0; i < allObjects.length; i++) {
                    let curObj = allObjects[i];
                    curObj.on('mousedown', function (e) {
                        let curObjId = e.target.id;
                        let objIDArray = store.getters.getObjIdArrayInSameOrderWithPalettesInPaletteView;
                        let index = objIDArray.indexOf(curObjId);
                        let bindInfoArr = store.getters.getElementBindInfoArray;
                        let curElementMS = bindInfoArr[index] == -1 ? [index] : helper.findIndexOfBindedElementGivenAFlag(bindInfoArr, bindInfoArr[index]);
                        store.commit(`changeCurElementsMultiSelected`, curElementMS);
                    })
                }
            }
            // construct tree from an img
            else if (targetObj.category === "img") {
                let loadingInstance = Loading.service({
                    target: document.querySelector("#userPreferenceDiv")
                });
                let numInImg = targetObj.numInImg;
                dataService.getFeaturesAndTreeStructure(numInImg, response => {
                    loadingInstance.close();
                    let tree = response.data.constructed_tree;
                    this.pixelArrayOfNodeInImage = response.data.pixel_array_of_node;
                    store.commit(`changeConstructedTree`, tree[0]);
                    store.commit(`changeTreeSource`, "img");
                });
            }
            // if not svg group or img, return
            else {
                this.$message.error(
                    "The selected object is not a group of SVG elements or an image. Please first group the SVG elements or choose an image."
                );
                return;
            }
        },
        /***
         * interaction between tree and paintingView
         ***/
        highlightHoverTreeObj(objID) {
            let treeSource = store.getters.getTreeSource;
            if (treeSource == "svg") {
                _.forEach(this.canvas.getObjects(), obj => {
                    obj.set({
                        stroke: null,
                        strokeWidth: 3
                    });
                });
                let targetObj = _.find(this.canvas.getObjects(), o => {
                    return o.id === objID;
                });
                targetObj.set({
                    stroke: "red",
                    strokeWidth: 3,
                    dirty: true
                });
                this.canvas.requestRenderAll();
            } else {
                let pixelArr = this.pixelArrayOfNodeInImage["" + objID];
                // apply filter to the object
                let imgObj = _.find(this.canvas.getObjects(), o => {
                    return o.category === "img";
                });

                var canvas2dBackend = new fabric.Canvas2dFilterBackend();
                fabric.filterBackend = canvas2dBackend;
                _.remove(imgObj.filters, f => {
                    // remove other Highlight filters
                    return f.type === "Highlight";
                });
                imgObj.filters.push(fabricImageFilter.getNewHightFilter(pixelArr));
                imgObj.applyFilters();
                this.canvas.requestRenderAll();
            }
        },
        removeRemoveAllHightlightFilter() {
            let treeSource = store.getters.getTreeSource;
            if (treeSource == "svg") {
                _.forEach(this.canvas.getObjects(), obj => {
                    obj.set({
                        stroke: null,
                        strokeWidth: 3
                    });
                });
                this.canvas.requestRenderAll();
            } else {
                // apply filter to the object
                let imgObj = _.find(this.canvas.getObjects(), o => {
                    return o.category === "img";
                });

                var canvas2dBackend = new fabric.Canvas2dFilterBackend();
                fabric.filterBackend = canvas2dBackend;
                _.remove(imgObj.filters, f => {
                    // remove other Highlight filters
                    return f.type === "Highlight";
                });
                imgObj.applyFilters();
                this.canvas.requestRenderAll();
            }
        },

        /***
         * user preference
         ***/
        setUserPreference(mode, value) {
            let treeSource = store.getters.getTreeSource;
            if (mode == "specificColor") {
                if (value == "") {
                    return;
                }
                let curElementMS = store.getters.getCurElementsMultiSelected;
                let objIDArraySameWithPalette =
                    store.getters.getObjIdArrayInSameOrderWithPalettesInPaletteView;
                let originalColors = store.getters.getOriginalColorsInPaletteView;
                if (treeSource == "svg") {
                    for (let i = 0; i < curElementMS.length; i++) {
                        let id = objIDArraySameWithPalette[curElementMS[i]];
                        let targetObj = _.find(this.canvas.getObjects(), o => {
                            return o.id === id;
                        });
                        if (targetObj == undefined) {
                            continue;
                        }
                        let color = value;
                        if (value == undefined) {
                            color = originalColors[curElementMS[i]].color;
                        }
                        targetObj.set("fill", color);
                    }
                    this.canvas.renderAll();
                } else if (treeSource == "img") {
                    let imgObj = _.find(this.canvas.getObjects(), o => {
                        return o.category === "img";
                    });

                    var canvas2dBackend = new fabric.Canvas2dFilterBackend();
                    fabric.filterBackend = canvas2dBackend;
                    // remove all Highlight filters
                    _.remove(imgObj.filters, f => {
                        return f.type === "Highlight";
                    });
                    for (let i = 0; i < curElementMS.length; i++) {
                        let id = objIDArraySameWithPalette[curElementMS[i]];
                        if (value == undefined) {
                            _.remove(imgObj.filters, f => {
                                return f.id === id;
                            });
                        } else {
                            let rgb_color = d3.cvtColorXXX2Rgb(value);
                            let pixelArr = this.pixelArrayOfNodeInImage["" + id];
                            imgObj.filters.push(
                                fabricImageFilter.getNewRecoloredFilter(pixelArr, rgb_color, id)
                            );
                        }
                    }
                    imgObj.applyFilters();
                    this.canvas.requestRenderAll();
                }
                setTimeout(() => {
                    store.commit(`changeUserSpecificColor`, "");
                }, 100);
            }
        },

        /***
         * recolor, after getting imputation result
         ***/
        recoloring(selectedIndex, ty) {
            let treeSource = store.getters.getTreeSource;
            let res, selectedPalette;
            if (ty == "recommend") {
                res = store.getters.getRgbImputationResultsAndNodeIds;
                selectedPalette = res["rgb_imputation_results"][selectedIndex];
            } else if (ty == "bookmark") {
                res = store.getters.getBookmarkPalettesInPaletteView;
                selectedPalette = res[selectedIndex];
            } else {
                return;
            }

            let correspondingObjId =
                store.getters.getObjIdArrayInSameOrderWithPalettesInPaletteView;
            if (treeSource == "svg") {
                for (let i = 0; i < correspondingObjId.length; i++) {
                    let id = correspondingObjId[i];
                    if (id == 0) { // 0 is not correspending to an object
                        continue;
                    }
                    let targetObj = _.find(this.canvas.getObjects(), o => {
                        return o.id === id;
                    });
                    let rgbColor = selectedPalette[i];
                    targetObj.set(
                        "fill",
                        d3
                            .color(
                                "rgb(" +
                                rgbColor[0] +
                                "," +
                                rgbColor[1] +
                                "," +
                                rgbColor[2] +
                                ")"
                            )
                            .formatHex()
                    );
                }
                this.canvas.requestRenderAll();
            } else if (treeSource == "img") {
                let imgObj = _.find(this.canvas.getObjects(), o => {
                    return o.category === "img";
                });
                let canvas2dBackend = new fabric.Canvas2dFilterBackend();
                fabric.filterBackend = canvas2dBackend;
                imgObj.filters = [];
                for (let i = 0; i < correspondingObjId.length; i++) {
                    let id = correspondingObjId[i];
                    let pixelArr = this.pixelArrayOfNodeInImage["" + id];
                    let rgbColor = selectedPalette[i];
                    imgObj.filters.push(
                        fabricImageFilter.getNewRecoloredFilter(pixelArr, rgbColor, id)
                    );
                }
                imgObj.applyFilters();
                this.canvas.requestRenderAll();
            }
        },

        // save infographics to png
        saveInfoToPng() {
            let treeSource = store.getters.getTreeSource;
            if (treeSource == "svg") {
                _.forEach(this.canvas.getObjects(), obj => {
                    obj.set({
                        stroke: null,
                        strokeWidth: 3
                    });
                });
            }
            let bb = this.canvas.getObjects()[0].getBoundingRect();
            var dataURL = this.canvas.toDataURL({
                format: "png",
                left: bb["left"],
                top: bb["top"],
                width: bb["width"],
                height: bb["height"]
            });
            let figureInSaveImgName = Math.floor(Math.random() * 1000 + 1);
            var a = document.createElement("a");
            a.href = dataURL;
            a.setAttribute("download", figureInSaveImgName + ".png");
            a.click();
        },

        contextMenuHandler(indexList) {
            let operation;
            let len = indexList.length;
            if (len == 1) {
                operation = contextMenuInCanvas[indexList[0]]["text"];
            } else {
                operation =
                    contextMenuInCanvas[indexList[0]]["children"][indexList[1]]["text"];
            }
            let targetObj = this.canvas.getActiveObject();
            if (operation == "Bring Forward") {
                this.canvas.bringForward(targetObj, true);
            } else if (operation == "Bring Backward") {
                this.canvas.sendBackwards(targetObj, true);
            } else if (operation == "Sent to Front") {
                this.canvas.bringToFront(targetObj);
            } else if (operation == "Sent to Back") {
                this.canvas.sendToBack(targetObj);
            } else if (operation == "Group") {
                if (!targetObj | (targetObj.type !== "activeSelection")) {
                    return;
                }
                let group = targetObj.toGroup();
                group.id = this.objID;
                group.category = "group";
                this.objID = this.objID + 1;

            } else if (operation == "Ungroup") {
                if (!targetObj | (targetObj.type !== "group")) {
                    return;
                }
                targetObj.toActiveSelection();
                // this.canvas.requestRenderAll();
            } else if (operation == "Duplicate") {
                targetObj.clone(clonedObj => {
                    this.createANewObject(
                        "clone",
                        clonedObj.set({
                            left: targetObj.left + 10,
                            top: targetObj.top + 10
                        })
                    );
                });
            } else if (operation == "Delete") {
                this.canvas.remove(targetObj);
            }
        }
    },

    watch: {
        /***
         * create new object (svg, img, text)
         ***/

        newSvgToCreated(url) {
            if (url != "") {
                this.createANewSvg(url);
                store.commit(`changeNewSvgToCreated`, "");
            }
        },
        newImgToCreated(urlInfo) {
            if (urlInfo != "") {
                this.createANewImg(urlInfo);
                // store.commit(`changeNewImgToCreated`, "");
            }
        },
        newTextToCreated(par) {
            if (par) {
                this.createANewText();
                store.commit(`changeNewTextToCreated`, false);
            }
        },
        /**Construct a tree */
        RequestTreeConstruction(val) {
            if (val) {
                this.constructATree();
                store.commit(`changeRequestTreeConstruction`, false);
            }
        },
        /***
         * user color preference input
         ***/
        userSpecificColor(color) {
            this.setUserPreference("specificColor", color);
        },

        /***
         * interaction between tree and paintingView
         ***/
        //for svg template
        hoverTreeObjID(objID) {
            this.highlightHoverTreeObj(objID);
        },
        RemoveAllHightlightFilter(val) {
            if (val) {
                this.removeRemoveAllHightlightFilter();
                store.commit(`changeRemoveAllHightlightFilter`, false);
            }
        },

        /***
         * recolor, after getting imputation result
         ***/
        selectedRecommendedColorPaletteIndex(selectedIndex) {
            if (selectedIndex === "") {
                return;
            }
            this.recoloring(selectedIndex, "recommend");
        },

        selectedBookmarkIndex(selectedIndex) {
            if (selectedIndex === "") {
                return;
            }
            this.recoloring(selectedIndex, "bookmark");
        },
        SaveRecoloredInfogState(state) {
            if (state) {
                this.saveInfoToPng();
                store.commit(`changeSaveRecoloredInfogState`, false);
            }
        }
    }
};