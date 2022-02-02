import "./lib/graphology.min.js"
import "./lib/sigma.min.js"
import {Plot} from "./plot.js"

$(document).ready(function() {

    var ID = window.location.pathname  //   http://host/graph/ID
    ID = ID.substring(ID.lastIndexOf("/")+1, ID.length)  // get just the ID

    var plot = new Plot()

    $.ajax({url: "/get_graph/"+ID,
        success: function(data) {
            plot.import(data)
        },
        error: function(data) {
            let json = data.responseJSON
            console.log('data', data)
            plot.error(json.error, json.message)
        }
    });



});