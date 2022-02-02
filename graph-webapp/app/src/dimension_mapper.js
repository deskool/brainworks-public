import {Tool} from "./tool.js"
import * as utils from "./utils.js"
import "./lib/sigma_animate.min.js"

// TODO: Currently doesn't support nested data keys beyond the initial attributes["data"].
//  - This means that the data object cannot have any nests, which isn't a huge problem at the moment,
//    but I can imagine it might be needed later down the road.
//  - In order to implement this, the methods that assign a mapping need to be able to specify data keys within nested keys,
//    and I haven't decided how that's going to work.
//  - Should it be syntactical like a directory structure? e.g. mapper.node_size('property1/subprop4/subsub2',0,1)
//  - Should it be like a list instead? e.g. mapper.node_size(['property1','subprop4','subsbu2'],0,1)
//  - Or should it be explicitly related to JSON? e.g. mapper.node_size({'property1': {'subprop4': 'subsub2'}},0,1)
//  - Also, the validate_graph() method will need to ensure that all nodes have the same data tree, even if nests have
//    all null values. Currently doesn't do this.
//  - However, I did implement full recursive traversal for the InteractiveTool when displaying node properties in
//    the right-click menu, so theres that. yay.

// NOTE: This class adds a global "degree" attribute to each node, which can be used as a node property for mapping purposes.
// TODO: If we ever implement dynamic adding of nodes/edges, make sure to update the node degree attribute: this.graph.setNodeAttribute(node, 'degree', this.graph.degree(node))

// NOTE: when referring to "attributes", these are any key-value pairs, including the built-ins used by sigma.
//      "data" refers to the "data" attribute, a nested object with custom assigned key-value pairs.


// constants
const CATEGORICAL = 'cat'
const CONTINUOUS = 'cont'
const SLIDER = 'slider'
const NODE = 'node'
const EDGE = 'edge'

const TREE_ANIMATE_DURATION = 500  // node expansion/collapse animation time

export class DimensionMapper extends Tool {
    // provides methods for mapping node/edge data to visual graph dimensions
    constructor(state) {
        super(state)

        // index of all data properties and whether they are categorical or continuous
        this.data = {[NODE]: {}, [EDGE]: {}}

        // index of sliders {<slider_name>: {node:<bool>, edge:<bool>, key:<data_key>, min: <min>, max: <max>}}
        this.sliders = {}

        this.init();
    }

    init() {
    }

    init_graph() {
        this.validate_graph()  // make sure it's in the proper format
        // write a function to check only a single node/edge, then call those in validate_graph.
        this.state.tree = new Tree(this.state, this)  // initialize tree

    }
    validate_graph() {
        // Ensures that all nodes all have the same set of data keys, and all edges have the same set of data keys.
        // If a node/edge is missing a certain data key, assign null
        // Ensure that all nodes have an accurate "degree" data key
        // Checks whether each data key has continuous or categorical data.
        //    - If any values in a key are not numerical, the whole set is categorical.

        // loop through all nodes to collect full set of data keys and check type
        this.graph.forEachNode((node, attributes) => {
            if (!attributes["data"]) return;  // if no data attribute, ignore
            for (let [key, val] of Object.entries(attributes["data"])) {
                let types = this.data[NODE]
                if (typeof val !== "number") {  // if any value is not a number, this data key is categorical
                    types[key] = CATEGORICAL
                } else if (this.data[NODE][key] === undefined) {  // if a number AND not checked yet, its continuous
                    types[key] = CONTINUOUS
                }
            }
        });

        // loop through all edges to collect full set of data keys
        this.graph.forEachEdge((edge, attributes) => {
            if (!attributes["data"]) return;  // if no data attribute, ignore
            for (let [key, val] of Object.entries(attributes["data"])) {
                let types = this.data[EDGE]
                if (typeof val !== "number") {  // if any value is not a number, this data key is categorical
                    types[key] = CATEGORICAL
                } else if (types[key] === undefined) {  // if a number AND not checked yet, its continuous
                    types[key] = CONTINUOUS
                }
            }
        });

        // make sure all nodes have all node data keys
        this.graph.updateEachNodeAttributes((node, attributes) => {
            var data = attributes["data"] || {}
            Object.keys(this.data[NODE]).forEach((key) => {
                if (!data.hasOwnProperty(key)) {
                    data[key] = null
                }
            })
            attributes["data"] = data  // set new data
            return attributes;
        });

        // make sure all edges have all edge data keys
        this.graph.updateEachEdgeAttributes((edge, attributes) => {
            var data = attributes["data"] || {}
            Object.keys(this.data[EDGE]).forEach((key) => {  // for each key, make sure this node has it
                if (!data.hasOwnProperty(key)) {
                  data[key] = null;  // assign null to new data key
                }
            })
            attributes["data"] = data  // set new data
            return attributes;
        });

        // set data values that aren't set manually.
        this.add_default_data()
    }
    add_default_data() {
        // Adds attributes values to each node/edge that do not have to be manually set.
        // Don't forget to add it to this.node_data or this.edge_data if it is a data value

        // node degree
        this.data[NODE]["degree"] = CONTINUOUS
        this.graph.forEachNode((node, attributes) => {
            this.set_node_data(node, "degree", this.graph.degree(node))
        });

        // node tree depth
        this.graph.forEachNode((node, attributes) => {
            this.graph.setNodeAttribute(node, "depth", 0)
        })

        // node/edge slider dimension values
        // a separate nested attribute
        this.graph.forEachNode((node, attributes) => {
            this.graph.setNodeAttribute(node, "sliders", {})
        })
        this.graph.forEachEdge((edge, attributes) => {
            this.graph.setEdgeAttribute(edge, "sliders", {})
        })

        // if node doesn't have coords, assign random.
        // If no size, assign default.
        // If no color, assign default.
        this.graph.updateEachNodeAttributes((node, attr) => {
            attr.x = (attr.x !== undefined) ? attr.x : (Math.random()-0.5)*100
            attr.y = (attr.y !== undefined) ? attr.y : (Math.random()-0.5)*100
            //attr.zIndex = 1
            attr.size = (attr.size !== undefined) ? attr.size : 10
            attr.color = (attr.color !== undefined) ? attr.color : "#C0C0C0"
            return attr;
        });

        this.graph.forEachEdge((edge, attr) => {
            attr.color = (attr.color !== undefined) ? attr.color : "#C0C0C0"
        });
    }

    // Given a node/edge attributes object, get a specific custom data key
    get_data(attributes, key=null) {
        // If key is not given, return all data keys
        if (key === null)
            return attributes["data"]
        return attributes["data"][key]
    }
    // given a node/edge, set a specific custom data key and value
    set_node_data(node, key, value) {
        let data = this.graph.getNodeAttribute(node, "data")
        data[key] = value
        this.graph.setNodeAttribute(node, "data", data)
    }
    set_edge_data(edge, key, value) {
        let data = this.graph.getEdgeAttribute(edge, "data")
        data[key] = value
        this.graph.setNodeAttribute(edge, "data", data)
    }

