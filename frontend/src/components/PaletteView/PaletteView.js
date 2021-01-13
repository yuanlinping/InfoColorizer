import dataService from '../../service/dataService.js'
import store from "../../service/store.js"
import helper from "./helper.js"
import DrawPalette from "./drawPalette.js"
import { SPECIFICCOLORSUBTITUTION, BINDINGCOLORS } from "../../service/variables.js"
import { Loading } from "element-ui";
import { tableviewConf } from '../../service/config.js'
/*global _ $ d3 */
export default {
    name: "PaletteView",
    data() {
        return {
            constructedTree: {}, // in format suitable for d3.hierarchy
            originalColors: [], // {"id":xx,"specificColor":xxx}; ordered in pre-order dfs 
            currentUserPreference: [], // {"id":xx, "specificColor":xxx,"colorName":xxx, "colorSematic":"", "colorAffection":""}; ordered in pre-order dfs
            /**imputation results*/
            curRgbImputationResults: [],
            /** bookmark recommendation */
            bookmarkedPalettes: [],
            // binded elements info
            multiSelectState: false,
            curElementsMultiSelected: [],  // the element is the index of selected elements in original Colors
            strokeColorIndex: 0,

            /** history */
            historyUserPrefence: [],
            historyBindInfoArray: [],
            historyRgbImputationResults: [],
            historySelectedPaletteIndex: [],
            currentHistoryIndex: -1, // used for getting a desired history from historyUserPreference,

        }
    },
    computed: {
        ConstructedTree() {
            return store.getters.getConstructedTree;
        },

        CurElementsMultiSelected() {
            return store.getters.getCurElementsMultiSelected;
        },

        userSpecificColor() {
            return store.getters.getUserSpecificColor;
        },
        userColorName() {
            return store.getters.getUserColorName;
        },

        selectedBookmarkIndex() {
            return store.getters.getSelectedBookmarkIndex;
        },

        rgbImputationResultsAndNodeIds() {
            return store.getters.getRgbImputationResultsAndNodeIds;
        },
        selectedRecommendedColorPaletteIndex() {
            return store.getters.getSelectedColorPaletteIndex;
        },
    },
    methods: {
        /** initialize */
        initialDrawInstance() {
            /** for user preference editor */
            let pad = tableviewConf.padding;
            let editorCanvas = d3.select("#userPreferenceSvg").append("g").attr("transform", d3.translate(pad, pad * 3));
            let editorWidth = $("#userPreferenceSvg").width() - 2 * pad;
            let editorHeight = $("#userPreferenceSvg").height() - 4 * pad;
            this.drawPaletteEditor = new DrawPalette(editorCanvas).width(editorWidth).height(editorHeight).setDrawType("editor").initDraw();
            /** for original palette */
            let originalCanvas = d3.select("#originalSvg").append("g").attr("transform", d3.translate(pad, pad));
            let originalWidth = $("#originalSvg").width() - 2 * pad;
            let originalHeight = $("#originalSvg").height() - 2 * pad;
            this.drawPaletteOriginal = new DrawPalette(originalCanvas).width(originalWidth).height(originalHeight).setDrawType("original").initDraw();
            /** for bookmark palettes */
            let bookmarkCanvas = d3.select('#bookmarkSvg').append("g").attr("transform", d3.translate(pad, pad));
            let bookmarkWidth = $('#bookmarkSvg').width() - 2 * pad;
            let bookmarkHeight = $('#bookmarkSvg').height() - 2 * pad;
            this.drawPaletteBookmark = new DrawPalette(bookmarkCanvas).width(bookmarkWidth).height(bookmarkHeight).setDrawType("bookmark").initDraw();
            /** for recommended palettes */
            let recommendedCanvas = d3.select("#recommendSvg").append("g").attr("transform", d3.translate(pad, pad));
            let recommendedWidth = $("#recommendSvg").width() - 2 * pad;
            let recommendedHeight = $("#recommendSvg").height() - 2 * pad;
            this.drawPaletteRecommended = new DrawPalette(recommendedCanvas).width(recommendedWidth).height(recommendedHeight).setDrawType("recommended").initDraw();
        },

        requestTreeConstruction() {
            store.commit('changeRequestTreeConstruction', true);
        },

        requestRecommendationResults() {
            if (this.curRgbImputationResults.length != 0) {  // when == 0, this is the first time to get recommendation results, so don't save status
                this.startNextIterate();
            }

            let self = this;
            // insert userPreference to the constructed tree
            let constructedTree = store.getters.getConstructedTree;
            let hierarchy = d3.hierarchy(constructedTree);
            let i = 0;
            hierarchy.eachBefore(d => {   // eachBefore will traverse the node with the same order with constructing originalColors/curUserpreferences
                d.data.rgb_user_specific_color = self.currentUserPreference[i].specificColor;
                d.data.color_name = self.currentUserPreference[i].colorName;
                i = i + 1;
            })

            let treeSource = store.getters.getTreeSource;
            let cur_tree = { 0: constructedTree };
            let bindArray = store.getters.getElementBindInfoArray;
            let num_in_img;
            if (treeSource == "img") {
                num_in_img = store.getters.getNewImgToCreated;
                num_in_img = num_in_img[1];
            } else if (treeSource == "svg") {
                cur_tree = { 0: store.getters.getConstructedTree };
                num_in_img = 0;
            }
            let loadingInstance = Loading.service({
                target: document.querySelector("#recommendDiv")
            })
            dataService.getImputationResults(
                treeSource,
                num_in_img,
                cur_tree,
                bindArray,
                response => {
                    loadingInstance.close();
                    console.log(response.data);
                    store.commit(`changeRgbImputationResultsAndNodeIds`, response.data);
                }
            );
        },



        bindMultiSelectedElements() {
            let elementBindInfoArray = store.getters.getElementBindInfoArray;
            let flag = d3.max(elementBindInfoArray) + 1;
            if (this.curElementsMultiSelected.length <= 1) {
                this.$message.error(
                    "No element or only one element is chosen. Please choose at least two elements."
                );
            } else {
                for (let i = 0; i < this.curElementsMultiSelected.length; i++) {
                    elementBindInfoArray[this.curElementsMultiSelected[i]] = flag;
                }
                let strokeC = d3.cvtColorXXX2Rgb(BINDINGCOLORS[this.strokeColorIndex]);
                d3.selectAll(".bindCircle").style("stroke", (d, i) => {
                    if (this.curElementsMultiSelected.includes(i)) {
                        d.strokeColor = d3.rgb(strokeC[0], strokeC[1], strokeC[2]);
                    }
                    return d.strokeColor
                })
                this.strokeColorIndex = this.strokeColorIndex + 1;
                store.commit(`changeElementBindInfoArray`, elementBindInfoArray);
            }
        },

        unbindMultiSelectedElements() {
            let elementBindInfoArray = store.getters.getElementBindInfoArray;
            if (this.curElementsMultiSelected.length <= 1) {
                this.$message.error(
                    "No element or only one element is chosen. Please choose at least two elements."
                );
            } else {
                for (let i = 0; i < this.curElementsMultiSelected.length; i++) {
                    elementBindInfoArray[this.curElementsMultiSelected[i]] = -1
                    let subColor = SPECIFICCOLORSUBTITUTION;
                    d3.selectAll(".bindCircle").style("stroke", (d, i) => {
                        if (this.curElementsMultiSelected.includes(i)) {
                            d.strokeColor = d3.rgb(subColor[0], subColor[1], subColor[2]);
                        }
                        return d.strokeColor
                    })
                }
                store.commit(`changeElementBindInfoArray`, elementBindInfoArray);
            }
        },

        keepColorsWithOriginal() {
            for (let i = 0; i < this.curElementsMultiSelected.length; i++) {
                let oricolor = this.originalColors[this.curElementsMultiSelected[i]].color;
                this.currentUserPreference[this.curElementsMultiSelected[i]].specificColor = (oricolor.length == 3 ? oricolor : d3.cvtColorXXX2Rgb(oricolor))
            }
            this.drawPaletteEditor.setPaletteData(this.currentUserPreference).drawNestedPalette().addInteractionOnEditorRectNode();
        },

        clearUserPreference() {  // clear specific color; semantic etc. not clean the binding
            for (let i = 0; i < this.curElementsMultiSelected.length; i++) {
                this.currentUserPreference[this.curElementsMultiSelected[i]].specificColor = undefined;
                this.currentUserPreference[this.curElementsMultiSelected[i]].colorName = undefined;
            }
            store.commit(`changeUserSpecificColor`, undefined)
            store.commit(`changeUserColorName`, undefined)
        },

        resetAllPreference() {
            this.curElementsMultiSelected = [];
            for (let i = 0; i < this.originalColors.length; i++) {
                this.curElementsMultiSelected.push(i);
            }
            store.commit(`changeCurElementsMultiSelected`, this.curElementsMultiSelected);
            this.clearUserPreference();
        },

        bookmarkARecommendation() {
            let selectedColorPaletteIndex = store.getters.getSelectedColorPaletteIndex;
            this.bookmarkedPalettes.push(this.curRgbImputationResults[selectedColorPaletteIndex]);
            this.drawPaletteBookmark.setPaletteData(this.bookmarkedPalettes).drawFlatPalette().addInteractionOnRectNode();
            store.commit(`changeBookmarkPalettesInPaletteView`, this.bookmarkedPalettes);
        },
        startNextIterate() {
            /**update this.userPreference according to the selected recommendation results; */
            // specific colors are add to this.userPreference; while remaining the vague preference; Backend should consider specific color first, then vague preference
            // the logic with other parts is that: select a recommendation -> user can change the preferences; 
            // but here, we just store the recommendation as their preference; to ensure when recovering history, the template and the svg are the same regarding colors
            let selectedColorPaletteIndex = store.getters.getSelectedColorPaletteIndex;
            let selectedColorPalette = this.curRgbImputationResults[selectedColorPaletteIndex];
            let selectedUserPreference = _.cloneDeep(this.currentUserPreference);
            for (let i = 0; i < selectedUserPreference.length; i++) {
                selectedUserPreference.specificColor = selectedColorPalette[i]
            }
            // store cur iteration results
            let curBindInfoArray = store.getters.getElementBindInfoArray;
            this.historyUserPrefence.push(selectedUserPreference);
            this.historyBindInfoArray.push(_.cloneDeep(curBindInfoArray));
            this.historyRgbImputationResults.push(_.cloneDeep(this.curRgbImputationResults));
            this.historySelectedPaletteIndex.push(selectedColorPaletteIndex);
            this.currentHistoryIndex = this.historyBindInfoArray.length - 1;
        },

        goToPreviousOrNextIteration(step) { // step: -1 or 1
            if (step == -1) { // previous
                if (this.currentHistoryIndex == 0 || this.currentHistoryIndex == -1) { this.$message.error("This is the first one."); return; }
            } else {
                if (this.currentHistoryIndex == this.historyUserPrefence.length - 1) { this.$message.error("This is the last one."); return; }
            }
            //get corresponding info
            this.currentHistoryIndex = this.currentHistoryIndex + step;
            this.currentUserPreference = this.historyUserPrefence[this.currentHistoryIndex];
            let curBindInfoArray = this.historyBindInfoArray[this.currentHistoryIndex];
            this.curRgbImputationResults = this.historyRgbImputationResults[this.currentHistoryIndex];
            store.commit(`changeElementBindInfoArray`, curBindInfoArray);
            let temp = store.getters.getRgbImputationResultsAndNodeIds;
            temp['rgb_imputation_results'] = this.curRgbImputationResults;
            store.commit(`changeRgbImputationResultsAndNodeIds`, temp);
            // update ui; here has a bug:
            let paletteindex = this.historySelectedPaletteIndex[this.currentHistoryIndex];
            store.commit(`changeSelectedColorPaletteIndex`, "");
            setTimeout(() => { store.commit(`changeSelectedColorPaletteIndex`, paletteindex); }, 50)
            this.drawPaletteEditor.setPaletteData(this.currentUserPreference).drawNestedPalette().addInteractionOnEditorRectNode();
            this.drawPaletteRecommended.setPaletteData(this.curRgbImputationResults).drawFlatPalette().addInteractionOnRectNode();
        },

        /** methods */
        initializePaletteViewWhenANewTreeContructed(constructedTree, source) {
            this.constructedTree = constructedTree;
            this.originalColors = helper.getOriginalColorsAndDepthFromTreeInD3HierarchyFormat(this.constructedTree, source);
            store.commit(`changeOriginalColorsInPaletteView`, this.originalColors)
            this.currentUserPreference = helper.getInitialUserPreferencesFromOriginalColors(this.originalColors);
            let elementBindInfoArray = helper.initializeElementBindInfoArray(this.originalColors.length); // an array full of -1
            store.commit(`changeElementBindInfoArray`, elementBindInfoArray);
            let objIDArray = helper.getObjIdArrayInSameOrderWithPalettes(this.originalColors);
            store.commit(`changeObjIdArrayInSameOrderWithPalettesInPaletteView`, objIDArray);
            this.drawPaletteEditor.setPaletteData(this.currentUserPreference).setTreeSource(source).drawNestedPalette().addInteractionOnEditorRectNode();
            this.drawPaletteOriginal.setPaletteData(this.originalColors).setTreeSource(source).drawFlatPalette().addInteractionOnRectNode();
            this.drawPaletteRecommended.setTreeSource(source);
        },

        /** editor update */
        hightlightSelectedRects() {
            let self = this;
            let editorRects = d3.select("#userPreferenceSvg").selectAll(".editorRect");
            editorRects.each(function (d, i) {
                if (self.curElementsMultiSelected.includes(i)) { d3.select(this).attr("class", "editorRect hightlightedEditorRect"); }
                else { d3.select(this).attr("class", "editorRect"); }
            })
        },

        updateTreeNodeColor(hex) {
            if (hex == "") {
                return;
            }
            let curElementMS = store.getters.getCurElementsMultiSelected;
            d3.selectAll(".editorRect").style("fill", (d, i) => {
                let sub = SPECIFICCOLORSUBTITUTION;
                if (curElementMS.includes(i)) {
                    if (hex == undefined) { // hex = undefined when clear user preference on elements; set d.specific = undefined has done in clearUserPreference()
                        return d3.rgb(sub[0], sub[1], sub[2])
                    } else {
                        d.specificColor = d3.cvtColorXXX2Rgb(hex);
                        return hex;
                    }

                } else {
                    return d.specificColor === undefined ? d3.rgb(sub[0], sub[1], sub[2]) : d.specificColor;
                }
            })
            d3.selectAll(".editorLine").style("visibility", (d) => {
                return d.specificColor === undefined ? "visible" : "hidden"
            })
        },

        updateTreeNodeColorName(name) {
            let curElementMS = store.getters.getCurElementsMultiSelected;
            d3.selectAll(".editorText").text((d, i) => {
                if (curElementMS.includes(i)) {
                    d.colorName = name;
                }
                return d.colorName == undefined ? "" : d.colorName;
            })
        },

        updateEditorPaletteAfterSelectingARecommendation(selectedColorPaletteIndex, type) {
            let selectedColorPalette;
            if (type == "recommend") {
                selectedColorPalette = this.curRgbImputationResults[selectedColorPaletteIndex];
            } else if (type == "bookmark") {
                selectedColorPalette = this.bookmarkedPalettes[selectedColorPaletteIndex];
            } else { return; }

            for (let i = 0; i < this.currentUserPreference.length; i++) {
                this.currentUserPreference[i].specificColor = selectedColorPalette[i]
            }
            // update the template
            this.drawPaletteEditor.setPaletteData(this.currentUserPreference).drawNestedPalette().addInteractionOnEditorRectNode();
        }
    },

    mounted: function () {
        this.initialDrawInstance();
    },

    watch: {
        ConstructedTree(tree) {
            let source = store.getters.getTreeSource;
            this.initializePaletteViewWhenANewTreeContructed(tree, source);
        },
        CurElementsMultiSelected(curElementMS) {
            this.curElementsMultiSelected = curElementMS;
            this.hightlightSelectedRects();
        },
        userSpecificColor(hex) {
            this.updateTreeNodeColor(hex);
        },
        userColorName(name) {
            if (name != "") {
                this.updateTreeNodeColorName(name);
                store.commit(`changeUserColorName`, "");
            }
        },
        rgbImputationResultsAndNodeIds(obj) {
            this.curRgbImputationResults = obj['rgb_imputation_results'];
            this.drawPaletteRecommended.setPaletteData(this.curRgbImputationResults).drawFlatPalette().addInteractionOnRectNode();
        },
        selectedRecommendedColorPaletteIndex(index) {
            if (index === "") { return; }
            this.updateEditorPaletteAfterSelectingARecommendation(index, "recommend");
        },
        selectedBookmarkIndex(index) {
            if (index === "") { return; }
            this.updateEditorPaletteAfterSelectingARecommendation(index, "bookmark");
        }
    }
}