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
            var chart = c3.generate(mom_chart);
        });

        $(document).ready(function () {
            var chart = c3.generate(treatment_chart);
        });

        $(document).ready(function () {
            var chart = c3.generate({
                bindto: '#appointment-pie',
                data: {
                    columns: appointment_by_doctor,
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
                    show: true,
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
                    columns: expense_amount,
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
            var chart = c3.generate(expense_trend);
        });


    }, 500);
}
