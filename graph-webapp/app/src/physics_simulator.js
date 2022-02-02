import {Tool} from "./tool.js"
import * as utils from "./utils.js"
import "./lib/forceatlas2.min.js"
import "./lib/forceatlas2_worker.min.js"

const DEFAULTS = {
    attraction: 0.02,  // 0.02
    repulsion: 150,    // 150
    drag: 2,  // 2
    drag_threshold: 0.01,  // speed at which nodes stop moving  0.01
    gravity: 0.01,  // 0.001
    max_speed: 100,  // 100
};

export class Simulator extends Tool {
    // Manages physics of springy graph
    constructor(state) {
        super(state)

        // use default settings if any aren't given
        this.settings = Object.assign(DEFAULTS, this.settings);

        this.node_states = {};
        this.running = false;

        // factor why which to scale calculated node distances based on cluster depth
        this.scale = function(depth) {
            return Math.pow(8, depth)
        }

        this.FA_worker;
        this.FA_frame_iterations = 1;  // number of iterations per animation frame
        this.FA_snap_iterations = 50;  // number of iterations for the organize button
        this.FA_optimize_threshold = 500 // at what graph order to use Barnes Hut Optimization (nlog(n))
        this.FA_settings = {  // default settings for ForceAtlas2
            adjustSizes: false,  // has weird side effect of close nodes piggybacking continuously. Uses degree???
            barnesHutOptimize: false,  // opt: if order > 2000
            barnesHutTheta: 0.5,  // opt: 0.5
            edgeWeightInfluence: 0,
            gravity: 1,  // opt: 0.05
            strongGravityMode: true,  // opt: true
            linLogMode: false,
            outboundAttractionDistribution: false,  // seems to cause more clustering of leaf nodes?
            scalingRatio:1,  // opt: 10
            slowDown: 10  // opt: 1 + Math.log(order)

        }

        this.fps = 30;  // maximum physics animation fps
        this.startTime;
        this.now;
        this.then;
        this.elapsed;
        this.frameCount=0;

        // jquery elements
        this.$toggle_button = $("button#physics");
        this.$start_label = $("button#physics span img.start-label");
        this.$stop_label = $("button#physics span img.stop-label");
        this.$organize_button = $("button#organize");

        this.x_key = 'x'
        this.y_key = 'y'
        this.init();
    }

    iterate_FA2(iterations) {
        for (let branch of this.state.tree.get_open_branches()) {  // for each open cluster of nodes
            this.simulate_cluster(branch, iterations)
        }
    }
    simulate_cluster(branch, iterations) {
        let cluster = this.state.tree.get_cluster_info(branch)  // get sub graph for this cluster

        //cluster.local_to_global()  // update global position from local sub-graph position (keeps sub-graph relative to parent)
        // TODO: This line appears to do two things:
        //  1: Makes child nodes follow their parent immediately rather than sluggishly (good)
        //  2: Makes zooming in while physics is active sometimes jitter (because this func is used in snap(), i think) (bad)
        cluster.global_to_local()  // update local sub-graph position from global position (nodes may have been moved in the global graph by other means)

        this.simulate(cluster.graph, iterations, true)  // simaulate and assign positions to graph

        // set global positions from new local positions
        cluster.local_to_global()
    }
    simulate(graph, iterations, assign=false) {
        // run forceatlas on a given graph
        let settings = this.FA_settings
        settings.barnesHutOptimize = graph.order > this.FA_optimize_threshold

        // calculate next positions for this sub graph
        if (assign) {
            FA2.assign(graph, {
                iterations: iterations,
                settings: settings
            });
        } else {
            let positions = FA2(graph, {
                iterations: iterations,
                settings: settings
            });
            return positions
        }
    }
    get_global_node_positions() {
        // update cluster local position from global position
        // needed to be called once before physics starts to account for any position changes
        for (let branch of this.state.tree.get_open_branches()) {  // for each open cluster of nodes
            let cluster = this.state.tree.get_cluster_info(branch)  // get sub graph for this cluster
            cluster.global_to_local()
        }
    }

    // Snap graph to optimal position
    snap() {
        this.iterate_FA2(this.FA_snap_iterations)
    }

    animate(duration) {
        this.now = window.performance.now()
        this.startTime = this.now;  // initialize
        this.then = this.now  // initialize
        this.frameCount = 0
        if (duration === undefined) {  // if no duration given, just keep going
            duration = Infinity
        }
        this._animate(this.now, duration)
    }
    _animate(timestamp, duration) {  // loop continuously
        this.now = timestamp;
        let frame_elapsed = this.now - this.then  // time elapsed since last frame
        let total_elapsed = this.now - this.startTime  // total time elapsed since start

        // if elapsed time is less than duration, set up the next animation
        if (total_elapsed < duration) {
            this.frameID = window.requestAnimationFrame((timestamp) => this._animate(timestamp, duration));
        }

        // if enough time has elapsed since last frame, calculate next frame
        if (frame_elapsed > 1000/this.fps) {
            // Get ready for next frame by setting then = now
            // Also, adjust for fps interval not being multiple of RAF's interval
            this.then = this.now - (frame_elapsed % 1000/this.fps);

            // calculate next frame
            //this.iterate_physics()
            this.iterate_FA2(this.FA_frame_iterations)

            // TESTING...Report #seconds since start and achieved fps.
            //var sinceStart = this.now - this.startTime;
            //var currentFps = Math.round(1000 / (sinceStart / ++this.frameCount) * 100) / 100;
            //console.log("Elapsed time= " + Math.round(sinceStart / 1000 * 100) / 100 + " secs @ " + currentFps + " fps.");
        }
    }

    init() {
        // make physics button toggle simulation
        this.$toggle_button.on("click", () => {
            if (this.running) {
                this.stop();
            } else if (this.graph !== undefined) {
                this.start();
            } else {  // no graph loaded
                console.log("Can't start physics engine - no graph loaded")
            }
        });

        // make organize button send placement request to backend
        this.$organize_button.on("click", () => {
            this.snap()
        })
    }

    init_graph() {
        // set state variable for external access
        this.state.simulation = this

        // initialize forceAtlas2 worker
        //Object.assign(this.FA_settings, FA2.inferSettings(this.graph))
        this.FA_worker = new FA2Layout(this.graph, {settings: this.FA_settings});
    }

    // Start / Stop physics animation
    start() {  // start animation loop
        if (this.running)
            return;

        this.get_global_node_positions()  // set current node positions - they may have changed when physics was off
        this.$start_label.toggle()
        this.$stop_label.toggle()
        this.animate()
        this.running = true;
    }
    stop() {  // cancel animation if running
        if (!this.running)
            return;
        if (typeof this.frameID === "number") {
            window.cancelAnimationFrame(this.frameID);
            this.frameID = undefined;
            this.$start_label.toggle()
            this.$stop_label.toggle()
        }
        this.running = false;
    }

    // Start/Stop FA2 webworker - currently not used. Would replace regular start/stop methods.
    start_worker() {
        this.FA_worker.start()
        this.running = true
        this.$start_label.toggle()
        this.$stop_label.toggle()
    }
    stop_worker() {
        this.FA_worker.stop()
        this.running = false
        this.$start_label.toggle()
        this.$stop_label.toggle()
    }
}