    // Given a node/edge attributes object, get a specific slider value
    get_slider(attributes, key=null) {
        // If key is not given, return all slider keys
        if (key === null)
            return attributes["sliders"]
        return attributes["sliders"][key]
    }
    // given a node/edge and slider name, set that node/edge slider value
    set_node_slider(node, key, value) {
        // given a node, set a slider value
        let data = this.graph.getNodeAttribute(node, "sliders")
        if (data != undefined) {
            data[key] = value
        } else {
            data = {[key]: value}
        }
        this.graph.setNodeAttribute(node, "sliders", data)
    }
    set_edge_slider(edge, key, value) {
        // given a edge, set a slider value
        let data = this.graph.getEdgeAttribute(edge, "sliders")
        data[key] = value
        this.graph.setEdgeAttribute(edge, "sliders", data)
    }

    // given whether 'node' or 'edge' data, return the type of the given data key
    get_data_type(element_type, key) {
        if (element_type !== NODE && element_type !== EDGE) {
            throw Error(`Specify node or edge for the data to retrieve. Got "${element_type}"`)
        }
        if (this.data[element_type][key] === undefined) {
            console.error(`No ${element_type==NODE?"nodes":"edges"} have the data key "${key}"`)
            return false
        }
        return this.data[element_type][key]
    }
    // finds the statistics for a specific data key across the given nodes/edges
    data_statistics(type, key, elements=[]) {
        if (elements.length == 0) {  // if elements not specified, use whole graph
            elements = (type == NODE) ? this.graph.nodes() : this.graph.edges()
        }
        let getAttributes = (type == NODE) ? node => this.graph.getNodeAttributes(node) : edge => this.graph.getEdgeAttributes(edge)
        let stats = {}
        if (this.data[type][key] === CONTINUOUS) {  // continuous data
            for (let elem of elements) {
                let attr = getAttributes(elem)
                let value = this.get_data(attr, key)  // get value for this data key
                if (value != undefined) {
                    if (stats.min === undefined || value < stats.min)
                        stats.min = value;
                    if (stats.max === undefined || value > stats.max)
                        stats.max = value;
                }
            }
        } else {  // categorical data
            stats.frequency = {}  // maps categories to their frequency
            for (let elem of elements) {
                let attr = getAttributes(elem)
                let value = this.get_data(attr, key)  // get value for this data key
                if (value != undefined) {
                    stats.frequency[value] = stats.frequency[value] === undefined ? 1 : stats.frequency[value]+1
                }
            }

            // also just a sorted list of all the categories
            stats.categories = Array.from(Object.keys(stats.frequency)).sort()
        }
        return stats
    }

    // reducers for rendering temporary states
    node_reducer(node, attrs) {
        // hide node if not visible in the tree
        if (this.is_out_of_tree(attrs)) {
            this.hide(attrs)
            //this.obscure(attrs)
        }

        // hide node based on slider setting
        for (let [name, slider] of Object.entries(this.sliders)) {  // for each slider
            if (!slider[NODE]) continue;  // slider not mapped to nodes
            if (!this.is_tree_node(node)) {  // regular node
                if (this.get_slider(attrs, name) == undefined || this.get_slider(attrs, name) < slider.min || this.get_slider(attrs, name) > slider.max) {
                    this.out_of_range(attrs)  // if this node's mapped slider value is outside the slider range (or undefined), it's out of range
                }
            } else {  // tree branches have a min and max value
                if (this.get_slider(attrs, name) == undefined || this.get_slider(attrs, name).max < slider.min || this.get_slider(attrs, name).min > slider.max) {
                    this.out_of_range(attrs)  // if this tree node's min and max slider values are outside the slider range (or undefined), it's out of range
                }
            }
        }

        // if this node's size or color is undefined, it's out of range
        if (attrs.color == undefined || attrs.size == undefined) {
            this.out_of_range(attrs)
        }

        return attrs;
    }
    edge_reducer(edge, attrs) {  // return temporary edge properties
        // hide edges based on slider settings
        for (let [name, slider] of Object.entries(this.sliders)) {  // for each slider
            if (!slider[EDGE]) continue;
            if (!this.is_tree_edge(edge)) {
                if (this.get_slider(attrs, name) == undefined || this.get_slider(attrs, name) < slider.min || this.get_slider(attrs, name) > slider.max) {
                    this.hide(attrs)  // if this edge's mapped slider value is outside the slider range, or is undefined, hide it
                }
            } else {  // tree edges have a min and max value
                if (this.get_slider(attrs, name) == undefined || this.get_slider(attrs, name).max < slider.min || this.get_slider(attrs, name).min > slider.max) {
                    this.hide(attrs)  // if this tree edge's min and max slider values are outside the slider range (or undefined), hide it.
                }
            }
        }
        // if this edge is connected to an obscured node, hide it
        let nodes = this.graph.extremities(edge)
        if (this.is_node_obscured(nodes[0]) || this.is_node_obscured(nodes[1])) {
            this.hide(attrs)
        }
        return attrs;
    }

    //
    // numerical mapping methods
    //

    linear_map(val, input_min, input_max, output_min, output_max) {
        // map a value linearly between input and output, given two points
        if (val == undefined) return undefined;
        if (input_min == input_max) return (output_max+output_min)/2  // undefined slope
        let slope = (output_max - output_min) / (input_max - input_min)
        return slope * (val - input_min) + output_min
    }


    //
    // General mapping methods
    //

    // mapping data keys to various types of dimensions
    map_dimension(element_type, key, dimension, dimension_type, map) {
        // element_type is either NODE or EDGE
        // key is the data key to map
        // dimension is the dimension to map to
        // dimension_type is CONTINUOUS, CATEGORICAL, or SLIDER
        // map is the appropriate mapping from key to dimension
        let data_type = this.get_data_type(element_type, key)  // data key type. CATEGORICAL or CONTINUOUS
        let stats = null;

        // retrieve statistics on the given data key
        stats = this.data_statistics(element_type, key)

        // get either node or edge iterator
        let updateIterator = element_type == NODE ? node => this.graph.updateEachNodeAttributes(node) : edge => this.graph.updateEachEdgeAttributes(edge)

        // continuous to continuous mapping
        if (data_type == CONTINUOUS && dimension_type == CONTINUOUS) {
            this.continuous_to_continuous(updateIterator, key, dimension, stats, map)
        }
        // continuous to categorical mapping
        if (data_type == CONTINUOUS && dimension_type == CATEGORICAL) {
            console.error("Continuous to Categorical mapping not yet implemented")
        }
        // categorical to continuous and categorical to categorical (same)
        if (data_type == CATEGORICAL && (dimension_type == CATEGORICAL || dimension_type == CONTINUOUS)) {
            this.categorical_to_categorical(updateIterator, key, dimension, map)
        }

        // sliders
        if (dimension_type === SLIDER) {
            this.to_slider(element_type, data_type, key, dimension, stats, map)
        }

    }

