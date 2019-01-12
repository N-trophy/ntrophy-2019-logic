 /**
 * This is a basic example on how to instantiate sigma. A random graph is
 * generated and stored in the "graph" variable, and then sigma is instantiated
 * directly with the graph.
 *
 * The simple instance of sigma is enough to make it render the graph on the on
 * the screen, since the graph is given directly to the constructor.
 */
var nodes_specs = [
    [0, 10, 20, 10],
    [1, 20, 30, 10],
    [2, 10, 50, 5],
    [3, 15, 25, 15],
]

var edges_specs = [
    [0, 0, 1],
    [1, 1, 2],
    [2, 2, 3],
    [3, 1, 3],
]

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


g = {
    nodes: nodes_specs.map(node => {
        return {
            id: 'n' + node[0],
            label: format("[{0}, {1}]", node[1], node[2]),
            x: node[1],
            y: node[2],
            size: node[3],
            color: '#333',
        }
    }),
    edges: edges_specs.map(edge => {
        return {
            id: 'e' + edge[0],
            source: 'n' + edge[1],
            target: 'n' + edge[2],
            size: 10,
            color: '#ccc'        
        }
    })
};

// Instantiate sigma:
s = new sigma({
graph: g,
container: 'graph-container'
});