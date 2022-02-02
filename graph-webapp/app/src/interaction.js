import "./lib/shortest_path.min.js"
import {Tool} from "./tool.js"

const NODE = 'node'
const NODE_EX = 'Node1, Node 2,'
const EDGE = 'edge'
const EDGE_EX = 'Edge1, Edge 2'

export class Interaction extends Tool {
    // Manages node searching and
    constructor(state) {
        super(state)

        // internal state
        this.search_type;  // NODE or EDGE
        this.searched_nodes = new Set()      // Set of current nodes selected by the search query
        this.suggested_nodes = new Set()     // Set of current nodes suggested by the search query
        this.searched_edges = new Set()      // Set of current edges selected by the search query
        this.suggested_edges = new Set()     // Set of current edges suggested by the search query
        this.node_query = false  // whether terms are in the node query
        this.edge_query = false  // whether terms are in the edge query

        this.hovered_node = null             // Node: current hovered node
        this.selected_nodes = [];            // first and second selected nodes
        this.selected_edges = new Set()      // set of current edges selected by user
        this.selected_neighbors = new Set()  // Set {Node}: current neighboring nodes of the selected node

        // nodes which aren't searched, suggested, or selected, but need to remain visible because the edges connecting them
        //  are selected (like from the shortest path node search)
        this.intermediate_nodes = new Set()

        this.dragged_node = null;  // node currently being dragged
        this.is_dragging = false;  // whether

        // zoom
        this.settings.animated_zoom_duration = 300  // only in effect for animated zooming
        this.settings.animated_zoom_ratio = 2  // ratio when animating zoom transition
        this.settings.animated_zoom_fps = 30
        this.settings.instant_zoom_ratio = 1.2  // ratio when zooming instantly
        this.zoom_animation_id = null

        // initial bbox state
        this.home_bbox


        // jQuery elements
        this.$search_input = $("#search-input");  // search input element
        this.$search_type_button = $("#search-type");   // search type button
        this.$home_button = $("div.interface button#home")  // home button
        this.$error = $("div#error")  // error div

        // init all search functions
        this.state.interaction = this
        this.init()
    }