    // specific element mapping functions
    continuous_to_continuous(updateIterator, key, dimension, stats, map) {
        // get a node/edge iterator, map this data key to this dimension
        if (map.min === undefined || map.max === undefined) {
            console.log(`Map must specify map.min and map.max, the min/max values of the target dimension "${dimension}".`)
        }

        updateIterator((elem, attr) => {
            let value = this.get_data(attr, key)  // get data value of this key
            attr[dimension] = this.linear_map(value, stats.min, stats.max, map.min, map.max)
            return attr;
        });
    }
    continuous_to_categorical(updateIterator, key, dimension, map) {
        // map a continuous data value with a categorical dimension
        // map [object]:
        //  - keys: DATA VALUE WHERE THE CATEGORY STARTS
        //  - values: DIMENSION CATEGORY

        // TODO: what to use as map input? Can't use object because object keys cannot be numbers.
        // maybe take in the same map as categorical_to_continuous - a map of dimension categories to data values.
        // Then automatically calculate uniform ranges to assign? greater than, less than, middle, etc.
        //  A Map object can associate numbers with values. maybe that?
        //   Maybe require a function to be input as a map? takes in a number and outputs a category

        updateIterator((node, attr) => {
            let value = this.get_data(attr, key)  // data value of this node
            // TODO: find which dimension category this value should be mapped to

            attr[dimension]
            return attr;
        });
    }
    categorical_to_categorical(updateIterator, key, dimension, map) {
        // map a categorical data key to a continuous dimension
        // map [Object]:
        //  - keys: DATA CATEGORY VALUE (strings)
        //  - values: DIMENSION VALUE (numbers)
        // If a data value is not given in the mapping, the value will be undefined
        updateIterator((node, attr) => {
            let value = this.get_data(attr, key)  // get data value of this key
            attr[dimension] = map[value]  // get mapped dimension value
            return attr;
        });
    }

    to_slider(element_type, data_type, key, slider_name, stats, map) {
        // iterate over either nodes or edges
        let elementIterator = element_type == NODE ? func => this.graph.forEachNode(func) : func => this.graph.forEachEdge(func)
        let setElementSlider = element_type == NODE ? (...args) => this.set_node_slider(...args) : (...args) => this.set_edge_slider(...args)

        // continuous to slider mapping
        if (data_type == CONTINUOUS) {
            this.continuous_to_slider(elementIterator, setElementSlider, key, slider_name, stats)
        }
        // continuous to slider mapping
        if (data_type == CATEGORICAL) {
            this.categorical_to_slider(elementIterator, setElementSlider, key, slider_name, stats)
        }

    }
    continuous_to_slider(elementIterator, setElementSlider, key, slider_name, stats) {
        elementIterator((node, attr) => {
            let slider_value = this.get_data(attr, key)  // get data value of this key
            setElementSlider(node, slider_name, slider_value)  // set element slider value
        });

        let slider = this.sliders[slider_name]
        let min = stats.min
        let max = stats.max

        // if the absolute minimum has already been set, that means another slider already exists
        if (slider.abs_min === undefined) {  // no slider already exists
            slider.abs_min = min  // set absolute min and max
            slider.abs_max = max
        } else {  // a slider has already been created
            // update absolute min and max instead
            slider.abs_min = slider.abs_min < min ? slider.abs_min : min
            slider.abs_max = slider.abs_max > max ? slider.abs_max : max
        }
        this.add_continuous_slider(slider_name, slider.abs_min, slider.abs_max)  // create new slider
    }
    categorical_to_slider(elementIterator, setElementSlider, key, slider_name, stats) {
        // will automatically collect all data categories and assign slider positions
        let map = {}  // map categories to a slider value
        for (var i=0; i<stats.categories.length; i++) {
            map[stats.categories[i]] = i
        }
        elementIterator((node, attr) => {
            let data_value = this.get_data(attr, key)  // get data value of this key
            let slider_value = map[data_value]
            setElementSlider(node, slider_name, slider_value)  // set dimension value
        });
        // mapping slider values to data categories
        let reverse_map = new Map(Object.entries(map).map(entry => entry.reverse()))
        this.add_categorical_slider(slider_name, reverse_map)
    }

    // Filter sliders with noUiSlider
    add_continuous_slider(name, min, max) {
        let slider = this.create_slider_html(name)

        if (max - min > 0) {
            var decimals = utils.decimals(max-min)  // number of decimals to display based on range
        } else {
            var decimals = 0
        }

        // pad min and max so values don't get rounded out of range
        let range_pad = Math.pow(0.1, decimals)
        min -= range_pad
        max += range_pad

        noUiSlider.create(slider, {
            start: [min, max],  // starting positions of handles
            range: {'min': min, 'max': max},
            tooltips: true,  // visually controlled with css .noUi-tooltip
            connect: [false, true, false],  // whether to fill in areas between handles
            behaviour: 'drag',  // allow dragging area between handles
            format: {
                to: (value) => value.toFixed(decimals).toString(),
                from: (string) => parseFloat(string)
            },
            pips: {  // tick marks
                mode: 'count',
                values: 5,  // pip major ticks
                density: 5,  // 1 minor tick every 5 percent
                format: {
                    to: (value) => value.toFixed(decimals).toString(),
                }
            }
        });

        slider.noUiSlider.on("update", (values, handle) => {  // bind the slider update event
            this.slider_event(name, values[0], values[1])  // pass in name, min val, and max val
        })
    }
    add_categorical_slider(name, map) {
        // adds a slider element to the page
        // map must be a map that maps slider values to categories
        let slider = this.create_slider_html(name)

        let keys = Array.from(map.keys())  // array of numerical keys
        let min = Math.min(...keys)  // minimum
        let max = Math.max(...keys)  // maximum

        let percents = {}  // object of percentage values mapping to numerical values for noUiSlider
        for (let i=0; i<keys.length; i++) {
            let p;
            if (i==0) p="min";
            else if (i==keys.length-1) p="max";
            else p=`${100*keys[i]/max}%`;
            percents[p] = keys[i]
        }

        noUiSlider.create(slider, {
            start: [min],  // starting positions of handles
            range: percents,
            tooltips: false,  // visually controlled with css .noUi-tooltip
            snap: true,  // snap handle to range values
            pips: {  // tick marks
                mode: 'range',
                density: 100,  //  only tick exactly at each range step
                format: {  // convert numerical slider value to category
                    to: (value) => map.get(value)
                }
            }
        });

        slider.noUiSlider.on("update", (values, handle) => {  // bind the slider update event
            this.slider_event(name, values[0], values[0])  // min and max value are the same for one slider
        })
    }
    create_slider_html(name) {
        // adds a slider element to the page
        let id = name.replaceAll(' ', '')
        let old_div = $(`div.slider_container#${id}`)
        if (old_div[0]) {  // a slider div for this ID already exists
            old_div.remove()  // remove it
        }
        let $slider_div = $(`<div class="slider_container" id="${id}"><span>${name}:</span></div>`).appendTo("#sliders")
        let $slider = $(`<div class="slider"></div>`).appendTo($slider_div)
        return $slider[0]  // html dom element
    }
    slider_event(slider_name, min_value, max_value) {
        // called by a slider when it's value is changed
        this.sliders[slider_name].min = min_value
        this.sliders[slider_name].max = max_value
        this.sigma.refresh()
    }

