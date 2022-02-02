import {animateNodes} from "sigma/utils/animate";
import FA2Layout from "graphology-layout-forceatlas2/work2er";
import forceAtlas2 from "graphology-layout-forceatlas2";

export function set_layouts() {
    // Retrieve some useful DOM elements:
    const container = document.getElementById("sigma-container");
    const FA2Button = document.getElementById("forceatlas2");
    const FA2StopLabel = document.getElementById("forceatlas2-stop-label");
    const FA2StartLabel = document.getElementById("forceatlas2-start-label");
    const randomButton = document.getElementById("random");
    const circularButton = document.getElementById("circular");

    /*** FA2 LAYOUT ***/
    /** This example shows how to use the force atlas 2 layout in a web worker */
    // Graphology provides a easy to use implementation of Force Atlas 2 in a web worker
    const sensibleSettings = forceAtlas2.inferSettings(graph);
    const fa2Layout = new FA2Layout(graph, {
        settings: sensibleSettings,
    });
    // A button to trigger the layout start/stop actions
    // A variable is used to toggle state between start and stop
    let FA2isRunning = false;
    let cancelCurrentAnimation = null;
    // correlate start/stop actions with state management
    function stopFA2() {
        fa2Layout.stop();
        FA2StartLabel.style.display = "flex";
        FA2StopLabel.style.display = "none";
        FA2isRunning = false;
    }
    function startFA2() {
        if (cancelCurrentAnimation)
            cancelCurrentAnimation();
        fa2Layout.start();
        FA2StartLabel.style.display = "none";
        FA2StopLabel.style.display = "flex";
        FA2isRunning = true;
    }
    // the main toggle function
    function toggleFA2Layout() {
        if (FA2isRunning) {
            stopFA2();
        }
        else {
            startFA2();
        }
    }
    // bind method to the forceatlas2 button
    FA2Button.addEventListener("click", toggleFA2Layout);
    /*** RANDOM LAYOUT ***/
    /** Layout can be handled manually by setting nodes x and y attributes */
    /** This random layout has been coded to show how to manipulate positions directly in the graph instance */
    /** Alternatively a random layout algo exists in graphology: https://github.com/graphology/graphology-layout#random  */
    function randomLayout() {
        // stop fa2 if running
        if (FA2isRunning)
            stopFA2();
        if (cancelCurrentAnimation)
            cancelCurrentAnimation();
        // to keep positions scale uniform between layouts, we first calculate positions extents
        const xExtents = { min: 0, max: 0 };
        const yExtents = { min: 0, max: 0 };
        graph.forEachNode((node, attributes) => {
            xExtents.min = Math.min(attributes.x, xExtents.min);
            xExtents.max = Math.max(attributes.x, xExtents.max);
            yExtents.min = Math.min(attributes.y, yExtents.min);
            yExtents.max = Math.max(attributes.y, yExtents.max);
        });
        const randomPositions = {};
        graph.forEachNode((node) => {
            // create random positions respecting position extents
            randomPositions[node] = {
                x: Math.random() * (xExtents.max - xExtents.min),
                y: Math.random() * (yExtents.max - yExtents.min),
            };
        });
        // use sigma animation to update new positions
        cancelCurrentAnimation = animateNodes(graph, randomPositions, { duration: 2000 });
    }
    // bind method to the random button
    randomButton.addEventListener("click", randomLayout);
    /*** CIRCULAR LAYOUT ***/
    /** This example shows how to use an existing deterministic graphology layout */
    function circularLayout() {
        // stop fa2 if running
        if (FA2isRunning)
            stopFA2();
        if (cancelCurrentAnimation)
            cancelCurrentAnimation();
        //since we want to use animations we need to process positions before applying them through animateNodes
        const circularPositions = circular(graph, { scale: 100 });
        //In other context, it's possible to apply the position directly we : circular.assign(graph, {scale:100})
        cancelCurrentAnimation = animateNodes(graph, circularPositions, { duration: 2000, easing: "linear" });
    }
    // bind method to the random button
    circularButton.addEventListener("click", circularLayout);

}