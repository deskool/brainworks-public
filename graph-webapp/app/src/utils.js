export function decimals(scale) {
    // returns appropriate number of decimals to keep
    return scale >= 100 ? 0 : Math.ceil(-Math.log10(scale)+1)
}

function hex_to_rgb(hex_code) {
  	var colors = {}
    colors.red = parseInt(hex_code.substr(1, 2), 16)
  	colors.green = parseInt(hex_code.substr(3, 2), 16)
  	colors.blue = parseInt(hex_code.substr(5, 2), 16)
    return colors
}

function rgb_to_hex(red, green, blue) {
	var hex_code = "#"
    hex_code += parseInt(red).toString(16)
  	hex_code += parseInt(green).toString(16)
  	hex_code += parseInt(blue).toString(16)
  	return hex_code
}

export function lighten(hex_code, val) {
    var {red, green, blue} = hex_to_rgb(hex_code)
    red += (255 - red) * val
    green += (255 - green) * val
    blue += (255 - blue) * val
    return rgb_to_hex(red, green, blue)
}

export function logbase(base, num) {
    return Math.log(num) / Math.log(base)
}

export function array_mode(arr) {
    if(arr.length == 0)
        return null
    var counts = {}
    for(let val of arr) {
        if(counts[val] == undefined)
            counts[val] = 1;
        else
            counts[val]++;
    }
    return Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b);
}

export function array_mean(arr) {
    return arr.reduce((a,b) => a + b, 0) / arr.length
}