    // Tree cluster slider
    // TODO: tree slider doesn't work well because the animations can't skip a level.
    add_tree_slider() {
        // adds a slider element to the page for cluster tree traversal
        let id = "tree_slider"
        let old_div = $(`div#${id}`)
        if (old_div[0]) {  // a slider div for this ID already exists
            old_div.remove()  // remove it
        }
        let $slider_div = $(`<div id="${id}"><p>Cluster Tree</p></div>`).appendTo("body")//("#interface")
        let $slider = $(`<div class="slider"></div>`).appendTo($slider_div)//("#interface")

        let levels = []  // indexes are levels and values are the levels names, plus an extra "all" level.
        let i = 0
        for (let level of this.state.tree.levels) {
            levels[i] = level
            i++
        }
        levels[i] = "all"  // last level is is where all nodes are open. doesn't have a name associated with it
        let max = levels.length-1  // max level number

        let percents = {}  // object of percentage values mapping to numerical values for noUiSlider
        for (let i=0; i<levels.length; i++) {
            let p;
            if (i==0) p="min";
            else if (i==max) p="max";
            else p=`${100*i/(max)}%`;
            percents[p] = i
        }

        // noUISlider needs the html dom element, not the jquery object.
        noUiSlider.create($slider[0], {
            start: [1],  // starting positions of handles
            range: percents,
            orientation: 'vertical',
            tooltips: true,  // visually controlled with css .noUi-tooltip
            snap: true,  // snap handle to range values
            pips: {  // tick marks
                mode: 'range',
                density: 100,  //  only tick exactly at each range step
                format: {
                    to: () => ""
                }
            },
            format: {  // convert numerical slider value to category
                to: (i) => levels[i],
                from: (val) => levels.indexOf(val)
            }
        });

        $slider[0].noUiSlider.on("update", (values) => {  // bind the slider update event
            this.state.tree.set_depth(levels.indexOf(values[0]))
        })
    }
    add_tree_buttons() {
        let $div = $("div#tree").show()
        let $up = $("div#tree button#tree_up")
        let $down = $("div#tree button#tree_down")

        $up.on("click", () => {
            if (this.slow_down_clicks(TREE_ANIMATE_DURATION))
                this.state.tree.modify_depth(1)
        })
        $down.on("click", () => {
            if (this.slow_down_clicks(TREE_ANIMATE_DURATION))
                this.state.tree.modify_depth(-1)
        })
    }
    slow_down_clicks(interval) {
        // returns true if called long enough after the last call
        let now = Date.now();
        if (this.last_click_time && now - this.last_click_time < interval) {
            return false;
        }
        this.last_click_time = now;
        return true;
    }

    //
    // For external use
    //

    node_size(key, map) {
        this.map_dimension(NODE, key, 'size', CONTINUOUS, map)
    }
    node_color(key, map) {
        this.map_dimension(NODE, key, 'color', CATEGORICAL, map)
    }
    node_slider(key, slider_name) {
        this.slider(NODE, key, slider_name)
    }
    edge_size(key, map) {
        this.map_dimension(EDGE, key, 'size', CONTINUOUS, map)
    }
    edge_color(key, map) {
        this.map_dimension(EDGE, key, 'color', CATEGORICAL, map)
    }
    edge_slider(key, slider_name) {
        this.slider(EDGE, key, slider_name)
    }
    slider(element_type, key, slider_name) {
        if (this.sliders[slider_name] != undefined) {  // a slider exists with the same name
            if (this.sliders[slider_name][element_type]) {  // this slider is already attached to this element type
                let elem_name = element_type==NODE?"node":"edge"
                console.error(`Extra instances of ${elem_name} slider "${slider_name}" were not added. Other ${elem_name} sliders with the same name are already assigned.`)
                return;
            }
            // this element type is not attached to this slider
            let slider_key = this.sliders[slider_name].data  // data key already assigned to this slider
            if (slider_key !== key) {  // data keys don't match
                console.error(`${elem_name} slider "${slider_name}" was not added. Its mapped data key does not match the first instance: ${first_key} =/= ${key}`)
                return;
            }
            if (this.get_data_type(NODE, key) !== this.get_data_type(EDGE, key)) {  // if not the same data type in both edges and nodes
                console.error(`${elem_name} slider "${slider_name}" was not added. They data key "${key}" is not the same data type in both nodes and edges.`)
                return;
            }
            this.sliders[slider_name][element_type] = true // associate this slider with this element type
        } else {  // slider with this name does not currently exist
            this.sliders[slider_name] = {[element_type]: true, data: key}
        }
        this.map_dimension(element_type, key, slider_name, SLIDER)
    }

    cluster(keys) {
        // given a list of data keys, create a tree structure with one level for each key
        this.state.tree.create_tree(keys)
        //this.add_tree_slider()
        this.add_tree_buttons()
    }

    // import JSON config for default mappings
    // Basically translates an object to the above function calls
    import_config(config) {
        if (config !== undefined) {
            if (config.maps !== undefined) {
                var allowed_methods = ['node_size', 'node_color', 'node_slider', 'cluster', 'edge_size', 'edge_color', 'edge_slider']
                for (let map of config.maps) {  // for each given map method
                    if (allowed_methods.includes(map.dimension)) {  // if an allowed dimension
                        if (map.data != undefined) {
                            this[map.dimension](map.data, map.args)  // call corresponding mapper method with given arguments
                        } else {
                            this[map.dimension](map.args)  // call corresponding mapper method with given arguments
                        }
                    } else {
                        console.error(`Mapping dimension does not exist "${map.dimension}" does not exist. Possible dimensions are: ${allowed_methods}`)
                    }
                }
            }
        }
        if (!this.state.tree.created) {  // if the tree wasn't created (no clustering specified in config)
            this.state.tree.create_tree([])  // create tree with no levels.
        }
        this.state.tree.update_tree_attributes()  // update branch node/edge properties given any new data mappings
    }

}

class Tree extends Tool {
    constructor(state, mapper) {
        super(state)
        this.state = state
        this.mapper = mapper  // reference to DimensionMapper
        this.trunk = {}  // nested structure of branches
        this.root_key = 'root'  // unique node key of the tree root
        this.branch_map = new Map() // map of node keys to their branch object
        this.depth_map = new Map()  // map of tree depth to an array of node keys at each depth
        this.parent_map = new Map()  // map node keys (both nodes and branches) to their parent's key
        this.height = 0  // current height of the tree
        this.depth = 0  // current viewing depth
        this.opened = new Map()  // keys:  currently opened nodes, values:  arrays with all sub-nodes of that node
        this.cluster_cache = {}  // keys: branch node, values: {nodes: [], edges: [], degrees: Map, depth: int, graph: graph}
        this.levels = []  // list of levels in this tree
        this.created = false  // whether the tree has been generated

        this.state.tree = this

        this.init()
    }

