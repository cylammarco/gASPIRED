var classesNumber = 10,
    cellSize = 24;

//#########################################################
function heatmap_display(data, heatmapId, paletteName) {

    var width = 35;
    //##########################################################################
    // Patrick.Brockmann@lsce.ipsl.fr
    //##########################################################################
    
    //==================================================
    // References
    // http://bl.ocks.org/Soylent/bbff6cc507dca2f48792
    // http://bost.ocks.org/mike/selection/
    // http://bost.ocks.org/mike/join/
    // http://stackoverflow.com/questions/9481497/understanding-how-d3-js-binds-data-to-nodes
    // http://bost.ocks.org/mike/miserables/
    // http://bl.ocks.org/ianyfchang/8119685

    //==================================================
    var tooltip = d3.select(heatmapId)
        .append("div")
        .style("position", "absolute")
        .style("visibility", "hidden");

    //==================================================
    // http://bl.ocks.org/mbostock/3680958
    function zoom() {
        svg.attr("transform", d3.event.transform);
    }

    // define the zoomListener which calls the zoom function on the "zoom" event constrained within the scaleExtents
    var zoomListener = d3.zoom().scaleExtent([0.1, 3]).on("zoom", zoom);

    //==================================================
    var viewerWidth = $(document).width();
    var viewerHeight = 600;
    var viewerPosTop = 200;
    var viewerPosLeft = 100;

    var legendElementWidth = cellSize * 2;

    // http://bl.ocks.org/mbostock/5577023
    var colors = colorbrewer[paletteName][classesNumber];

    // http://bl.ocks.org/mbostock/3680999
    var svg;

    //==================================================

    var arr = data.data;
    var row_number = arr.length;
    var col_number = arr[0].length;
    //console.log(col_number, row_number);

    var colorScale = d3.scaleQuantize()
        .domain([0.0, 1.0])
        .range(colors);

    svg = d3.select(heatmapId).append("svg")
        .attr("width", viewerWidth)
        .attr("height", viewerHeight)
    .call(zoomListener)
        .append("g")
        .attr("transform", "translate(" + viewerPosLeft + "," + viewerPosTop + ")");

    svg.append('defs')
        .append('pattern')
        .attr('id', 'diagonalHatch')
        .attr('patternUnits', 'userSpaceOnUse')
        .attr('width', 4)
        .attr('height', 4)
        .append('path')
        .attr('d', 'M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2')
        .attr('stroke', '#000000')
        .attr('stroke-width', 1);

    var row = svg.selectAll(".row")
        .data(data.data)
        .enter().append("g")
        .attr("id", function(d) {
            return d.idx;
        })
        .attr("class", "row");

    var j = 0;
    var heatMap = row.selectAll(".cell")
        .data(function(d) {
            return d;
        })
        .enter().append("svg:rect")
        .attr("x", function(d, i) {
            return i * cellSize;
        })
        .attr("y", function(d, i) {
            if (i % width == 0) {
                j++;
            }
            return j * cellSize;
        })
        .attr("rx", 2)
        .attr("ry", 2)
        .attr("class", function(d, i) {
            return "cell bordered cr" + j + " cc" + i;
        })
        .attr("row", function(d, i) {
            return j;
        })
        .attr("col", function(d, i) {
            return i;
        })
        .attr("width", cellSize)
        .attr("height", cellSize)
        .style("fill", function(d) {
            if (d != null) return colorScale(d);
            else return "url(#diagonalHatch)";
        })
        .on('mouseover', function(d, i) {
            d3.select(this.parentNode).raise();
            d3.select(this)
                .raise()
                .attr('class', function(d, i) {
                    return "cell highlighted cr" + j + " cc" + i;
                })
//                if (d != null) {
//                    tooltip.html('<div class="heatmap_tooltip">' + d.toFixed(3) + '</div>');
//                    tooltip.style("visibility", "visible");
//                } else
//                    tooltip.style("visibility", "hidden");
        })
        .on('mouseout', function(d, i,) {
            d3.select(this)
                .attr('class', function(d, i) {
                    return "cell bordered cr" + j + " cc" + i;
                })
//                tooltip.style("visibility", "hidden");
        })
        .on("mousemove", function(d, i) {
//                tooltip.style("top", (d3.event.pageY - 55) + "px").style("left", (d3.event.pageX - 60) + "px");
        })
        .on('click', function() {
            //console.log(d3.select(this));
        });

    var legend = svg.append("g")
        .attr("class", "legend")
        .attr("transform", "translate(0,-300)")
        .selectAll(".legendElement")
        .data([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
        .enter().append("g")
        .attr("class", "legendElement");

    legend.append("svg:rect")
        .attr("x", function(d, i) {
            return legendElementWidth * i;
        })
        .attr("y", viewerPosTop)
        .attr("class", "cellLegend bordered")
        .attr("width", legendElementWidth)
        .attr("height", cellSize / 2)
        .style("fill", function(d, i) {
            return colors[i];
        });

    legend.append("text")
        .attr("class", "mono legendElement")
        .text(function(d) {
            return "≥" + Math.round(d * 100) / 100;
        })
        .attr("x", function(d, i) {
            return legendElementWidth * i;
        })
        .attr("y", viewerPosTop + cellSize);

    //==================================================
    d3.select("#palette")
        .on("keyup", function() {
    var newPalette = d3.select("#palette").property("value");
    if (newPalette != null)                     // when interfaced with jQwidget, the ComboBox handles keyup event but value is then not available ?
                changePalette(newPalette, heatmapId);
        })
        .on("change", function() {
    var newPalette = d3.select("#palette").property("value");
            changePalette(newPalette, heatmapId);
        });

    //==================================================
}

//#########################################################
function changePalette(paletteName, heatmapId) {
    var colors = colorbrewer[paletteName][classesNumber];
    var colorScale = d3.scale.quantize()
        .domain([0.0, 1.0])
        .range(colors);
    var svg = d3.select(heatmapId);
    var t = svg.transition().duration(500);
    t.selectAll(".cell")
        .style("fill", function(d) {
                if (d != null) return colorScale(d);
                else return "url(#diagonalHatch)";
        })
    t.selectAll(".cellLegend")
        .style("fill", function(d, i) {
            return colors[i];
        });
}