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

function point_dist(x1, y1, x2, y2){
    dx = x1-x2
    dy = y1-y2
    return Math.sqrt(dx*dx+dy*dy)
}

function rot_left(p){
    nx = p.x * Math.sqrt(2)/2 - p.y * Math.sqrt(2)/2
    ny = p.x * Math.sqrt(2)/2 + p.y * Math.sqrt(2)/2
    return {x: nx, y: ny}
}

function rot_right(p){
    nx = p.x * Math.sqrt(2)/2 + p.y * Math.sqrt(2)/2
    ny = - p.x * Math.sqrt(2)/2 + p.y * Math.sqrt(2)/2
    return {x: nx, y: ny}
}

function edge_point_dist(edge, x, y){
    if (edge.from.x == edge.to.x) {
        if ((y > edge.from.y && y > edge.to.y) || (y < edge.from.y && y < edge.to.y)) {
            dist_from = point_dist(x, y, edge.from.x, edge.from.y)
            dist_to = point_dist(x, y, edge.to.x, edge.to.y)
            if (dist_from < dist_to) return {dist: dist_from, point: edge.from}
            else return {dist: dist_to, point: edge.to}
        } else return {dist: Math.abs(x - edge.from.x), point: {x: edge.from.x, y: y}}
    }
    if (edge.from.y == edge.to.y) {
        if ((x > edge.from.x && x > edge.to.x) || (x < edge.from.x && x < edge.to.x)) {
            dist_from = point_dist(x, y, edge.from.x, edge.from.y)
            dist_to = point_dist(x, y, edge.to.x, edge.to.y)
            if (dist_from < dist_to) return {dist: dist_from, point: edge.from }
            else return {dist: dist_to, point: edge.to}
        } else return {dist: Math.abs(y - edge.from.y), point: {x:x, y: edge.from.y}}
    }
    from_nx = rot_left(edge.from).x
    from_ny = rot_left(edge.from).y
    to_nx = rot_left(edge.to).x
    to_ny = rot_left(edge.to).y
    nx = rot_left({x:x, y:y}).x
    ny = rot_left({x:x, y:y}).y
    if (Math.abs(from_nx - to_nx) < 0.01) {
        if ((ny > from_ny && ny > to_ny) || (ny < from_ny && ny < to_ny)) {
            dist_from = point_dist(nx, ny, from_nx, from_ny)
            dist_to = point_dist(nx, ny, to_nx, to_nx)
            if (dist_from < dist_to) return {dist: dist_from, point: edge.from}
            else return {dist: dist_to, point: edge.to}
        } else return {dist: Math.abs(nx - from_nx), point: rot_right({x: from_nx, y: ny})}
    }
    if (Math.abs(from_ny - to_ny) < 0.01) {
        if ((nx > from_nx && nx > to_nx) || (nx < from_nx && nx < to_nx)) {
            dist_from = point_dist(nx, ny, from_nx, from_ny)
            dist_to = point_dist(nx, ny, to_nx, to_nx)
            if (dist_from < dist_to) return {dist: dist_from, point: edge.from }
            else return {dist: dist_to, point: edge.to}
        } else return {dist: Math.abs(ny - from_ny), point: rot_right({x: nx, y: from_ny})}
    }
}

function get_nearest_edge(x, y){
    edge = Object.values(network.body.edges)[0]
    res = edge_point_dist(edge, x, y)
    min_dist = res.dist
    min_pos = res.point
    for (key in network.body.edges) {
        res = edge_point_dist(network.body.edges[key], x, y)
        dist = res.dist
        if (dist < min_dist) {
            min_dist = dist
            edge = network.body.edges[key]
            min_pos = res.point
        }
    }
    return [edge, min_pos]
}

