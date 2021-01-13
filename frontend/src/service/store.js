import Vue from 'vue'
import vuex from 'vuex'
import { objectConf } from "../service/config.js"
Vue.use(vuex)

export default new vuex.Store({
    state: {
        imageUrl: "",
        imageName: "",
        objectConf: objectConf,
        /** create new object */
        newSvgToCreated: "",
        newImgToCreated: "",
        newTextToCreated: false,
        /** interaction between tree and painting view*/
        // constructed tree from svg/img in painting view
        RequestTreeConstruction: false,
        treeSource: null,  // value: svg or img
        ConstructedTree: {},
        // mouseover tree node and then highlight corresponding area in painting view
        hoverTreeObjID: -1,
        RemoveAllHightlightFilter: false,

        /** paletteView */
        OriginalColorsInPaletteView: [],
        ObjIdArrayInSameOrderWithPalettesInPaletteView: [],
        /** user preference*/
        //click tree node and then modify the color of curresponding tree node and area
        toBeModifiedTreeObjID: -1, // abandoned in version of PaletteView; influenced for both svg and image; id in tree = id of fabric obj id (svg) = id of each shape/element (img)

        UserColorName: null,
        userSpecificColor: null, // in hex
        CurElementsMultiSelected: [],
        ElementBindInfoArray: [],

        /** imputation results*/
        RgbImputationResultsAndNodeIds: {}, // contains 'rgb_imputation_results', 'corresponding_ids'
        BookmarkPalettesInPaletteView: [],
        SelectedColorPaletteIndex: null,
        SelectedBookmarkIndex: null,

        /** save recolored infographics */
        SaveRecoloredInfogState: false,
    },
    mutations: {
        changeImageUrl(state, url) {
            state.imageUrl = url;
        },
        changeImageName(state, name) {
            state.imageName = name;
        },
        changeObjectConf(state, objectType, feature, value) {
            state.objectConf[objectType][feature] = value
        },

        changeNewSvgToCreated(state, url) {
            state.newSvgToCreated = url;
        },
        changeNewImgToCreated(state, url) {
            state.newImgToCreated = url;
        },
        changeNewTextToCreated(state, par) {
            state.newTextToCreated = par
        },

        changeHoverTreeObjID(state, objID) {
            state.hoverTreeObjID = objID
        },

        changeRemoveAllHightlightFilter(state, val) {
            state.RemoveAllHightlightFilter = val;
        },


        changeRequestTreeConstruction(state, val) {
            state.RequestTreeConstruction = val;
        },

        changeTreeSource(state, source) {
            state.treeSource = source
        },
        changeConstructedTree(state, tree) {
            state.ConstructedTree = tree;
        },

        changeOriginalColorsInPaletteView(state, val) {
            state.OriginalColorsInPaletteView = val;
        },
        changeObjIdArrayInSameOrderWithPalettesInPaletteView(state, val) {
            state.ObjIdArrayInSameOrderWithPalettesInPaletteView = val;
        },

        changeToBeModifiedTreeObjID(state, id) {
            state.toBeModifiedTreeObjID = id;
        },

        changeUserSpecificColor(state, color) {
            state.userSpecificColor = color
        },

        changeUserColorName(state, val) {
            state.UserColorName = val;
        },

        changeCurElementsMultiSelected(state, val) {
            state.CurElementsMultiSelected = val;
        },
        changeElementBindInfoArray(state, val) {
            state.ElementBindInfoArray = val;
        },

        changeRgbImputationResultsAndNodeIds(state, obj) {
            state.RgbImputationResultsAndNodeIds = obj;
        },
        changeBookmarkPalettesInPaletteView(state, val) {
            state.BookmarkPalettesInPaletteView = val;
        },
        changeSelectedColorPaletteIndex(state, ind) {
            state.SelectedColorPaletteIndex = ind;
        },

        changeSelectedBookmarkIndex(state, ind) {
            state.SelectedBookmarkIndex = ind;
        },
        changeSaveRecoloredInfogState(state, val) {
            state.SaveRecoloredInfogState = val;
        }

    },
    getters: {
        getImageUrl: state => state.imageUrl,
        getImageName: state => state.imageName,
        getObjectConf: state => state.objectConf,

        getNewSvgToCreated: state => state.newSvgToCreated,
        getNewImgToCreated: state => state.newImgToCreated,
        getNewTextToCreated: state => state.newTextToCreated,

        getHoverTreeObjID: state => state.hoverTreeObjID,
        getRemoveAllHightlightFilter: state => state.RemoveAllHightlightFilter,
        getRequestTreeConstruction: state => state.RequestTreeConstruction,
        getTreeSource: state => state.treeSource,
        getConstructedTree: state => state.ConstructedTree,

        getOriginalColorsInPaletteView: state => state.OriginalColorsInPaletteView,
        getObjIdArrayInSameOrderWithPalettesInPaletteView: state => state.ObjIdArrayInSameOrderWithPalettesInPaletteView,
        getToBeModifiedTreeObjID: state => state.toBeModifiedTreeObjID,
        getUserColorName: state => state.UserColorName,
        getUserSpecificColor: state => state.userSpecificColor,
        getCurElementsMultiSelected: state => state.CurElementsMultiSelected,
        getElementBindInfoArray: state => state.ElementBindInfoArray,

        getRgbImputationResultsAndNodeIds: state => state.RgbImputationResultsAndNodeIds,
        getBookmarkPalettesInPaletteView: state => state.BookmarkPalettesInPaletteView,
        getSelectedColorPaletteIndex: state => state.SelectedColorPaletteIndex,
        getSelectedBookmarkIndex: state => state.SelectedBookmarkIndex,

        getSaveRecoloredInfogState: state => state.SaveRecoloredInfogState
    }
});
