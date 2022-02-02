import {Tool} from "./tool.js"

export class Menu extends Tool{
    // Manages menu interface
    constructor(state) {
        super(state)

        // internal state
        this.showing = false  // whether the menu is being shown

        // jQuery elements
        this.$menu_button = $("#settings-menu-button");
        this.$menu = $("#settings-menu")

        this.$help_button = $("button#help-button")
        this.$help = $("div#help-container")

        // init menu items
        this.init()
    }

    create_menu() {
        this.add_checkbox('Show un-selected nodes', 'show_unfocused_nodes', true, "When a node is selected, other nodes not directly connected to it will be visible but slightly desaturated.")
        this.add_checkbox('Show out-of-range nodes', 'show_out_of_range_nodes', false, "When nodes are removed by a filter, keep them faintly visible.")
        this.add_checkbox('Advanced data menu', 'advanced_data', false, "In the right-click menu, show all attributes of the node or edge. Mostly for debugging purposes.")
        this.add_checkbox('Smooth zooming', 'animate_zoom', true, "Enables smooth zooming transitions.")

    }

    show_menu() {
        this.$menu.toggle()
        this.showing = this.showing ? false : true
    }

    // add a boolean setting with a checkbox to the settings menu
    add_checkbox(label, setting, default_value, description) {
        let $setting = $(`<div class='setting'></div>`).appendTo(this.$menu)  // wrapping div
        let $checkbox = $(`<input type='checkbox' id='${setting}'></input>`).appendTo($setting)  // checkbox input
        let $label = $(`<label for='${setting}'>${label}</label>`).appendTo($setting)  // label for checkbox
        this.add_tooltip(description, $label)

        if (this.settings[setting] === undefined) {  // this setting hasn't been given
            this.settings[setting] = default_value
        }

        $checkbox[0].checked = this.settings[setting]  // initial value
        $checkbox.on('change', (event) => {
            this.settings[setting] = $checkbox[0].checked
            this.sigma.refresh()  // re-render everything
        })


    }

    // add a tooltip to the given element
    add_tooltip(text, $element) {
        let $tooltip = $(`<span class='tooltip' style="display:none">${text}</span>`).appendTo($element)  // tooltip for label
        $element.hover(
            (event) => {  // enter event
                $tooltip.show()
            },
            (event) => {  // leave event
                $tooltip.hide()
        })
    }

    // node reducer for rendering temporary states
    node_reducer(node, attrs) {  // return temporary node properties
        // depending on settings, hide or obscure out-of-range nodes
        if (this.is_out_of_range(attrs)) {
            if (this.settings.show_out_of_range_nodes) {
                this.obscure(attrs)
            } else {
                this.hide(attrs)
            }
        }

        return attrs;
    };

    // edge reducer for rendering temporary states
    edge_reducer(edge, attrs) {  // return temporary edge properties
        return attrs;
    }

    init() {
        // populate menu
        this.create_menu()

        // bind settings menu to settings menu button
        this.$menu_button.on('click', () => this.$menu.toggle())

        // help button and tutorial
        this.$help.load("/help")  // load help.html into the container div
        this.$help_button.on('click', () => this.$help.toggleClass("expanded"))  // clicking the help button expands the tutorial div
    }

    init_graph() {
    }

}