    // get and display suggestions based on the current search query (or clear current search query)
    search_nodes() {
        let query = this.$search_input.val().toLowerCase()
        if (!query) {  // If the query is empty, reset the searched_node and suggestions
            this.searched_nodes.clear()
            this.suggested_nodes.clear()
            this.node_query = false
            return
        }
        this.node_query = true

        let searched_nodes = []  // nodes to search
        let suggested_nodes = []  // nodes to suggest

        let queries = query.split(',')  // all node searches
        for (let i=0; i<queries.length; i++) {
            let term = queries[i]

            // Populate matches with nodes and associated labels that contain the query (not case sensitive)
            //var search_pool = this.graph.nodes().filter((node) => {
            //    return !this.is_tree_node(node)  // TODO: Right now, just ignore tree nodes. Maybe later add ability to search tree nodes.
            //})
            var matches = this.graph.nodes().map((key) => {
                    return {key: key, label: this.graph.getNodeAttribute(key, "label")}
                }).filter(node => (node.label||'').toLowerCase().includes(term));

            var exact_matches = matches.filter(node => node.label.toLowerCase() == term)

            if (matches.length == 1) {  // only 1 match - add it
                searched_nodes.push(matches[0].key)
                suggested_nodes.push(matches[0].key)
                if (i == queries.length-1) {  // last query
                    this.centerNode(matches[0].key)  // center the camera on it
                }
            } else {  // zero or more than one match - add exact matches
                if (i == queries.length-1) {  // last query - add all matches
                    suggested_nodes = suggested_nodes.concat(matches.map(node => node.key))
                } else {  // not last query - add only exact matches
                    searched_nodes = searched_nodes.concat(exact_matches.map(node => node.key))
                    suggested_nodes = suggested_nodes.concat(exact_matches.map(node => node.key))
                }
            }
        }

        // if exactly 2 nodes searched, display shortest path
        if (searched_nodes.length == 2 && suggested_nodes.length == 2) {
            this.get_shortest_path(searched_nodes[0], searched_nodes[1])
        } else {
            this.clear_shortest_path()
        }

        // set global state
        this.searched_nodes = new Set(searched_nodes)
        this.suggested_nodes = new Set(suggested_nodes)
        this.sigma.refresh();  // Refresh rendering
    }
    search_edges() {
        let query = this.$search_input.val().toLowerCase()
        if (!query) {  // If the query is empty, reset the searched_node and suggestions
            this.searched_edges.clear()
            this.suggested_edges.clear()
            this.edge_query = false
            return
        }
        this.edge_query = true

        let searched_edges = []  // edges to search
        let suggested_edges = []  // edges to suggest

        let queries = query.split(',')  // all node searches
        for (let i=0; i<queries.length; i++) {
            let term = queries[i]

            // Populate matches with edges and associated labels that contain the query (not case sensitive)
            var matches = this.graph.edges().map((key) => {
                    return {key: key, label: this.graph.getEdgeAttribute(key, "label")}
                }).filter(edge => (edge.label||'').toLowerCase().includes(term));

            suggested_edges = suggested_edges.concat(matches.map(edge => edge.key))  // add matching edges to the suggestion'
            if (matches.length == 1) {  // if exactly 1 match
                searched_edges.push(matches[0].key)
                if (i == queries.length-1) {  // last term
                }
            }
        }

        // set global state
        this.searched_edges = new Set(searched_edges)
        this.suggested_edges = new Set(suggested_edges)
        this.sigma.refresh();  // Refresh rendering

    }
    search_clear() {
        this.$search_input.val("")        // clear the search bar
        this.searched_nodes.clear()
        this.suggested_nodes.clear()
        this.node_query = false
        this.searched_edges.clear()
        this.suggested_edges.clear()
        this.edge_query = false
        this.sigma.refresh()
    }

    // display shortest path between two nodes
    get_shortest_path(node1, node2) {
        let node_path = shortestPath(this.graph, node1, node2)
        if (node_path != null) {  // shortest path exists
            this.intermediate_nodes = new Set(node_path)  // mark these nodes as being used as part of the shortest path
            let edge_path = []
            for (let i=1; i<node_path.length; i++) {   // construct list of edges in this path
                let edges = this.graph.edges(node_path[i-1], node_path[i])
                edge_path.push(edges[0])  // just pick the first edge
            }
            this.selected_edges = new Set(edge_path)
            return true
        } else {  // no shortest path exists
            this.clear_shortest_path()
        }
        return false
    }
    clear_shortest_path() {
        this.selected_edges.clear()
        this.intermediate_nodes.clear()
    }

    // resets bounding box and camera
    reset_camera() {
        this.sigma.getCamera().animatedReset()  // reset camera (100 ms duration)
        this.animate_bbox(this.sigma.getCustomBBox(), this.home_bbox, 100)
    }

    // set the given node as the currently hovered node (or unset the currently hovered node)
    hoverNode(node) {
        if (node) {
            this.hovered_node = node;
        } else {  // no node given - unset
            this.hovered_node = undefined;
        }
        this.sigma.refresh();   // Refresh rendering
    }

