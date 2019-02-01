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


function get_node_by_id(id){
    let n = Object.values(network.body.nodes).filter(node=>node.id==id)
    if (n.length) return n[0]
}

function get_edge_by_id(id){
    let n = Object.values(network.body.edges).filter(edge=>edge.id==id)
    if (n.length) return n[0]
}

function get_edge_by_node_id(id){
    for (key in network.body.edges) {
        edge = network.body.edges[key]
        if (edge.toId == id || edge.fromId == id) return edge
    }
}

function eval(){
    cords = Object.values(data_to_send)
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
            score = document.getElementById('score')
            score.innerText = res.data.score
        })
        .catch(err=>{
            console.log(err)
        })
}

function submit(){
    cords = Object.values(data_to_send)
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
        x: x,
        y: y,
        label: ""+size,
        size: Math.sqrt(size) * 10,
        shape: 'dot',
        fixed: true,
        title: format("[{0},{1}] (score: {2}, id: \"{3}\")", x, y, size, id),
        shadow:{
            enabled: false,
        },
        shapeProperties: {
            borderDashes: false, // only for borders
            borderRadius: 6,     // only for box shape
            interpolation: false,  // only for image and circularImage shapes
            useImageSize: false,  // only for image and circularImage shapes
            useBorderWithImage: false  // only for image shape
        }
    }
    // color: '#333', 
}

function new_station_node(x, y){
    var node = new_node(undefined, x, y, 2)
    node.id = 's' + next_station_id++
    node.color = '#aa3512'
    node.fixed = false
    return node
}

var network
var nodes
var edges
var place_anywhere = false
var station_counter = 0
var next_station_id = 0
var max_number_of_stations = 0
var data_to_send = {}

function place_node(event){
    x = event.pointer.canvas.x
    y = event.pointer.canvas.y
    event_nodes = event.nodes.filter(node => node[0]=='n')
    if (event_nodes.length){
        center = get_node_by_id(event_nodes[0])
        x = center.x
        y = center.y
    } else if (event.edges.length) {
        e = get_edge_by_id(event.edges[0])
        from = get_node_by_id(e.fromId)
        to = get_node_by_id(e.toId)
        vx = x-from.x
        vy = y-from.y
        ux = to.x-from.x
        uy = to.y-from.y
        nx = -uy
        ny = ux
        norm_len = Math.sqrt(nx*nx + ny*ny)
        len = (vx*uy-vy*ux)/norm_len
        
        nx *= len/norm_len
        ny *= len/norm_len
        x += nx
        y += ny
    }
    if (place_anywhere || event.edges.length){
        station_counter++
        let n = new_station_node(x, y)
        data_to_send[n.id] = {x:x, y:y}
        if (!place_anywhere && event.edges.length) {
            e = get_edge_by_id(event.edges[0])
            data_to_send[n.id].edge_a = e.fromId.substr(1)
            data_to_send[n.id].edge_b = e.toId.substr(1)
        }
        if (!place_anywhere && event.nodes.length) {
            e = get_edge_by_node_id(event.nodes[0])
            data_to_send[n.id].edge_a = e.fromId.substr(1)
            data_to_send[n.id].edge_b = e.toId.substr(1)
        }
        nodes.add([n])
    }
}

function delete_node(node_id){
    nodes.remove(node_id)
    station_counter--
    delete data_to_send[node_id]
}

function init_graph(graph_spec){
    if (graph_spec.edges.length == 0) place_anywhere = true
    nodes = new vis.DataSet(Object.entries(graph_spec.nodes).map(rec => {
        return new_node(rec[0], rec[1][0], rec[1][1], rec[1][2])
    }))
    next_station_id = 0
    station_counter = 0
    max_number_of_stations = graph_spec.stations
    
    // create an array with edges
    edges = new vis.DataSet(graph_spec.edges.map(edge => {
        return {
            from: 'n' + edge[0],
            to: 'n' + edge[1],
            label: "" + edge[2],
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

    function is_station_node(node){
        return node[0] == 's'
    }

    // initialize your network!
    network = new vis.Network(container, data, options)
    network.on('click',function(event){
        deleted = false
        for(let i=0;i<event.nodes.length;i++) {
            if (is_station_node(event.nodes[i])) {
                delete_node(event.nodes[i])
                deleted = true
                break
            }
        }
        if(!deleted && station_counter < max_number_of_stations){
            place_node(event)
        }
    })

    network.on('dragEnd', function(event){
        console.log(event.edges)
    })
}