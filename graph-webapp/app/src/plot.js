import {Simulator} from "./physics_simulator.js"
import {Interaction} from "./interaction.js"
import {DimensionMapper} from "./dimension_mapper.js"
import {Menu} from "./menu.js"

export class Plot {
    // Manages graph state and interaction with all tools
    constructor() {
        this.graph = new graphology.MultiUndirectedGraph();  // graph object
        this.container = document.getElementById("sigma-container");  // get html div for sigma display
        this.sigma = new sigma.Sigma(this.graph, this.container, {  // sigma renderer
            renderLabels: false,
            renderEdgeLabels: false,
            enableEdgeClickEvents: true,
            enableEdgeWheelEvents: true,
            enableEdgeHoverEvents: "debounce",
            zIndex: true
            //nodeProgramClasses: {
                //image: getNodeProgramImage(),
                //border: NodeProgramBorder,
            //},

        });

        // prepend each node/edge key with this to ensure no overlap with branches added after import
        this.key_prefix = "_"

        this.state = {  // global graph state object
            graph: this.graph,
            sigma: this.sigma,
            settings: {},
            tree: null,
            interaction: null,
            simulation: null
        }

        // Menu interface
        this.menu = new Menu(this.state)

        // node interactivity
        this.interact = new Interaction(this.state)

        // Simulate physics
        this.simulator = new Simulator(this.state);

        // Allow mapping of properties to data dimensions
        this.mapper = new DimensionMapper(this.state)

        // init
        this.init()
    }

    init() {
        // set node/edge render conditions based on state
        this.render()
    }

    // Render Nodes and Edges according to internal states
    render() {
        this.sigma.setSetting("nodeReducer", (node, attrs) => {  // return conditional node properties
            attrs = this.mapper.node_reducer(node, attrs)  // first apply value-mapped rendering
            attrs = this.interact.node_reducer(node, attrs)  // then interaction rendering
            attrs = this.menu.node_reducer(node, attrs)  // then menu settings
            return attrs;
        });

        this.sigma.setSetting("edgeReducer", (edge, attrs) => {  // return conditional edge properties
            attrs = this.mapper.edge_reducer(edge, attrs)  // first apply value-mapped rendering
            attrs = this.interact.edge_reducer(edge, attrs)  // then interaction rendering
            attrs = this.menu.edge_reducer(edge, attrs)  // then menu settings
            return attrs;
        });
    }

    // show an error
    error(error, message) {
        this.interact.error(error, message)
    }

    // import a JSON data with a graph and config options
    import(data) {
        if (data == undefined || data.graph == undefined) {
            this.error("No graph data given.", "Could not find the graph in the JSON data provided. See documentation for proper JSON structure.")
            return
        }

        // prepend all node/edge keys with an underscore to ensure no overlap with keys that I add
        let graph = data.graph
        for (let node of graph.nodes) {
            node.key = this.key_prefix+node.key
        }
        for (let edge of graph.edges) {
            edge.key = this.key_prefix+edge.key
            edge.undirected = true  // ensure undirected
            edge.source = this.key_prefix+edge.source
            edge.target = this.key_prefix+edge.target
        }

        this.graph.import(graph)  // initialize graph

        this.interact.init_graph()
        this.simulator.init_graph()
        this.mapper.init_graph()
        this.menu.init_graph()

        // Optional Config
        if (data.config == undefined) {
            console.log("No optional config found.")
        }
        this.mapper.import_config(data.config)

    }

}

