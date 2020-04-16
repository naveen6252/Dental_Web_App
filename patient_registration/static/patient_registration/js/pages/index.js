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
                bindto: '#treatment-chart', // id of chart wrapper
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
                        categories: ['Treatment 1', 'Treatment 2', 'Treatment 3', 'Treatment 4']
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
                bindto: '#expense-pie', // id of chart wrapper
                data: {
                    columns: [
                        ['Rent', 50000],
                        ['Salary', 60000],
                        ['Material', 10000],
                        ['Medicine', 40000],
                        ['Lab Bills', 5000],
                        ['Government Bills', 5000],
                        ['Accessories', 250000],
                        ['Enhancement', 12000],
                    ],
                    type: 'pie',

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
                    show: false, //hide legend
                },
                padding: {
                    bottom: 0,
                    top: 0
                },
            });
        });

        $(document).ready(function () {
            var chart = c3.generate({
                bindto: '#expense-trend',
                data: {
                    columns: [
                        // each columns data
                        ['data1', 12000, 12000, 15000, 1000, 8000, 20000, 25000, 18000, 26000, 30000, 60000, 20000]
                    ],
                    type: 'line', // default type of chart
                    colors: {
                        'data1': "#3866a6"
                    },
                    names: {
                        'data1': 'Expense Amount'
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


    }, 500);
}
