function select_menu_tab(event, $menu, class_name) {
    // when the tab with class "class_name" is clicked in the given $menu
    let selector = CSS.escape(class_name)  // clean selector for this class name

    // hide all menu tabs
    let $tabs = $menu.find("div.page");
    for (let tab of $tabs) {
        $(tab).hide()
    }
    // unhide the selected menu tab
    $menu.find(`div.page.${selector}`).show()

    // remove active class from all tab buttons
    let $buttons = $menu.find('div.tabs button');
    for (let button of $buttons) {
        $(button).removeClass("active")
    }
    // add active class to selected tab button
    $menu.find(`div.tabs button.${selector}`).addClass("active")
}

$(document).ready(function() {
    var $help = $("div#help")  // main div
    var $display = $help.find("div#display")  // hover-image display div
    var $display_img = $("<img/>").appendTo($display)
    var screen_width = $(window).width()
    var screen_height = $(window).height()

    // wrap all images in special divs with class "display" to be targeted by css
    let $images = $("div.page p img")  // images within instruction paragraphs in each section
    for (let img of $images) {
        let $div = $(img).wrap('<div">&#128065</div>').parent()  // wrap image in div to hover
        $div.hover(
            event => {  // enter
                $display.addClass("active") // set as active
                $display_img.prop('src', img.src)  // set image source to the hovered div's image
                let pos = $(event.target).position()  // get hovered div's page position
                $display.css({left: pos.left + "px", top: pos.top + "px"})  // set the display div to that position
            },
            event => {  // leave
                $display.removeClass("active")  // no longer active
            })
    }

    // different visible tabs for different sections
    var $tabs = $("div.tabs")  // div to contain all tabs
    var $first = null  // first tab button created
    let n = 0;  // tab number
    for (let page of $("div.page")) {  // for each tab section
        let name = $(page).attr("name")  // name of this section
        let class_name = "tab-"+n  // unique class number for this tab

        let $tab = $(`<button class="tab ${class_name}">${name}</button>`).appendTo($tabs)
        $tab.on('click', event => select_menu_tab(event, $help, class_name))  // bind click event to open menu with this class
        if ($first === null) $first = $tab  // this was the first button added

        // set the tab's associated menu page class too
        $(page).addClass(class_name)
        n += 1
    }
    $first.trigger('click')  // click the first button added
});