    // set the given node as the currently selected node (or unset the currently selected node)
    selectNode(node) {
        if (node) {  // if a node was given
            this.selected_nodes.unshift(node);  // select new node
            this.selected_nodes = this.selected_nodes.slice(0,2)  // keep last two nodes
            this.selected_neighbors = new Set(this.graph.neighbors(node));  // set neighbors

            // if exactly 2 nodes selected
            if (this.selected_nodes.length == 2) {
                let [node_1, node_2] = this.selected_nodes
                // select connecting edges that are visible
                this.selected_edges = new Set(this.graph.edges(node_1, node_2).filter(edge => !this.is_edge_hidden(edge)))
                let p1 = {x: this.sigma.nodeDataCache[node_1].x, y: this.sigma.nodeDataCache[node_1].y}  // node 1 coords
                let p2 = {x: this.sigma.nodeDataCache[node_2].x, y: this.sigma.nodeDataCache[node_2].y}  // node 2 coords
                let mid = {x: (p1.x+p2.x)/2, y: (p1.y+p2.y)/2}  // mid-point
                let {x, y} = this.sigma.framedGraphToViewport(mid)  // convert to viewport coords for display

                if (this.selected_edges.size != 0) {  // if connecting edges exist
                    this.show_menu(EDGE, this.selected_edges.values(), x, y)
                } else {  // no connecting edges - get shortest path
                    if (!this.get_shortest_path(this.selected_nodes[0], this.selected_nodes[1]))  // if no shortest path
                        this.selected_nodes = this.selected_nodes.slice(0,1)  // keep only newest node
                }
            } else {
                this.clear_shortest_path()
            }
        } else {  // no node given
            this.selected_nodes = [];  // unset currently selected nodes
            this.selected_neighbors.clear();  // unset neighbors
            this.clear_shortest_path()
        }  // if no node is given, and no node is selected, do nothing
        this.sigma.refresh();   // Refresh rendering
    }

    // set the given node as the currently dragged node
    dragNode(node) {
        if (node) {
            this.dragged_node = node;
            this.is_dragging = true;
            this.sigma.getCamera().disable();  // disable camera so it doesn't follow the mouse
            //if (!this.sigma.getCustomBBox())  // lock current bounding box, disabling auto-scaling.
                //this.sigma.setCustomBBox(this.sigma.getBBox());

        } else {  // no node given - unset everything
            this.dragged_node = null;
            this.is_dragging = false;
            this.sigma.getCamera().enable();  // re-enable camera movement
        }
        this.sigma.refresh();   // Refresh rendering
    }

    // move camera to center view on this node
    centerNode(node) {
        var coords = this.sigma.getNodeDisplayData(node);  // get node coords
        this.sigma.getCamera().animate(coords, {duration: 500});  // Move camera to center on the node
    }

    // check if node is able to be interacted with
    is_interactive(node) {
        if (this.is_node_hidden(node) || this.is_node_obscured(node)) {
            return false
        }
        return true;
    }