    init() {
        this.clear_trunk()
    }

    // reset trunk to default properties
    clear_trunk() {
        this.trunk.nodes = this.graph.nodes()  // start with all the graph nodes
        this.trunk.branches = []  // begin with no branches
        this.trunk.depth = 0  // this is the root branch
        this.trunk.level = null
        this.trunk.name = null
        this.trunk.node_key = this.root_key
    }

    // given a node, return all it's sub-branch and sub-node keys in an array
    get_cluster(node) {
        let branch = this.branch_map.get(node)
        let nodes = []
        if (!(branch.branches == undefined || branch.branches.length == 0)) {
            nodes = nodes.concat(branch.branches.map(branch => branch.node_key))
        }
        if (!(branch.nodes == undefined || branch.nodes.length == 0)) {
            nodes = nodes.concat(branch.nodes)
        }
        return nodes
    }

    // return array of all open branch node keys
    get_open_branches() {
        return Array.from(this.opened.keys())
    }

    // add new levels to the tree, splitting nodes according to categories
    add_levels(levels) {
        if (levels === undefined) {  // if no levels given
            levels = this.get_optimal_levels()
        }
        this.levels = []
        for (let level of levels) {
            if (this.mapper.data[NODE][level] !== CATEGORICAL) continue;  // must be categorical
            this.add_level(level, this.trunk)  // add each level to the structure
            this.levels.push(level)
            this.height++  // increment height
        }
    }
    add_level(key, branch) {
        if (branch.branches == undefined || branch.branches.length == 0) {  // base case: no sub-branches
            let {categories} = this.mapper.data_statistics(NODE, key, branch.nodes)  // values of this data key
            branch.branches = []

            // get the split of nodes in each category
            let split = this.split_leaves(branch.nodes, key, categories)

            // create all category branches
            for (let [cat, nodes] of Object.entries(split)) {
                let new_branch = {
                    parent: branch.node_key,  // parent branch key
                    depth: branch.depth + 1,
                    level: key,  // data property key
                    name: cat,   // data property category
                    nodes: nodes,
                    node_key: branch.node_key + `-${key}-${cat}`
                }
                branch.nodes = []  // clear nodes from this branch
                branch.branches.push(new_branch)  // add new branch to its parent
            }
        } else {  // otherwise, recursively call on each branch until base case
            for (let twig of branch.branches) {  // for each sub-branch
                this.add_level(key, twig)
            }
        }
    }
    split_leaves(nodes, key, categories) {
        // split given nodes into separate categories of the given data key
        // returns object with keys of each category, and values are lists of all nodes in that category
        let leaves = {}
        for (let cat of categories) {
            leaves[cat] = []
        }

        for (let node of nodes) {
            let attrs = this.graph.getNodeAttributes(node)
            let category = this.mapper.get_data(attrs, key)
            leaves[category].push(node)  // add node to appropriate category
        }

        // TODO temporary until I can connect nodes to branches
        // if any category only has one node, instead put it in the 'MISC' category
        leaves['MISC'] = []
        for (let [cat,nodes] of Object.entries(leaves)) {
            if (nodes.length == 1) {
                leaves['MISC'].push(nodes[0])
                delete leaves[cat]
            }
        }
        if (leaves['MISC'].length == 0) {
            delete leaves['MISC']
        }

        return leaves
    }
    // determines the optimal hierarchical structure, and returns an array of category names in that order.
    get_optimal_levels() {
        let levels = {}  // all categorical data keys mapped to how many categories it has
        for (let [data, type] of Object.entries(this.mapper.data[NODE])) {
            if (type !== CATEGORICAL) continue;  // must be categorical
            let stats = this.mapper.data_statistics(NODE, data)
            if (stats.categories.length > 1)  // only make it a level if there is more than 1 category
                levels[data] = stats.categories.length
        }
        console.log('tree levels:', levels)
        // return list of levels sorted by number of categories
        return Object.keys(levels).sort(function(a,b){return levels[a]-levels[b]})
    }

    log_tree() {
        if (this.levels == undefined || this.levels.length == 0) return;
        this.depth_map.forEach((value, key) => {
            if (key === 0 || key === this.height+1) return;  // top or bottom
            let level = this.levels[key-1]
            console.log(level+': ', value)
        })
    }

    // add a new tree node/edge to the graph
    add_new_node(key, attrs) {
        let defaults = {
            x: 0,
            y: 0,
            size: 100,
            color: "#111111",
            data: {},
            sliders: {},
            tree: true
        }
        this.graph.addNode(key, Object.assign(defaults, attrs))
    }
    add_new_edge(key, source, target, attrs) {
        let defaults = {
            size: 1,
            color: "#111111",
            data: {},
            sliders: {},
            tree: true
        }
        // add this edge if it doesn't exist. If it does, update it's properties.
        this.graph.mergeUndirectedEdgeWithKey(key, source, target, Object.assign(defaults, attrs))
    }

    // creates all lookup maps for the tree
    create_maps() {
        this.branch_map = new Map()  // clear maps
        this.depth_map = new Map()
        this.parent_map = new Map()
        this.opened = new Map()
        this.update_branch_map(this.trunk)  // recursively update branch_map and parent_map
        this.update_depth_map()  // update depth_map
    }
    update_branch_map(branch, parent) {
        this.branch_map.set(branch.node_key, branch)  // map the node key to it's branch
        if (branch.branches != undefined) {  // sub branches
            for (let twig of branch.branches) {  // for each sub-branch
                this.update_branch_map(twig, branch)  // recursively update the map for these sub-branches
            }
        }
        // also update parent_map while we're here
        this.parent_map.set(branch.node_key, parent ? parent.node_key:parent)  // map the node key to the parent key
        if (branch.nodes != undefined) {  // sub nodes
            for (let node of branch.nodes) {  // for each sub-node
                this.parent_map.set(node, branch.node_key)  // map the node key to the parent key
            }
        }
        // base case is no sub branches
    }
    update_depth_map() {
        this.branch_map.forEach((branch, key) => {
            if (this.depth_map.has(branch.depth)) {  // update depth map
                this.depth_map.get(branch.depth).push(branch.node_key)
            } else {
                this.depth_map.set(branch.depth, [branch.node_key])
            }

            // also add non-branch nodes to depth below it
            if (!this.depth_map.has(branch.depth+1)) {
                this.depth_map.set(branch.depth+1, [])
            }
            for (let node of branch.nodes) {
                this.depth_map.get(branch.depth+1).push(node)
            }
        })
    }
    update_node_depth() {
        this.depth_map.forEach((nodes, depth) => {
            for (let node of nodes) {
                this.graph.setNodeAttribute(node, "depth", depth)  // set node depth attribute
            }
        })
    }

    // remove all current branch nodes from the graph
    remove_from_graph() {
        this.branch_map.forEach((mapping, node) => {
            this.graph.dropNode(node)
        })
    }

