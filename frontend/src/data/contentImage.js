let nums = [1, 101, 129, 135, 19, 2286, 2411, 258, 3032, 3046, 3134, 3135, 3142, 3143, 3227, 3233, 3257, 337, 3464, 3465, 3466, 3475, 3495, 442, 459, 478, 521, 525, 621, 65, 693, 70, 703, 71, 718, 72, 735, 757, 767, 776, 777, 817, 82, 86]

let svgData = [];
for (let i = 0; i < nums.length; i++) {
    svgData.push({
        icon: require('../assets/img/' + nums[i] + ".jpg"), numInImg: nums[i]
    })
}
export default svgData;