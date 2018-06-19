var site_status = Vue.component('site-status', {
    props: ['siteid'],
    data() {
        return {
            status: "Good",
            production: 20,
            performance: 10
        }
    },
    delimiters: ['[[', ']]'],
    // language=HTML
    template: `
            <div class="bottom-info-row">
                <div class="production-info">
                    <div><h2>Today's production:</h2></div>
                    <div><h1>[[ production ]] kWh</h1></div>
                </div>
                <div class="production-info">
                    <div><h2>Status:</h2></div>
                    <div><h1>[[ status ]]</h1></div>
                </div>
                <div class="production-info">
                    <div><h2>Performance:</h2></div>
                    <div><h1>[[ performance ]] %</h1></div>
                </div>
            </div>
    `,
    created: function() {
        var _this = this;
        $.getJSON('/data/' + this.siteid, function (data) {
            generated = data.daily.energy_generated;
            expected = data.daily.energy_expected;
            _this.status = data.status.dashboard_status;
            _this.production = Math.round(generated / 1000);
            if (generated === null) {
                _this.performance = 0;
            } else{
                _this.performance = Math.round(100 * generated / expected)
            }
            console.log(data);
        });
    }
});

var site_weather = Vue.component('site-weather', {
    props: ['siteid'],
    data() {
        return {
            temperature: 10,
            weather_icon: "",
            weather: "fine"
        }
    },
    delimiters: ['[[', ']]'],
    template: `<div><h2>[[ temperature ]] &deg;C <i v-bind:class="weather_icon"></i></h2></div>`,
    created: function() {
        var _this = this;
        $.getJSON('/data/' + this.siteid, function (data) {
            _this.temperature = Math.round(data.weather.Weather.temperature.temp - 273.15);
            weather_icon = data.weather.Weather.weather_code;
            _this.weather_icon = "owf owf-" + weather_icon;
            console.log(_this.weather_icon);
            _this.weather = data.weather.Weather.status;
        })
    }
});


var site_data = Vue.component('site-data', {
    props: ['siteid'],
    data: function(){
        return {
            componentid: guidGenerator(),
        }
    },
    delimiters:['[[',']]'],
    template: '<div class="graph" v-bind:id="componentid"></div>',

    mounted: function(){
        var self = this;
        $.getJSON('/data/'+this.siteid ,
            function (data) {
                data = data.solar;

                Highcharts.chart(self.componentid, {
                    chart: {
                        zoomType: 'x',
                        backgroundColor: '#00292D',
                    },
                    title: {
                        text: ''
                    },

                    xAxis: {
                        type: 'datetime'
                    },
                    yAxis: {
                        title: {
                            text: 'kW'
                        },
                        min:0,
                    },
                    legend: {
                        enabled: false
                    },
                    plotOptions: {
                        area: {
                            fillColor: {
                                linearGradient: {
                                    x1: 0,
                                    y1: 0,
                                    x2: 0,
                                    y2: 1
                                },
                                stops: [
                                    [0, Highcharts.getOptions().colors[0]],
                                    [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                                ]
                            },
                            marker: {
                                radius: 2
                            },
                            lineWidth: 1,
                            states: {
                                hover: {
                                    lineWidth: 1
                                }
                            },
                            threshold: null
                        }
                    },

                    series: [{
                        type: 'area',
                        name: 'Generation',
                        data: data
                    }]
                });
            }
        );
    }
});


function guidGenerator() {
    var S4 = function() {
       return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    };
    return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}
