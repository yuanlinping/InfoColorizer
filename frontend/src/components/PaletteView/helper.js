/*global d3*/
export default {
    getOriginalColorsAndDepthFromTreeInD3HierarchyFormat(tree, source) {
        let root = d3.hierarchy(tree);
        let originalColors = []
        root.eachBefore(d => {
            originalColors.push({
                id: d.data.id,
                depth: d.depth,
                color: (source == "img" ? d.data.rgb_color : d.data.color)
            })
        })
        return originalColors
    },
    initializeElementBindInfoArray(len) {
        let arr = [];
        for (let i = 0; i < len; i++) { arr.push(-1); }
        return arr
    },
    getObjIdArrayInSameOrderWithPalettes(originalColors) {
        let arr = [];
        for (let i = 0; i < originalColors.length; i++) {
            arr.push(originalColors[i].id)
        }
        return arr;
    },

    getInitialUserPreferencesFromOriginalColors(originalColors) {
        let userPreferences = [];
        for (let i = 0; i < originalColors.length; i++) {
            let value = originalColors[i];
            userPreferences.push({
                id: value.id,
                depth: value.depth,
                specificColor: undefined,
                colorName: undefined,
            })
        }
        return userPreferences;
    },

    getTreeNodeInContructredTreeGivenId(tree, id) {
        let root = d3.hierarchy(tree);
        let target;
        root.each(d => {
            if (d.data.id == id) {
                target = d.data;
            }
        })
        return target;
    },

    findIndexOfBindedElementGivenAFlag(bindInfoArr, flag) {
        return bindInfoArr.reduce((arr, ele, ind) => {
            if (ele == flag) { arr.push(ind); }
            return arr;
        }, [])
    },
}