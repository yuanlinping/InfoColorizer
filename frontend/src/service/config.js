export const canvasConf = {
    fireRightClick: true,
}

export const objectConf = {
    "Circle": {
        left: Math.floor(Math.random() * canvasConf.width / 2),
        top: Math.floor(Math.random() * canvasConf.height / 2),
        radius: 20,
        stroke: "black",
        fill: "white"
    },
    "Ellipse": {
        left: Math.floor(Math.random() * canvasConf.width / 2),
        top: Math.floor(Math.random() * canvasConf.height / 2),
        rx: 30,
        ry: 20,
        stroke: "black",
        fill: "white"
    },
    "line": {
        x1: 20,
        y1: 20,
        x2: 20,
        y2: 100,
        width: 2,
        stroke: "black",
        fill: "white"
    },
    "Rect": {
        left: Math.floor(Math.random() * canvasConf.width / 2),
        top: Math.floor(Math.random() * canvasConf.height / 2),
        width: 50,
        height: 50,
        stroke: "black",
        fill: "white",
        angle: 0
    },
    "Triangle": {
        left: Math.floor(Math.random() * canvasConf.width / 2),
        top: Math.floor(Math.random() * canvasConf.height / 2),
        width: 50,
        height: 50,
        stroke: "black",
        fill: "white",
        angle: 0
    }
}

export const TreeViewConf = {
    padding_left: 35,
    padding: 15,
    padding_bottom: 25
}

export const tableviewConf = {
    padding: 5,
    tableRowHeight_two: 45,
    legendHeight: 25,
    normalColorPalette: "outline:none",
    selectedColorPalette: "outline:3px solid orange",
    columnGap: 5
};
