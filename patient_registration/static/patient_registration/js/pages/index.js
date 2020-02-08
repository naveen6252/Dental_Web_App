//[custom Javascript]
//Project:	Aero - Responsive Bootstrap 4 Template
//Version:  1.0
//Last change:  15/12/2019
//Primary use:	Aero - Responsive Bootstrap 4 Template
//should be included in all pages. It controls some layout
$(function () {
    "use strict";
    initSparkline();
    initC3Chart();
});

function initSparkline() {
    $(".sparkline").each(function () {
        var $this = $(this);
        $this.sparkline('html', $this.data());
    });
}

function initC3Chart() {
    setTimeout(function () {
        $(document).ready(function () {
            var chart = c3.generate({
                bindto: '#mom-chart', // id of chart wrapper
                data: {
                    columns: [
                        // each columns data
                        ['data1', 10000, 26000, 38000, 18000, 19000, 45000, 55000, 62000, 15000, 22000, 8000, 20000],
                        ['data2', 2000, 3000, 1000, 100, 0, 4000, 300, 3000, 2000, 1000, 4000, 30000]
                    ],
                    type: 'line', // default type of chart
                    groups: [
                        ['data1', 'data2']
                    ],
                    colors: {
                        'data1': "#3866a6",
                        'data2': "#b93d30"
                    },
                    names: {
                        'data1': 'Service Amount',
                        'data2': 'Due Amount'
                    }
                },
                axis: {
                    x: {
                        type: 'category',
                        // name of each category
                        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    },
                },
                bar: {
                    width: 60,
                },
                legend: {
                    show: true, //hide legend
                },
                padding: {
                    bottom: 0,
                    top: 0,
                },
                grid: {
                    x: {
                        show: true
                    },
                    y: {
                        show: true
                    }
                },
            });
        });

        $(document).ready(function () {
            var chart = c3.generate({
                bindto: '#appointment-pie', // id of chart wrapper
                data: {
                    columns: [
                        ['Doctor 1', 30],
                        ['Doctor 2', 10],
                        ['Doctor 3', 5],
                    ],
                    type: 'pie', // default type of chart
                    colors: {
                        'Doctor 1': Aero.colors["lime"],
                        'Doctor 2': Aero.colors["teal"],
                        'Doctor 3': Aero.colors["yellow-dark"],
                    },

                },
                pie: {
                    label: {
                        format: function (value, ratio, id) {
                            return value
                        }
                    }
                },
                axis: {},
                legend: {
                    show: true, //hide legend
                },
                padding: {
                    bottom: 0,
                    top: 0
                },
            });
        });

        $(document).ready(function () {
            var chart = c3.generate({
                bindto: '#doctor-chart', // id of chart wrapper
                data: {
                    columns: [
                        // each columns data
                        ['revenue', 120300, 255700, 203500, 437000],
                        ['due', 70000, 90000, 106000, 200000]
                    ],
                    type: 'bar',
                    types: {
                        'due': "line",
                    },
                    groups: [
                        [ 'revenue']
                    ],
                    colors: {
                        'revenue': Aero.colors["cyan"],
                        'due': Aero.colors["green"],
                    },
                },
                axis: {
                    x: {
                        type: 'category',
                        // name of each category
                        categories: ['Doctor 1', 'Doctor 2', 'Doctor 3', 'Doctor 4']
                    },
                },
                bar: {
                    width: '50%',
                },
                legend: {
                    show: true, //hide legend
                },
                padding: {
                    bottom: 0,
                    top: 0
                },
            });
        });

    }, 500);
}

setTimeout(function () {
    "use strict";
    var mapData = {
        "US": 298,
        "SA": 200,
        "AU": 760,
        "IN": 2000000,
        "GB": 120,
    };
    if ($('#world-map-markers').length > 0) {
        $('#world-map-markers').vectorMap({
            map: 'world_mill_en',
            backgroundColor: 'transparent',
            borderColor: '#fff',
            borderOpacity: 0.25,
            borderWidth: 0,
            color: '#e6e6e6',
            regionStyle: {
                initial: {
                    fill: '#f4f4f4'
                }
            },

            markerStyle: {
                initial: {
                    r: 5,
                    'fill': '#fff',
                    'fill-opacity': 1,
                    'stroke': '#000',
                    'stroke-width': 1,
                    'stroke-opacity': 0.4
                },
            },

            markers: [{
                latLng: [21.00, 78.00],
                name: 'INDIA : 350'

            },
                {
                    latLng: [-33.00, 151.00],
                    name: 'Australia : 250'

                },
                {
                    latLng: [36.77, -119.41],
                    name: 'USA : 250'

                },
                {
                    latLng: [55.37, -3.41],
                    name: 'UK   : 250'

                },
                {
                    latLng: [25.20, 55.27],
                    name: 'UAE : 250'

                }],

            series: {
                regions: [{
                    values: {
                        "US": '#49c5b6',
                        "SA": '#667add',
                        "AU": '#50d38a',
                        "IN": '#60bafd',
                        "GB": '#ff758e',
                    },
                    attribute: 'fill'
                }]
            },
            hoverOpacity: null,
            normalizeFunction: 'linear',
            zoomOnScroll: false,
            scaleColors: ['#000000', '#000000'],
            selectedColor: '#000000',
            selectedRegions: [],
            enableZoom: false,
            hoverColor: '#fff',
        });
    }
}, 800);