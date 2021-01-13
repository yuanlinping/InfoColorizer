// import { fabric } from "fabric";

/*global _ $*/
export default {
    calculateRelativePixelArea(imageUrl, width, height, fabricObj) {
        let img = new Image();
        img.src = imageUrl;
        img.onload = function () {
            let canv = $("#inputImageCanvas")[0];
            canv.width = width;
            canv.height = height;
            let ctx = canv.getContext('2d');
            ctx.drawImage(this, 0, 0)
            let imageData = ctx.getImageData(0, 0, canv.width, canv.height);
            imageData = imageData.data;
            imageData = _.chunk(imageData, 4);
            let whiteCount = _.reduce(imageData, function (count, ele) {
                let sum = _.reduce(ele, function (s, e) { return s + e }, 0)
                if (sum == 0) {
                    return count + 1;
                } else {
                    return count;
                }
            }, 0);
            ctx.clearRect(0, 0, canv.width, canv.height);

            fabricObj["relative_pixel_area"] =
                (canv.width * canv.height - whiteCount) /
                (canv.width * canv.height);
        }
    },

    getPureTreeStructureFromSvg(objsInTheGroup, totalHeight, totlaWidth) {  // equal to featureExtractionPipeline in the backend
        let constructedTree = {};
        for (let i = objsInTheGroup.length - 1; i >= 0; i--) {
            let childObj = objsInTheGroup[i];
            let bound = childObj.getBoundingRect();
            constructedTree[childObj.id] = {
                id: childObj.id,
                top: bound.top,
                left: bound.left,
                color: childObj.get("fill"),
                relative_height: childObj.get("height") / totalHeight,
                relative_width: childObj.get("width") / totlaWidth,
                relative_pixel_area: childObj.get("relative_pixel_area")
            };
            if (i == 0) {
                constructedTree[childObj.id].father_id = 0; // 0 currently is not corresponding to any fabric object
                continue;
            }
            for (let j = i - 1; j >= 0; j--) {
                let curFatherObj = objsInTheGroup[j];
                if (childObj.isContainedWithinObject(curFatherObj)) {
                    constructedTree[childObj.id].father_id = curFatherObj.id;
                    break;
                } else if (j == 0) {
                    constructedTree[childObj.id].father_id = 0;
                } else {
                    continue;
                }
            }
        }
        return constructedTree; // no key "0" in this constructedTree
    },

    getTreeInD3Format(tree) {
        let treeInD3 = _.mapValues(_.groupBy(tree, "father_id"), v => _.sortBy(v, ["left", "top"], ["asc", "asc"]));
        _.map(treeInD3, (children, key) => {
            if (treeInD3[key] != undefined) {
                dfs(children, treeInD3);
            }
        })

        let postTreeInD3 = {}
        _.map(treeInD3, (children, key) => {
            postTreeInD3.id = key;
            postTreeInD3.children = children;

        })
        postTreeInD3 = postTreeInD3.children[0];
        return postTreeInD3;

        function dfs(children, treeD3) {
            for (let i = 0; i < children.length; i++) {
                let element = children[i];
                let curId = element.id;
                let curChildren = treeD3[curId];
                if (curChildren == undefined) {
                    element["children"] = []
                } else {
                    delete treeD3[curId];
                    let res = dfs(curChildren, treeD3);
                    element["children"] = res
                }
            }
            return children;
        }
    },

    getTreeWithLightRightNumber(tree) {
        let treeWithLR = tree;
        let number = 0;

        treeWithLR["left_number"] = number;
        number = number + 1;
        let temp = treeWithLR["children"];
        leftRightNumberDFS(temp)
        treeWithLR["right_number"] = number
        return treeWithLR;



        function leftRightNumberDFS(children) {
            if (children == []) { return }
            _.forEach(children, child => {
                child["left_number"] = number
                number = number + 1
                let cur_children = child["children"]
                leftRightNumberDFS(cur_children)
                child["right_number"] = number
                number = number + 1
            });
            return
        }
    },

    findIndexOfBindedElementGivenAFlag(bindInfoArr, flag) {
        return bindInfoArr.reduce((arr, ele, ind) => {
            if (ele == flag) { arr.push(ind); }
            return arr;
        }, [])
    },
}