    // populate right-click menu with node/edge properties at the given mouse position
    // keys is a list of node/edge keys to display
    show_menu(type, keys, x, y) {
        // whether node or edge, use corresponding methods
        // data_cache return the node/edge sigma data cache
        // get_attributes returns node/edge attributes
        // new_label returns the label of a node/edge if it isn't defined
        if (type === EDGE) {  // edge
            var data_cache = this.sigma.edgeDataCache
            var get_attributes = key => this.graph.getEdgeAttributes(key)
            var get_label = key => {
                let label = get_attributes(key).label
                if (label === undefined) {  // if not defined, return "node1 <-> node2"
                    let nodes = this.graph.extremities(key)
                    label = this.graph.getNodeAttribute(nodes[0],'label') + "<->" + this.graph.getNodeAttribute(nodes[1], 'label')
                }
                return label
            }
        } else {  // node
            var data_cache = this.sigma.nodeDataCache
            var get_attributes = key => this.graph.getNodeAttributes(key)
            var get_label = key => {
                let label = get_attributes(key).label
                if (label === undefined) label = key  // if not defined, return node key
                return label
            }
        }

        let $menu = $("<div id='data-menu'></div>")  // menu div
        let $menu_buttons = $("<div id='tab-buttons'></div>").appendTo($menu)  // menu tab buttons
        if (typeof keys === 'string') keys = [keys]  // if just one key, convert to single item in list

        let $first = null
        for (let key of keys) {  // for each key given
            let show_empty = false
            let attributes = null
            let class_key = "key-"+key.replace(/\s/g, '__')  // replace spaces in key // TODO need to maintain uniqueness

            if (this.settings["advanced_data"]) {  // if advanced data settings option is on
                attributes = data_cache[key]  // includes visual attributes as well
            } else {  // if not
                attributes = get_attributes(key)["data"]  // custom data attributes only
            }

            let label = get_label(key)  // node/edge display label
            let $menu_tab = $(`<div class='tab ${class_key}'></div>`).appendTo($menu)  // label menu tab with classes "tab" and "key-<keystring>"
            let $tab_button = $(`<button class='button ${class_key}'>${label}</button>`).appendTo($menu_buttons)  // label tab button with classes "button" and "key-<keystring>"
            $tab_button.on('click', (event) => this.select_menu_tab(event, class_key))  // bind click event
            if ($first === null) $first = $tab_button  // this was the first button added

            this.generate_data_menu_html($menu_tab, attributes)  // add html for all attribute data
        }

        $menu.appendTo("body").css({left: x + "px", top: y + "px"});  // finally append whole menu div to main body at given position
        $first.trigger('click')  // click the first button added
    }
    select_menu_tab(event, class_key) {
        // when a node/edge menu tab is clicked
        let selector = CSS.escape(class_key)  // selector for this class name

        // hide all menu tabs
        let $tabs = $("div#data-menu div.tab");
        for (let tab of $tabs) {
            $(tab).hide()
        }
        // unhide the selected menu tab
        $(`div#data-menu div.tab.${selector}`).show()

        // remove active class from all tab buttons
        let $buttons = $("div#data-menu div#tab-buttons button");
        for (let button of $buttons) {
            $(button).removeClass("active")
        }
        // add active class to selected tab button
        $(`div#data-menu div#tab-buttons button.${selector}`).addClass("active")
    }
    generate_data_menu_html($parent_element, attributes) {
        // recursively generate html for the object structure, given a parent jQuery element
        let $element = $(`<div class='menu-section'></div>`)
        let objects = {}  // objects to be recursively displayed

        // if attributes exist
        if (attributes !== undefined && Object.keys(attributes).length > 0) {
            for (let [key, val] of Object.entries(attributes)) {  // for each attribute
                if (typeof val === 'object' && val !== null) {
                    objects[key] = val
                } else {  // display normally
                    $(`<div><span>${key}:</span><span>${val}</span></div>`).appendTo($element)
                }
            }
            // now display the object (after all normal properties)
            for (let [key, val] of Object.entries(objects)) {
                $(`<div><span>${key}:</span></div>`).appendTo($element)
                this.generate_data_menu_html($element, val)  // generate sub object html recursively
            }
        } else {  // no attributes
            $("<div><span>No data</span></div>").appendTo($element).css({'font-style': 'italic', 'color':'grey'})
        }
        // add this element to its parent
        $element.appendTo($parent_element)
    }
    clear_data_menus() {
        // remove any node/edge data menus on the screen
        $("div#data-menu").remove();  // remove current node menu if open
    }

