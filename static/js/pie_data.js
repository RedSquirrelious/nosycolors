d3.select('#tweet_view').append("text")
	.text("")
	.attr("class", "viewed_tweet");

var targetthing = {{target|safe}};

var something = {{tweet_emotions|safe}};

var otherthing = {{tweet_details|safe}};



var label = d3.scale.ordinal()
.range(["anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"]);


var color = d3.scale.ordinal()
	.domain(["anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"])
	.range(["#e34141", "#4545ec", "#652e2e", "#272323", "#eeee4b", "#808080", "#944fba", "#22c322"]);
	// .range(red, blue, brown, black, yellow, grey, purple,green)

var m = 5,
    r = 45,
    height = 300,
    width = 300,
    centered;


var scoring = function(d) {
	console.log(d);
	return d.sentiment.score;
};

var pie = d3.layout.pie()
	.value( function(d) { return d.scores; })
	.padAngle(.01)
	.sort(null);

var arc = d3.svg.arc()
        .innerRadius(r / 2)
        .outerRadius(r);

var arcOver = d3.svg.arc()
		.innerRadius(r * 2 )
		.outerRadius(r * 4);

var pie = d3.layout.pie()
    .value(function(d) { return +d.score; })
    .sort(null);
    // .sort(function(a, b) { return b.score - a.score; });

var data = {};

var tweet_scoring = d3.nest()
		.key(function(d) { return d.tweet_id; })
		.entries(something);

var tweet_emoting = d3.nest()
		.key(function(d) { return d.tweet_id; })
		.entries(something);
    
var svg = d3.select(".testpie").selectAll("div")
			.data(tweet_scoring)
			.enter().append("div")
			.attr("class", "emotion_donut")
			// .attr("class", "svg-container")
   		// .classed("svg-container", true)
				.append("svg")
		    .attr("width", (r + m) * 2)
		    .attr("height", (r + m) * 2)
		    .attr("class", "tweet")
		  	.attr("id", function(d, i) {return "tweet_" + i; })
  		.append("g")
    	.attr("transform", "translate(" + (r + m) + "," + (r + m) + ")");

svg.append("text")
	.each(function(d) { this._current = d;})
  .attr("dy", ".35em")
  .attr("text-anchor", "middle")
  .attr("class", "tweet_text")
  // .text(function(d) {return this._current.key;})
  .attr("id", function(d) { return "tweet_text_" + this._current.key; });


var g = svg.selectAll('g')
	.data(function(d) { return pie(d.values); })
	.enter().append('g');

  g.append("path")
  		.each(function(d) { this._current = d; })
      .attr("d", arc)
      .attr("class", "emotionArc")
      // .attr("class", this._current.data.tweet_id)
	 		.attr("id", function(d, i) {return "emotionArc_" + i; })
      .style("fill", function(d) { return color(d.data.emotion); });

      // g.append("text")
      //     .attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")"; })
      //     .attr("dy", ".35em")
      //     .style("text-anchor", "middle");

      // g.select("text").text(function(d) { return d.data.emotion; });      

      g.on("mouseover", function(obj){
        // console.log(obj.data)
        svg.select("#tweet_text_"+ obj.data.tweet_id)
        .attr("fill", function(d) { return color(obj.data.emotion); })
        .attr("font-weight", "bold")
        .style("font-size", r/6+"px")
        .text(function(d){
          return obj.data.emotion;
        });
      });

      svg.on("click", clicked);



function clicked(d) {
	console.log(this);
	var mypie = d3.select(this);
	console.log(mypie[0][0].viewportElement.id);
	var bigpie = ("#"+mypie[0][0].viewportElement.id);
	console.log(bigpie);
	var thatpie = bigpie.replace(/[^0-9]/gi, '');
	console.log(thatpie);

	// d3.select(".nosy_query")
	// .html("")
	// .html(function(d) { return "'" + target.name "'" + " is feeling all these feels...";});

	d3.select('#tweet_view')
	.text("")
	.html(function(d) { return "[" + otherthing[thatpie].created_at + "] " + otherthing[thatpie].text;})

};

