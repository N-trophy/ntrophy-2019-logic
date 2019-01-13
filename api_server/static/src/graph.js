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
        throw new Error('invalid format string.');
    }
    return fmt.replace(/((?:[^{}]|(?:\{\{)|(?:\}\}))+)|(?:\{([0-9]+)\})/g, (m, str, index) => {
        if (str) {
            return str.replace(/(?:{{)|(?:}})/g, m => m[0]);
        } else {
            if (index >= args.length) {
                throw new Error('argument index is out of range in format');
            }
            return args[index];
        }
    });
}

function new_node(id, x, y, size){
    return {
        id: 'n' + id,
        label: format("[{0}, {1}]", x, y),
        x: x,
        y: y,
        size: size * 10,
        shape: 'dot',
        fixed: true,
        // color: '#333',
    } 
}

function station_node(x, y){
    var node = new_node(undefined, x, y, 1);
    node.id = 's' + station_id++;
    node.color = '#aa3512';
    return node;
}

var station_counter = 0;
var station_id = 0;

function update_graph(graph_spec){
    var nodes = new vis.DataSet(graph_spec.nodes.map(node => {
        return new_node(node[0], node[1], node[2], node[3])
    }))
    station_id = 0
    station_counter = 0
    
    // create an array with edges
    var edges = new vis.DataSet(graph_spec.edges.map(edge => {
        return {
            from: 'n' + edge[1],
            to: 'n' + edge[2],
            smooth: false,
        }
    }))
    
    // create a network
    var container = document.getElementById('graph-container');
    
    // provide the data in the vis format
    var data = {
        nodes: nodes,
        edges: edges,
    };
    var options = {
        physics: {
            enabled: false,
        }
    };
    
    // initialize your network!
    var network = new vis.Network(container, data, options);
    network.on('click',function(event){
        if(station_counter < 1 && event.nodes.length == 0 && event.edges.length == 1) {
            station_counter++
            nodes.add([
                station_node(event.pointer.canvas.x, event.pointer.canvas.y)
            ])
        }
        if(event.nodes.length == 1 && event.nodes[0][0] == 's') {
            nodes.remove(event.nodes[0])
            station_counter--
        }
    })
}