    //
    // Camera stuff
    //
    zoom(direction, x, y) {
        let camera = this.sigma.getCamera();
        let ratioDiff = direction > 0 ? 1/this.settings.animated_zoom_ratio : this.settings.animated_zoom_ratio
        let new_ratio = camera.getState().ratio * ratioDiff;
        camera.animate(
            this.sigma.getViewportZoomedState({x:x, y:y}, new_ratio),
                {easing: "quadraticOut", duration: this.settings.animated_zoom_duration},
                () => {
                    this.currentWheelDirection = 0;
                },
        );
    }
    zoomBBox(direction, x, y) {
        let zoom_ratio = this.settings.animate_zoom ? this.settings.animated_zoom_ratio : this.settings.instant_zoom_ratio

        // calculate new bbox
        let {x:mouse_x, y:mouse_y} = this.sigma.viewportToGraph({x:x, y:y});  // convert mouse to graph coords
        let ratio = direction > 0 ? 1/zoom_ratio : zoom_ratio;  // zoom ratio
        let cur = this.sigma.getCustomBBox() || this.sigma.getBBox()  // current BBox in graph coords

        // get current center point in graph coords
        var center_x = (cur.x[1]+cur.x[0]) / 2;
        var center_y = (cur.y[1]+cur.y[0]) / 2;

        // get new center position while preserving mouse position
        center_x += (mouse_x - center_x) * (1 - ratio)
        center_y += (mouse_y - center_y) * (1 - ratio)

        // scale BBox height and width according to zoom ratio
        let width = ratio*(cur.x[1]-cur.x[0]);
        let height = ratio*(cur.y[1]-cur.y[0]);

        // calculate new BBox edges
        let x_extent =  [center_x - width/2, center_x + width/2]
        let y_extent = [center_y - height/2, center_y + height/2]
        let target = {x: x_extent, y: y_extent}

        // change bbox
        if (this.settings.animate_zoom) {  // animate it
            this.animate_bbox(cur, target, this.settings.animated_zoom_duration)
        } else {
            this.sigma.setCustomBBox(target)
            this.sigma.refresh()
        }
    }
    bbox_easing(t) {
        return t * (2-t);
    }
    animate_bbox(initial, target, duration) {
        let now = window.performance.now()
        this.startTime = now;  // initialize
        this.then = now
        this._animate_bbox(initial, target, now, duration)
    }
    _animate_bbox(initial, target, timestamp, duration) {
        // loop bbox zoom animation for a duration
        let now = timestamp;
        let frame_elapsed = now - this.then  // time elapsed since last frame
        let total_elapsed = now - this.startTime  // total time elapsed since start
        // if elapsed time is less than duration, set up the next animation
        if (total_elapsed < duration) {
            this.zoom_animation_id = window.requestAnimationFrame((timestamp) => this._animate_bbox(initial, target, timestamp, duration));
        } else {
            this.zoom_animation_id = null
        }

        // if enough time has elapsed since last frame, calculate next frame
        if (frame_elapsed > 1000/this.settings.animated_zoom_fps) {
            // Get ready for next frame by setting then = now
            // Also, adjust for fps interval not being multiple of RAF's interval
            this.then = now - (frame_elapsed % 1000/this.settings.animated_zoom_fps);
            let t = (now - this.startTime) / duration

            let frame_bbox = {}
            let coefficient = this.bbox_easing(t)
            frame_bbox.x = [initial.x[0] + (target.x[0] - initial.x[0]) * coefficient, initial.x[1] + (target.x[1] - initial.x[1]) * coefficient]
            frame_bbox.y = [initial.y[0] + (target.y[0] - initial.y[0]) * coefficient, initial.y[1] + (target.y[1] - initial.y[1]) * coefficient]
            this.sigma.setCustomBBox(frame_bbox)
            this.sigma.refresh()
        }
    }


    // show an alert with the given error and message
    error(error, message) {
        this.$error.show()
        this.$error.find("p#name").html("Error: "+error)
        this.$error.find("p#message").html(message)
    }

    //
    // reducers
    //

    // node reducer for rendering temporary states
    node_reducer(node, attrs) {  // return temporary node properties
        // If node is selected or searched, highlight it
        if (this.selected_nodes.includes(node) || this.searched_nodes.has(node)) {
            this.highlight(attrs)
        }
        // If any nodes are selected, all non-adjacent nodes are unfocused (unless also selected or intermediate)
        if (this.selected_neighbors.size != 0 && !this.selected_neighbors.has(node) && !this.selected_nodes.includes(node) && !this.intermediate_nodes.has(node)) {
            this.unfocus(attrs)
        }

        // if any EDGE is selected
        if (this.selected_edges.size != 0) {
            // unfocus nodes not connected to any selected edges
            if (!this.graph.edges(node).some(edge => this.selected_edges.has(edge))) {
                this.unfocus(attrs)
            }
        }

        // If nodes are being queried, all non searched/suggested nodes are unfocused
        if (this.node_query && (!this.suggested_nodes.has(node) && !this.searched_nodes.has(node))) {
            this.unfocus(attrs)
        }

        // if EDGES are being queried
        if (this.edge_query) {
            // unfocus nodes not connected to any suggested edge
            if (!this.graph.edges(node).some(edge => this.suggested_edges.has(edge))) {
                this.unfocus(attrs)}
        }

        // if node is being dragged, disallow it from being otherwise moved
        if (this.dragged_node && this.dragged_node == node) {
            this.fix(attrs)
        }

        // depending on settings, hide out-of-focus nodes instead of unfocusing them
        // note that this still does not hide intermediate nodes, which may be out-of-focus but must remain visible.
        if (!this.settings.show_unfocused_nodes && this.is_unfocused(attrs) && !this.intermediate_nodes.has(node)) {
            this.hide(attrs)
        }

        return attrs;
    };