function clip_to_edge(edge, x, y){
    if (edge.from.x == edge.to.x) return { x: edge.from.x, y:y }
    if (edge.from.y == edge.to.y) return { x: x, y: edge.from.y }
    vx = x-edge.from.x
    vy = y-edge.from.y
    ux = edge.to.x-edge.from.x
    uy = edge.to.y-edge.from.y
    nx = -uy
    ny = ux
    norm_len = Math.sqrt(nx*nx + ny*ny)
    len = (vx*uy-vy*ux)/norm_len
    
    nx *= len/norm_len
    ny *= len/norm_len
    x += nx
    y += ny
    return {x:x, y:y}
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
        .then(after_eval)
        .catch(err=>{
            console.log(err);
            document.getElementById('eval-info').innerHTML = "Kontaktujte organizátory (" + err + ")";
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
        .then(after_submit)
        .catch(err=>{
            console.log(err);
            document.getElementById('submit-info').innerHTML = "Kontaktujte organizátory (" + err + ")";
        })
}

// Graph handler
function new_node(id, x, y, size){
    title = format("[{0},{1}] (id: \"{2}\")", x, y, id)
    if (place_anywhere) {
        title = format("[{0},{1}]", x, y)
    }
    return {
        id: 'n' + id,
        x: x,
        y: y,
        chosen: false,
        label: weighted_nodes == "True" ? ""+size : false,
        size: Math.sqrt(size) * 10,
        shape: 'dot',
        fixed: true,
        title: title,
        shadow:{
            enabled: false,
        },
        shapeProperties: {
            borderDashes: false, // only for borders
            borderRadius: 6,     // only for box shape
            interpolation: false,  // only for image and circularImage shapes
            useImageSize: false,  // only for image and circularImage shapes
            useBorderWithImage: false  // only for image shape
        },
        color: "#ff2828",
    }
}

function new_station_node(x, y){
    var node = new_node(undefined, x, y, 2)
    node.id = 's' + next_station_id++
    node.color = '#87ebff'
    node.title = false
    node.fixed = false
    node.title = undefined
    node.label = format("[{0},{1}]", x.toFixed(2), y.toFixed(2))
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
var score
var remaining_evals = 0

function update_node(event){
    x = event.pointer.canvas.x
    y = event.pointer.canvas.y
}

function place_node(event){
    x = event.pointer.canvas.x
    y = event.pointer.canvas.y
    event_nodes = event.nodes.filter(node => node[0]=='n')
    if (event_nodes.length){
        center = get_node_by_id(event_nodes[0])
        x = center.x
        y = center.y
    }
    if (place_anywhere) {
        station_counter++
        let n = new_station_node(x, y)
        data_to_send[n.id] = {x:x, y:y}
        nodes.add([n])
    } else {
        station_counter++
        data = get_nearest_edge(x, y)
        e = data[0]
        x = data[1].x
        y = data[1].y
        let n = new_station_node(x, y)
        data_to_send[n.id] = {
            x: x,
            y: y,
            edge_a: e.fromId.substr(1),
            edge_b: e.toId.substr(1)
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
            label: weighted_edges == "True" ? ""+edge[2] : false,
            smooth: false,
            color: "#383737",
            chosen: false,
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
        if (event.event.srcEvent.ctrlKey) {
            for(let i=0;i<event.nodes.length;i++) {
                if (is_station_node(event.nodes[i])) {
                    delete_node(event.nodes[i])
                    deleted = true
                    break
                }
            }
        } else {
            if(station_counter < max_number_of_stations){
                place_node(event)
            }
        }
    })

    network.on('dragEnd', function(event){
        if (event.nodes.length == 0) return
        x = event.pointer.canvas.x
        y = event.pointer.canvas.y

        if (!place_anywhere) {
            data = get_nearest_edge(x, y)
            console.log(data[0])
            x = data[1].x
            y = data[1].y
        }

        id = event.nodes[0]
        data_to_send[id].x = x
        data_to_send[id].y = y
        node = get_node_by_id(id)
        nodes.remove(node)
        let n = new_station_node(x, y)
        nodes.add(n)
        data_to_send[n.id] = data_to_send[id]
        if (!place_anywhere) {
            data_to_send[n.id].edge_a = data[0].to.id.substr(1)
            data_to_send[n.id].edge_b = data[0].from.id.substr(1)
        }
        delete data_to_send[id]
    })
}
