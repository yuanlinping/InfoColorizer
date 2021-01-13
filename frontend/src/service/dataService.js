import axios from 'axios'

const GET_REQUEST = 'GET'
const POST_REQUEST = 'POST'
const dataServerUrl = process.env.DATA_SERVER_URL || 'http://127.0.0.1:5000'

function request(url, params, type, callback) {
    let func
    if (type === GET_REQUEST) {
        func = axios.get
    } else if (type === POST_REQUEST) {
        func = axios.post
    }

    func(url, params).then((response) => {
        if (response.status === 200) {
            callback(response)
        } else {
            console.error(response) /* eslint-disable-line */
        }
    })
        .catch((error) => {
            console.error(error) /* eslint-disable-line */
        })
}

function getFeaturesAndTreeStructure(numInImg, callback) {
    const url = `${dataServerUrl}/getFeaturesAndTreeStructure`
    let params = { "numInImg": numInImg }
    request(url, params, POST_REQUEST, callback);
}

function getImputationResults(treeSource, numInImg, modifiedTree, bindArray, callback) {
    const url = `${dataServerUrl}/getImputationResults`
    let params = { "treeSource": treeSource, "numInImg": numInImg, "modifiedTree": modifiedTree, "bindArray": bindArray }
    request(url, params, POST_REQUEST, callback);
}

export default {
    dataServerUrl,
    getFeaturesAndTreeStructure,
    getImputationResults
}
