 /**
 * This is a basic example on how to instantiate sigma. A random graph is
 * generated and stored in the "graph" variable, and then sigma is instantiated
 * directly with the graph.
 *
 * The simple instance of sigma is enough to make it render the graph on the on
 * the screen, since the graph is given directly to the constructor.
 */

function format(fmt, ...args) {
    if (!fmt.match(/^(?:(?:(?:[^{}]|(?:\{\{)|(?:\}\}))+)|(?:\{[0-9]+\}))+$/)) {
        throw new Error('invalid format string.')
    }
    return fmt.replace(/((?:[^{}]|(?:\{\{)|(?:\}\}))+)|(?:\{([0-9]+)\})/g, (m, str, index) => {
        if (str) {
            return str.replace(/(?:{{)|(?:}})/g, m => m[0])
        } else {
            if (index >= args.length) {
                throw new Error('argument index is out of range in format')
            }
            return args[index]
        }
    })
}


// Evaluator
function station_nodes_as_cords(){
    return Object.values(network.body.nodes).filter(node=>node.id[0]=='s').map(node => {return {x: node.x, y: node.y}})
}

function eval(){
    cords = station_nodes_as_cords()
    axios({
            method:'post',
            url: SITE_DOMAIN + format('/level/{0}/eval', level_id),
            data: cords,
            headers: {
                "X-CSRFToken": CSRF_TOKEN, 
                "content-type": "application/json"
            }
        })
        .then(res=>{
            console.log(res.data)  
        })
        .catch(err=>{
            console.log(err)
        })
}

function submit(){
    cords = station_nodes_as_cords()
    axios({
            method:'post',
            url: SITE_DOMAIN + format('/level/{0}/submit', level_id),
            data: cords,
            headers: {
                "X-CSRFToken": CSRF_TOKEN, 
                "content-type": "application/json"
            }
        })
        .then(res=>{
            console.log(res.data)  
        })
        .catch(err=>{
            console.log(err)
        })
}

// Graph handler
function new_node(id, x, y, size){
    return {
        id: 'n' + id,
        // label: format("[{0}, {1}]", x, y),
        x: x,
        y: y,
        size: size * 10,
        shape: 'dot',
        fixed: true,
        // color: '#333',
    } 
}

function new_station_node(x, y){
    var node = new_node(undefined, x, y, 1)
    node.id = 's' + next_station_id++
    node.color = '#aa3512'
    return node
}

var network
var station_counter = 0
var next_station_id = 0
var max_number_of_stations = 0

function init_graph(graph_spec){
    var nodes = new vis.DataSet(graph_spec.nodes.map(node => {
        return new_node(node[0], node[1], node[2], node[3])
    }))
    next_station_id = 0
    station_counter = 0
    max_number_of_stations = graph_spec.stations
    
    // create an array with edges
    var edges = new vis.DataSet(graph_spec.edges.map(edge => {
        return {
            from: 'n' + edge[0],
            to: 'n' + edge[1],
            smooth: false,
        }
    }))
    
    // create a network
    var container = document.getElementById('graph-container')
    
    // provide the data in the vis format
    var data = {
        nodes: nodes,
        edges: edges,
    }
    var options = {
        physics: {
            enabled: false,
        }
    }
    
    function place_node(event){
        station_counter++
        nodes.add([
            new_station_node(event.pointer.canvas.x, event.pointer.canvas.y)
        ])
    }

    function is_station_node(node){
        return node[0] == 's'
    }

    // initialize your network!
    network = new vis.Network(container, data, options)
    network.on('click',function(event){
        if(station_counter < max_number_of_stations){
            console.log(event)
            place_node(event)
        }
        for(let i=0;i<event.nodes.length;i++) {
            if (is_station_node(event.nodes[i])) {
                nodes.remove(event.nodes[i])
                station_counter--
                break
            }
        }
    })
}