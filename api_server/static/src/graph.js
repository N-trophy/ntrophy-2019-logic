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

var S = undefined

function init_sigma(){
    S = new sigma({
        graph: {nodes:[], edges:[]},
        renderers: [
            {
                container: document.getElementById('graph-container'),
                type: 'canvas'
            }
        ],
        settings: {
            doubleClickEnabled: true,
            enableEdgeHovering: true,
            maxEdgeSize: 4,
        }
    });

    S.bind('clickEdge', function(e) {
        console.log(e)
        if (e.data.captor.isDragging) return;
        S.graph.addNode({
            id: format('n.{0}.{1}', e.data.edge.id, Math.random()),
            label: format("[{0}, {1}]", e.data.captor.x, e.data.captor.y),
            x: e.data.captor.x,
            y: e.data.captor.y,
            size: 20,
            color: 'aa4444',
        })
        S.refresh();        
    });
}

function update_graph(graph_spec){
    S.graph.clear()
    graph_spec.nodes.forEach(node => {
        S.graph.addNode({
            id: 'n' + node[0],
            label: format("[{0}, {1}]", node[1], node[2]),
            x: node[1],
            y: node[2],
            size: node[3],
            color: '#333',
        })
    })
    graph_spec.edges.forEach(edge => {
        S.graph.addEdge({
            id: 'e' + edge[0],
            source: 'n' + edge[1],
            target: 'n' + edge[2],
            size: 20,
            color: '#ccc'        
        })
    })
    S.refresh()
}