    // edge reducer for rendering temporary states
    edge_reducer(edge, attrs) {  // return temporary edge properties
        // if there are selected edges, unfocus all others
        if (this.selected_edges.size != 0 && !this.selected_edges.has(edge)) {
            this.unfocus(attrs)
        }

        // if a node has been selected, hide non-selected edges not connected to either node
        if (this.selected_nodes.length != 0) {
            let [first, second] = this.selected_nodes
            if (first && !this.selected_edges.has(edge) && (!this.graph.hasExtremity(edge,first) && !this.graph.hasExtremity(edge,second))) {
                this.hide(attrs)
            }
        }

        // If there are NODES being queried
        if (this.node_query) {
            // hide non-searched and non-selected edges that don't connect two NODE suggestions
            if (!this.searched_edges.has(edge) && !this.selected_edges.has(edge) && (!this.suggested_nodes.has(this.graph.source(edge)) || !this.suggested_nodes.has(this.graph.target(edge)))) {
                this.hide(attrs)}
        }

        // If there are EDGES being queried
        if (this.edge_query) {
            if (!this.suggested_edges.has(edge)) {  // non suggested edges are hidden
                this.hide(attrs)
            }
        }

        return attrs;
    }

    init() {
        // NOTE: This jQuery line is aesthetic and not necessary.
        // It populates the datalist associated with the search bar input with all the labels of each node on the graph.
        // The datalist will search suggestions, and clicking on a suggestion will auto-complete the query.
        // The problem is that if the implemented custom search method for the nodes changes (in this.search()),
        //      then this datalist dropdown will not reflect the same set of searched nodes. This is because
        //      the datalist has it's own native search method.
        // The reason I have a separate object (this.suggestions) to do searching is because I need somewhere to store
        //      the Node objects associated with each label in order to access their properties, and also to implement
        //      possible custom search methods in the future.
        // I would much rather have a single object that both contains the nodes, and also displays their
        //      associated labels in the datalist dropdown. As it is, I have settled with just removing
        //      the datalist dropdown suggestions for the time being. It's functional, just not future-proof.
        //
        //$("#suggestions")[0].innerHTML = this.graph.nodes().map((node) => `<option value="${this.graph.getNodeAttribute(node, "label")}"></option>`).join("\n");

        $(document).contextmenu(function() {  // disable default right-click menu
            return false;
        });

        //
        // Search Bar
        //

        // set search query for each character typed into search bar
        this.$search_input.on('input', () => {
            this.selectNode();  // unset any selected nodes
            if (this.search_type === NODE) {
                this.search_nodes()
            } else {
                this.search_edges()
            }
        });

        // reset search on loss of focus?
        this.$search_input.blur(() => {
            //this.search_clear()
        });
        // defaults
        this.search_type = NODE
        this.$search_type_button.html("Nodes")
        this.$search_input.prop('placeholder', NODE_EX)
        // set search type button to toggle
        this.$search_type_button.on("click", () => {
            this.search_clear()
            if (this.search_type === NODE) {
                this.$search_type_button.html("Edges")
                this.$search_input.prop('placeholder', EDGE_EX)
                this.search_type = EDGE
            } else {
                this.$search_input.prop('placeholder', NODE_EX)
                this.$search_type_button.html("Nodes")
                this.search_type = NODE
            }
        });

        //
        // interface buttons
        //
        this.$home_button.on('click', () => this.reset_camera())

        //
        //  Mouse Interactions
        //
        /*
        this.sigma.on("enterNode", (event) => {  // mouse enters a node
            if (!this.is_interactive(event.node)) return;
            this.hoverNode(event.node);  // set hovered node
        });

        this.sigma.on("leaveNode", (event) => {  // mouse leaves a node
            this.hoverNode();  // unset hovered node
        });
        */

        this.sigma.on("downNode", (event) => {  // holding mouse down on a node
            if (!this.is_interactive(event.node)) return;
            this.dragNode(event.node);    // start dragging
        });

        this.sigma.on("clickNode", (event) => {  // full left click on node
            if (!this.is_interactive(event.node)) return;
            this.selectNode(event.node);  // select node
        })

        this.sigma.on("clickStage", (event) => {  // left click off a node
            this.selectNode()  // unset selected node
            this.search_clear()  // clear search query
        })

        // TODO: if visible nodes can't be clicked anymore, this check for hidden isn't necessary
        this.sigma.on("rightClickNode", (event) => {  // full right click on a node
            // Can't right click only if hidden.
            // Can still right click even if not interactive.
            if (this.is_node_hidden(event.node)) return;
            this.show_menu(NODE, event.node, event.event.x, event.event.y)
        })

        this.sigma.on("clickEdge", (event) => {
            // does nothing at the moment
        })

        this.sigma.on("rightClickEdge", (event) => {
            if (this.is_edge_hidden(event.edge)) return;
            this.show_menu(EDGE, event.edge, event.event.x, event.event.y)
        })

        this.sigma.getMouseCaptor().on("mousedown", () => {  // On down-click (left or right) anywhere
            this.clear_data_menus()
        });

        this.sigma.getMouseCaptor().on("mouseup", () => {  // When releasing click
            this.dragNode()  // stop dragging
        });

        this.sigma.getMouseCaptor().on("mousemove", (event) => {  // When moving mouse
            if (!this.is_dragging || !this.dragged_node)  // if not dragging a node, return
                return;
            const pos = this.sigma.viewportToGraph(event);  // Get mouse position
            this.graph.setNodeAttribute(this.dragged_node, "x", pos.x);  // set node x
            this.graph.setNodeAttribute(this.dragged_node, "y", pos.y);  // set node y
        });

        this.sigma.getMouseCaptor().on("doubleClick", (event) => {
            event.preventSigmaDefault()  // prevent default zoom action on double click
        })
        this.sigma.on("doubleClickNode", (event) => {
            this.state.tree.open_node(event.node)  // open node on double click
            this.selectNode()  // deselect node from single click
        })

        this.sigma.getMouseCaptor().on("wheel",  (event) => {
            event.preventSigmaDefault()  // prevent default zooming
            var wheelDirection = event.deltaY > 0 ? 1 : -1

            // if ctrl is held, do regular sigma zoom
            if (window.event.ctrlKey) {  // set current viewed tree depth
                // Cancel events that are too close too each other (plus some padding)
                const now = Date.now();
                if (
                    this.lastWheelTriggerTime &&
                    now - this.lastWheelTriggerTime < (this.settings.animated_zoom_duration)
                ) {
                    return;
                }
                this.currentWheelDirection = wheelDirection;
                this.lastWheelTriggerTime = now;
                this.zoom(wheelDirection, event.clientX, event.clientY)
            } else if (this.zoom_animation_id === null) {  // otherwise zoom bbox if not currently doing so
                this.zoomBBox(wheelDirection, event.clientX, event.clientY)
            }

        });


        $("body").on('keypress', (event) => {
            let recent_select = this.selected_nodes[0]
            if (event.keyCode == 43) {  // + key
                if (!recent_select) return;
                this.state.tree.open_node(recent_select)
            } else if (event.keyCode == 45 || event.keyCode == 61) {  // - key
                if (!recent_select) return;
                this.state.tree.close_node(recent_select)
            }
        })
    }

    init_graph() {

    }

}