    // adding and updating tree branch/edge properties
    add_to_graph(branch) {
        // recursively add all branch nodes to the graph
        let attributes = {
            label: branch.name,
            level: branch.level,
            depth: branch.depth,
            name: branch.name  // data category
        }
        if (branch.depth == 0) {  // root branch
            attributes.label = 'tree-root'
            attributes.size = 0
            attributes.hidden = true
            attributes.fixed = true
        } else {
            attributes.data = {
                [branch.level]: branch.name  // assign to it's mapped data category
            }
        }
        this.add_new_node(branch.node_key, attributes)  // add it to the graph

        if (branch.branches == undefined) {  // base case: no sub-branches
            return;
        } else {  // otherwise, recursively call on each branch until base case
            for (let twig of branch.branches) {  // for each sub-branch
                this.add_to_graph(twig)
            }
        }
    }
    update_branch_attributes() {
        // make branch nodes reflect attributes of their sub-nodes
        let attribute_map = new Map()  // map of branch keys to their attribute list
        this.get_cluster_attributes(this.trunk.node_key, attribute_map)  // populate it

        // assign node attributes from attribute_map
        attribute_map.forEach((attributes, key) => {
            let avg_size = Math.max(...attributes.sizes)  // max sub node size
            this.graph.setNodeAttribute(key, 'size', avg_size)
            let most_color = utils.array_mode(attributes.colors)  // most common sub node color
            this.graph.setNodeAttribute(key, 'color', most_color)

            let sliders = {}  // min and max of each slider
            for (let [name, vals] of Object.entries(attributes.sliders)) {
                let min_val = Math.min(...vals)
                let max_val = Math.max(...vals)
                sliders[name] = {min:min_val, max:max_val}
            }
            this.graph.setNodeAttribute(key, 'sliders', sliders)
        })
    }
    get_cluster_attributes(node, attribute_map) {
        // recursively populate attribute map
        // attribute_map: keys are branch node keys, values are object with nodes as keys and the following attrs object as values
        // sliders has slider names as keys and a list of all slider values as value
        let branch = this.branch_map.get(node)
        let attrs = attribute_map.get(node) || {sizes: [], colors: [], sliders: {}}

        // populate ndoe sliders
        for (let name of Object.keys(this.mapper.sliders)) {
            if (!this.mapper.sliders[name].node) continue
            attrs.sliders[name] = []
        }

        if (branch.branches != undefined) {  // has sub branches
            for (let twig of branch.branches) {  // for each sub-branch
                this.get_cluster_attributes(twig.node_key, attribute_map)  // recursively get attributes
                // add child attrs lists to parent attrs lists
                let child_attrs = attribute_map.get(twig.node_key)
                attrs.sizes = attrs.sizes.concat(child_attrs.sizes)
                attrs.colors = attrs.colors.concat(child_attrs.colors)
                for (let name of Object.keys(child_attrs.sliders)) {
                    attrs.sliders[name] = attrs.sliders[name].concat(child_attrs.sliders[name])
                }

            }
            attribute_map.set(node, attrs)
        }  // base case is it has no sub branches'

        // has sub nodes
        if (branch.nodes != undefined) {
            for (let sub_node of branch.nodes) {
                attrs.sizes.push(this.graph.getNodeAttribute(sub_node, 'size'))
                attrs.colors.push(this.graph.getNodeAttribute(sub_node, 'color'))
                for (let [name,val] of Object.entries(this.graph.getNodeAttribute(sub_node, 'sliders'))) {
                    attrs.sliders[name].push(val)
                }
            }
            attribute_map.set(node, attrs)
        }

    }
    update_branch_edges() {
        // make branch edges reflect attributes of their sub-edges

        // maps each node to all other nodes, with edge properties between them
        // first level keys are node keys, second level are connecting node keys, third level are edge attributes.
        let attribute_map = {}
        this.get_cluster_edges(attribute_map)  // populate it

        // add/merge edge attributes from attributes map
        for (let [node, edges] of Object.entries(attribute_map)) {  // for each branch
            let node_label = this.graph.getNodeAttribute(node, 'label')
            for (let [other_node, edge] of Object.entries(edges)) {  // for each other branch
                if (edge.count === 0) continue;  // if no connections, don't create a branch edge
                let other_node_label = this.graph.getNodeAttribute(other_node, 'label')
                let attributes = {
                    tree: true,
                    //label: node_label + "<->" + other_node_label  // default branch edge label  // TODO put back in when overlapping label issue is solved.
                    count: edge.count,  // number of sub edges
                    color: utils.array_mode(edge.colors),  // most common color
                    size: utils.array_mean(edge.sizes),  // average size
                    sliders: {},
                }
                for (let [name, vals] of Object.entries(edge.sliders)) {
                    let min_val = Math.min(...vals)
                    let max_val = Math.max(...vals)
                    attributes.sliders[name] = {min:min_val, max:max_val}
                }
                this.add_new_edge(`${node}<->${other_node}`, node, other_node, attributes)
            }
        }
    }
    get_cluster_edges(edges) {
        // add edges to graph and populate the attribute map
        var sliders_template = {}  // edge slider map template
        for (let name of Object.keys(this.mapper.sliders)) {
            if (!this.mapper.sliders[name].edge) continue
            sliders_template[name] = []
        }

        for (let depth=this.height; depth>0; depth--) {  // start at bottom tree branch depth, and go up to depth 1
            for (let node of this.depth_map.get(depth)) {  // for each node at this depth
                let branch = this.branch_map.get(node)  // get branch object for this node key
                if (branch == undefined) continue; // this is a regular node, move on

                // keep track of all edges from this branch
                edges[node] = {}
                for (let other_node of this.depth_map.get(depth)) {  // for all other branch nodes at this depth
                    // if other_node is already connected to this node, and if they are different nodes. (don't double count the same connection)
                    if (node !== other_node && edges[other_node] !== undefined) continue;
                    edges[node][other_node] = {
                        count: 0, // number of sub-edges between these two branches
                        colors: [],  // list of sub-edge colors
                        sizes: [],  // list of sub-edge sizes
                        sliders: $.extend(true, {}, sliders_template)  // deep copy the slider template
                    }
                }

                // collect edge attributes from regular nodes
                if (branch.nodes != undefined) {
                    let checked_edges = new Set()  // temporarily keep track of edges checked so as not to double count
                    for (let sub_node of branch.nodes) {  // for each sub node
                        this.graph.forEachEdge(sub_node, (edge) => {  // for each edge of this sub node
                            if (!checked_edges.has(edge)) { // haven't checked this edge yet
                                let attrs = this.graph.getEdgeAttributes(edge)  // edge attributes
                                let adj = this.graph.opposite(sub_node, edge)  // get adjacent node
                                let other_node = this.parent_map.get(adj)  // get parent of adjacent node
                                if (edges[node][other_node] !== undefined) {  // this connection is defined, add all sub-node attributes
                                    edges[node][other_node].count += 1
                                    edges[node][other_node].colors.push(attrs.color)
                                    edges[node][other_node].sizes.push(attrs.size)
                                    for (let [name, val] of Object.entries(attrs.sliders)) {
                                        edges[node][other_node].sliders[name].push(val)
                                    }
                                }
                                checked_edges.add(edge)  //  mark edge as checked
                            }
                        })
                    }
                }

                // collect sub-edge attributes from sub-branch nodes
                if (branch.branches != undefined) {
                    for (let sub_branch of branch.branches) {  // for each sub branch
                        for (let [other_sub_node, sub_edge] of Object.entries(edges[sub_branch.node_key])) {  // for each connection of this sub branch
                            let other_node = this.parent_map.get(other_sub_node)  // get parent of sub branch connection
                            if (edges[node][other_node] !== undefined) {  // if this connection is defined, append all sub-edge attributes
                                edges[node][other_node].count += sub_edge.count
                                edges[node][other_node].colors = edges[node][other_node].colors.concat(sub_edge.colors)
                                edges[node][other_node].sizes = edges[node][other_node].sizes.concat(sub_edge.sizes)
                                for (let [name, val] of Object.entries(sub_edge.sliders)) {
                                    edges[node][other_node].sliders[name] = edges[node][other_node].sliders[name].concat(val)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    update_tree_attributes() {
        // update both branches and edges
        this.update_branch_attributes()
        this.update_branch_edges()
    }

    // retrieves info about the sub-graph of a given branch. Uses this.cluster_cache
    get_cluster_info(branch) {
        if (this.cluster_cache[branch] == undefined) {  // none stored
            let nodes = new Set(this.get_cluster(branch))  // get cluster (this branch's children)
            let edge_map = new Map() // map of node keys to array of its edges
            let degree_map = new Map()  // map of node keys to it's cluster degree (only counting edges within the cluster)
            let edges = new Set()
            let graph = this.graph.nullCopy()  // sub-graph for this cluster. Copies graph type & properties, but not nodes or edges

            var cluster = new Cluster(this.state, graph, branch)

            for (let node of nodes) {  // for each node
                let attrs = this.graph.getNodeAttributes(node)
                cluster.graph.addNode(node, (({x,y,size})=>({x,y,size}))(attrs))  // add node (and x,y,size attrs) to subgraph
                edge_map.set(node, [])  // set empty array in edge map
                degree_map.set(node, 0)  // initialize degree at 0
                this.graph.forEachEdge(node, (edge) => {edges.add(edge)})  // collect all edges
            }
            for (let edge of edges) {  // for each edge
                let extremities = this.graph.extremities(edge)  // nodes at each end
                if (!(nodes.has(extremities[0]) && nodes.has(extremities[1]))) {  // if either extremity isn't in the cluster
                    edges.delete(edge)  // remove from edge collection
                } else {  // both extremities are in the cluster
                    cluster.graph.addEdgeWithKey(edge, extremities[1], extremities[0])  // TODO is the ordering of these guaranteed? should I use .source and .target instead?
                    edge_map.get(extremities[0]).push(edge)  // add this edge to each node's edge map
                    edge_map.get(extremities[1]).push(edge)
                    //degree_map.set(extremities[0], degree_map.get(extremities[0])+1)
                    //degree_map.set(extremities[1], degree_map.get(extremities[1])+1)
                }
            }

            cluster.graph = graph
            //cluster.degrees = degree_map
            cluster.depth = this.branch_map.get(branch).depth
            cluster.update()  // update cluster stats

            this.cluster_cache[branch] = cluster  // store cluster in cache
        }
        return this.cluster_cache[branch]  // return cached cluster
    }

    //
    // External methods
    //

    // updates the tree structure given an array of levels (data keys), top to bottom
    create_tree(levels) {
        this.log("Creating Tree")
        this.remove_from_graph()  // remove all nodes in branch_map from the graph

        this.clear_trunk()  // clear branch structure
        this.cluster_cache = {}  // clear edge cache

        this.add_levels(levels)  // add the given levels to the tree
        this.create_maps()  // create maps from the new tree structure

        this.add_to_graph(this.trunk)  // recursively add all branch nodes in the structure to the graph
        this.update_tree_attributes()  // branch/edge attributes reflect sub node/edge attributes

        this.update_node_depth() // set depth of nodes from depth_map and set out_of_tree state

        this.log_tree()  // output tree structure to console

        this.sigma.refresh()  // force the sigma.nodeDataCache to populate so the physics simulator works in the first open_node()

        // initialize state of tree
        this.branch_map.forEach((branch, key) => {
            this.open_node(key, false)  // all start open, no animation
        })

        this.sigma.setCustomBBox(this.sigma.getBBox())  // set bounding box to encompass entire opened graph
        this.state.interaction.home_bbox = this.sigma.getCustomBBox()  // set this as the home bbox

        this.close_node(this.root_key, false)  // close the whole tree, starting at the root (ensures all branches collapse their sub nodes)
        this.open_node(this.root_key, false)
        this.sigma.refresh()

        this.created = true
    }

    // set entire tree open to a given depth
    set_depth(depth, animate=true) {
        depth = Math.round(depth)  // integer
        // can't set depth beyond from 0 to height
        if (depth < 0) {
            depth = 0;
        } else if (depth > this.height) {
            depth = this.height;
        }
        this.depth = depth  // track current depth
        // close all nodes one depth lower
        if (this.height > depth) {
            for (let node of this.depth_map.get(depth+1)) {
                this.close_node(node, animate)
            }
        }
        // open all nodes at this depth
        for (let node of this.depth_map.get(depth)) {
            this.open_node(node, animate)
        }
    }
    // modify current viewing depth by n
    modify_depth(n=1) {  // default is increase by 1
        this.set_depth(this.depth+n)
    }

    // open a branch node - add it and its immediate sub-nodes to this.opened, as well as every parent branch.
    open_node(node, animate=true) {
        // if it's already open, or it's not a tree node at all, do nothing else
        if (this.opened.get(node) != undefined || !this.mapper.is_tree_node(node)) return;

        if (this.branch_map.get(node).parent != undefined) {  // if the node has a parent
            this.open_node(this.branch_map.get(node).parent, animate)  // recursively open all parents
        }
        // this.depth = this.branch_map.get(node).depth
        // TODO This can only work if the tree is able to go from any level to any other level (and have the animations work).

        this.opened.set(node, this.get_cluster(node))
        this.graph.setNodeAttribute(node, "out_of_tree", true)  // opened branches are considered out of tree

        // expand the cluster
        let cluster = this.get_cluster_info(node)
        cluster.expand(animate)

    }

    // closes the branch node - removes it and ALL its sub nodes (recursively) from this.opened
    close_node(node, animate=false) {
        // if already closed, or not even a tree node, do nothing
        if (this.opened.get(node) == undefined || !this.mapper.is_tree_node(node)) return;

        for (let sub_branch of this.opened.get(node)) {  // close all sub branches first
            this.close_node(sub_branch, animate)
        }

        this.opened.delete(node)  // remove from this.opened

        // collapse the cluster
        var cluster = this.get_cluster_info(node)
        cluster.collapse(animate)



    }
}

class Cluster {
    constructor(state, local_graph, node) {
        this.state = state
        this.sigma = state.sigma
        this.tree = state.tree
        this.global_graph = state.tree.graph

        this.graph = local_graph  // dynamic graph that updates the global graph position
        this.optimal_graph = null  // constant version of the graph with nodes in optimal positions

        this.degree_map = new Map()
        this.depth = this.global_graph.getNodeAttribute(node, 'depth')
        this.scale = this.state.simulation.scale(this.depth)

        this.parent = node
        this.starting_local_positions = {}  // starting local positions for expansino

        // functions to cancel the current animation and timeout
        this._cancel_animation = null
        this._cancel_timeout = null
    }

    log(msg, time=false) {
        // logs a message and optionally show the amount of time passed since called last
        let now = window.performance.now()
        if (time && this.last_time) {
            let elapsed = now - this.last_time
            console.log(`${msg} (${elapsed}ms)`)
        } else {
            console.log(msg)
        }
        this.last_time = now
    }

    // update properties and graph stats. Should be called after graph fully created
    update() {
        this.optimal_graph = this.graph.copy()
        // need to spread out nodes a bit for physics to work
        let angle = 2*Math.PI / this.graph.order  // angle to spread cluster out by
        let radius = 1 / (100*this.scale)  // radius to spread cluster out by
        let n = 0
        this.optimal_graph.updateEachNodeAttributes((node, attr) => {
            attr.x = radius * Math.cos(angle*n)
            attr.y = radius * Math.sin(angle*n)
            n += 1
            return attr
        })
        this.state.simulation.simulate(this.optimal_graph, 50, true)  // run some iterations of FA to place nodes
    }

    global_to_local(global_positions, assign=true) {
        // convert the given global node positions to local node positions, and optionally assign them
        // if none given, use current global positions and assign them
        let parent_pos = this.global_graph.getNodeAttributes(this.parent)  // get parent position
        let local_positions = {}
        if (!global_positions) {
            global_positions = {}
            this.graph.forEachNode((node, attrs) => {
                global_positions[node] = this.global_graph.getNodeAttributes(node)  // get GLOBAL attrs of this node
            })
        }

        for (let [node, pos] of Object.entries(global_positions)) {
            let x = (pos.x - parent_pos.x) * this.scale
            let y = (pos.y - parent_pos.y) * this.scale
            local_positions[node] = {x:x, y:y}
            if (assign) this.graph.mergeNodeAttributes(node, {x:x, y:y})
        }
        return local_positions
    }
    local_to_global(local_positions, assign=true) {
        // convert the given local node positions to global node positions and optionally assign those positions
        // if none given, use current local positions and assign them
        let parent_pos = this.global_graph.getNodeAttributes(this.parent)  // get parent position
        let global_positions = {}
        if (!local_positions) {
            local_positions = {}
            this.graph.forEachNode((node, attrs) => {
                local_positions[node] = attrs  // get LOCAL attrs of this node
            })
        }
        for (let [node, pos] of Object.entries(local_positions)) {
            let x = pos.x/this.scale + parent_pos.x
            let y = pos.y/this.scale + parent_pos.y
            global_positions[node] = {x:x, y:y}
            if (assign && !this.tree.is_node_fixed(node)) this.global_graph.mergeNodeAttributes(node, {x:x, y:y})
        }
        return global_positions
    }

    set_animation(cancel_function) {
        // cancel_function is the function returned by Sigma animateNodes()
        this._cancel_animation = cancel_function
    }
    set_timeout(timeout_id) {
        this._cancel_timeout = () => {clearTimeout(timeout_id)}
    }
    cancel_animation() {
        if (this._cancel_animation) this._cancel_animation()
        if (this._cancel_timeout) this._cancel_timeout()
    }

    // TODO: more modular way of modifying node attributes. Right now the tool.fix() is the one that sets the 'fixed' attr, and it's only meant to be used in reducers.
    // Since I am manually setting the 'fixed' attr here, I have to be sure to manually unset it as well.

    expand_start() {
        for (let node of this.graph.nodes()) {
            this.global_graph.setNodeAttribute(node, 'fixed', true)  // prevent physics
            this.global_graph.setNodeAttribute(node, "out_of_tree", false)  // now in the tree
        }
    }
    expand_stop() {
        for (let node of this.graph.nodes()) {
             this.global_graph.setNodeAttribute(node, 'fixed', false)    // allow physics
        }
    }
    collapse_start() {
        for (let node of this.graph.nodes()) {
            this.global_graph.setNodeAttribute(node, 'fixed', true)  // prevent physics
        }
    }
    collapse_stop() {
        for (let node of this.graph.nodes()) {
             this.global_graph.setNodeAttribute(node, 'fixed', false)    // allow physics
             this.global_graph.setNodeAttribute(node, "out_of_tree", true)  // put out of tree
        }
        this.global_graph.setNodeAttribute(this.parent, "out_of_tree", false)  // parent comes back into tree
    }

    expand(animate=true) {
        // animate cluster expanding outward from parent node
        this.cancel_animation()

        // move all global nodes to parent position
        let parent_pos = this.global_graph.getNodeAttributes(this.parent)
        for (let node of this.graph.nodes()) {
            this.global_graph.setNodeAttribute(node, 'x', parent_pos.x)
            this.global_graph.setNodeAttribute(node, 'y', parent_pos.y)
        }

        // set optimal local cluster node positions
        this.graph = this.optimal_graph.copy()

        this.expand_start()
        if (animate) {
            let global_positions = this.local_to_global(null, false)  // convert to global positions, but don't assign to global graph
            this.set_animation = Animate.animateNodes(this.global_graph, global_positions, {duration: TREE_ANIMATE_DURATION, easing: "quadraticOut"});

            let timeout = setTimeout(() => {this.expand_stop()}, TREE_ANIMATE_DURATION)
            this.set_timeout(timeout)
        } else {
            this.local_to_global()  // update global instantly from local positions
            this.expand_stop()
        }
    }
    collapse(animate=true) {
        // animate cluster collapsing in toward the parent
        this.cancel_animation()  // cancel current cluster animation
        let parent_pos = this.global_graph.getNodeAttributes(this.parent)  // get parent position

        let global_positions = {}
        for (let node of this.graph.nodes()) {
            global_positions[node] = {x:parent_pos.x, y:parent_pos.y}  // all nodes collapse to parent position
        }
        let local_positions = {}
        for (let node of this.graph.nodes()) {
            local_positions[node] = {x:0, y:0}  // all nodes collapse to parent position
        }
        this.collapse_start()
        if (animate) {
            this.set_animation = Animate.animateNodes(this.global_graph, global_positions, {duration: TREE_ANIMATE_DURATION, easing: "quadraticOut"});

            let timeout = setTimeout(() => {this.collapse_stop()}, TREE_ANIMATE_DURATION)
            this.set_timeout(timeout)
        } else {
            this.local_to_global(local_positions, true)
            this.collapse_stop()
        }
    }

}
