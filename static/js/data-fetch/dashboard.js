
// Fetch Session Number Changes
$(document).ready(function () {
fetchSessionChange();

function fetchSessionChange() {
    $.ajax({
    type: "GET",
    url: "/fetch-session-change",
    success: function (data) {
        $("#percentage-change").text(data.percentage_change + "%");
    },
    error: function (error) {
        console.error("Error fetching session change data:", error);
        $("#percentage-change").text("N/A");
    }
    });
}
});

// Fetch Session Summary Chart

$(document).ready(function() {
fetchSessionSummary();
});

function fetchSessionSummary(){
fetch('/session-summary-data')
    .then(response => response.json())
    .then(data => {
    updateSessionSummary(data);
    })
    .catch(error => console.error(error));
}

function updateSessionSummary(data){
$('#total-session').text(data.total_sessions);
var statusSummaryChartCanvas = document.getElementById("status-summary").getContext('2d');

// Extract session counts from the received data
var sessionCounts = data.current_week_data.map(row => row.session_count);
var sessionDays = data.current_week_data.map(row => row.day);

var statusData = {
    labels: sessionDays,
    datasets: [{
        label: '# of Sessions',
        data: sessionCounts,
        backgroundColor: "#FFFF",
        borderColor: [
            '#FFFF',
        ],
        borderWidth: 2,
        fill: false,
        pointBorderWidth: 0,
        pointRadius: [0, 0, 0, 0, 0, 0, 0],
        pointHoverRadius: [0, 0, 0, 0, 0, 0, 0],
    }]
};

var statusOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        yAxes: [{
            display: false,
            gridLines: {
                display: false,
                drawBorder: false,
                color: "#F0F0F0"
            },
            ticks: {
                beginAtZero: false,
                autoSkip: true,
                maxTicksLimit: 4,
                fontSize: 10,
                color: "#FFFF"
            }
        }],
        xAxes: [{
            display: false,
            gridLines: {
                display: false,
                drawBorder: false,
            },
            ticks: {
                beginAtZero: false,
                autoSkip: true,
                maxTicksLimit: 7,
                fontSize: 10,
                color: "#FFF"
            }
        }],
    },
    legend: false,

    elements: {
        line: {
            tension: 0.4,
        }
    },
    tooltips: {
        backgroundColor: 'rgba(31, 59, 179, 1)',
    }
}
var statusSummaryChart = new Chart(statusSummaryChartCanvas, {
    type: 'line',
    data: statusData,
    options: statusOptions
});
}

setInterval(fetchSessionSummary, 60000);

// Fetch Datas

const sessionCount = {{ session_count }};
const inMessageCount = {{ inMessage_count }};
const botResponseCount = {{ botMessage_count }};
const avgResponseTime = {{ avg_response_time }};
const countVisitors = {{ visitor_count }};

$('#session-count').text(sessionCount);
$('#in-message-count').text(inMessageCount);
$('#bot-response-count').text(botResponseCount);
$('#avg-response-time').text(avgResponseTime);
$('#count-visitors').text(countVisitors);


// Fetch Session Number for Line Chart

$(document).ready(function() {
fetchPerformanceLineChart();

function fetchPerformanceLineChart(){
    fetch('/performance-linechart-data')
    .then(response => response.json())
    .then(data => {
        updateLineChart(data);
    })
    .catch(error => console.error(error));
}
});

function updateLineChart(data){
var graphGradient = document.getElementById("performaneLine").getContext('2d');
var graphGradient2 = document.getElementById("performaneLine").getContext('2d');
var saleGradientBg = graphGradient.createLinearGradient(5, 0, 5, 100);
saleGradientBg.addColorStop(0, 'rgba(26, 115, 232, 0.18)');
saleGradientBg.addColorStop(1, 'rgba(26, 115, 232, 0.02)');
var saleGradientBg2 = graphGradient2.createLinearGradient(100, 0, 50, 150);
saleGradientBg2.addColorStop(0, 'rgba(0, 208, 255, 0.19)');
saleGradientBg2.addColorStop(1, 'rgba(0, 208, 255, 0.03)');

var salesTopData = {
    labels: data.days,
    datasets: [{
        label: 'This week',
        data: data.current_week_session_data,
        backgroundColor: saleGradientBg,
        borderColor: [
            '#1F3BB3',
        ],
        borderWidth: 1.5,
        fill: true, // 3: no fill
        pointBorderWidth: 1,
        pointRadius: [4, 4, 4, 4, 4,4, 4, 4, 4, 4,4, 4, 4],
        pointHoverRadius: [2, 2, 2, 2, 2,2, 2, 2, 2, 2,2, 2, 2],
        pointBackgroundColor: ['#1F3BB3)', '#1F3BB3', '#1F3BB3', '#1F3BB3','#1F3BB3)', '#1F3BB3', '#1F3BB3',],
        pointBorderColor: ['#fff','#fff','#fff','#fff','#fff','#fff','#fff',],
    },{
        label: 'Last week',
        data: data.last_week_session_data,
        backgroundColor: saleGradientBg2,
        borderColor: [
            '#52CDFF',
        ],
        borderWidth: 1.5,
        fill: true, // 3: no fill
        pointBorderWidth: 1,
        pointRadius: [4, 4, 4, 4, 4,4, 4, 4, 4, 4,4, 4, 4],
        pointHoverRadius: [2, 2, 2, 2, 2,2, 2, 2, 2, 2,2, 2, 2],
        pointBackgroundColor: ['#52CDFF)', '#52CDFF', '#52CDFF', '#52CDFF','#52CDFF)', '#52CDFF', '#52CDFF',],
        pointBorderColor: ['#fff','#fff','#fff','#fff','#fff','#fff','#fff',],
    }]
};

var salesTopOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        yAxes: [{
            gridLines: {
                display: true,
                drawBorder: false,
                color:"#F0F0F0",
                zeroLineColor: '#F0F0F0',
            },
            ticks: {
                beginAtZero: false,
                autoSkip: true,
                maxTicksLimit: 4,
                fontSize: 10,
                color:"#6B778C"
            }
        }],
        xAxes: [{
            gridLines: {
                display: false,
                drawBorder: false,
            },
            ticks: {
            beginAtZero: false,
            autoSkip: true,
            maxTicksLimit: 7,
            fontSize: 10,
            color:"#6B778C"
            }
        }],
    },
    legend:false,
    legendCallback: function (chart) {
        var text = [];
        text.push('<div class="chartjs-legend"><ul>');
        for (var i = 0; i < chart.data.datasets.length; i++) {
        console.log(chart.data.datasets[i]); // see what's inside the obj.
        text.push('<li>');
        text.push('<span style="background-color:' + chart.data.datasets[i].borderColor + '">' + '</span>');
        text.push(chart.data.datasets[i].label);
        text.push('</li>');
        }
        text.push('</ul></div>');
        return text.join("");
    },
    
    elements: {
        line: {
            tension: 0.4,
        }
    },
    tooltips: {
        backgroundColor: 'rgba(31, 59, 179, 1)',
    }
}
var salesTop = new Chart(graphGradient, {
    type: 'line',
    data: salesTopData,
    options: salesTopOptions
});
document.getElementById('performance-line-legend').innerHTML = salesTop.generateLegend();
}

setInterval(fetchPerformanceLineChart, 60000);


// Fetch Session Number for BarChart

$(document).ready(function() {
fetchPerformanceBarChart();

function fetchPerformanceBarChart() {
    fetch('/performance-barchart-data')
    .then(response => response.json())
    .then(data => {
        updateBarChart(data);
    })
    .catch(error => console.error(error));
}
});

function updateBarChart(data) {
var marketingOverviewChart = document.getElementById("performanceBarChart").getContext('2d');
var marketingOverviewData = {
    labels: data.months,
    datasets: [{
        label: 'Month',
        data: data.session_counts,
        backgroundColor: "#CE1E2D",
        borderColor: [
            '#CE1E2D',
        ],
        borderWidth: 0,
        fill: true,
    }]
};

var marketingOverviewOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        yAxes: [{
            gridLines: {
                display: true,
                drawBorder: false,
                color:"#F0F0F0",
                zeroLineColor: '#F0F0F0',
            },
            ticks: {
                beginAtZero: true,
                autoSkip: true,
                maxTicksLimit: 5,
                fontSize: 10,
                color:"#6B778C"
            }
        }],
        xAxes: [{
            stacked: true,
            barPercentage: 0.35,
            gridLines: {
                display: false,
                drawBorder: false,
            },
            ticks: {
            beginAtZero: false,
            autoSkip: true,
            maxTicksLimit: 12,
            fontSize: 10,
            color:"#6B778C"
            }
        }],
    },
    legend:false,
    legendCallback: function (chart) {
        var text = [];
        text.push('<div class="chartjs-legend"><ul>');
        for (var i = 0; i < chart.data.datasets.length; i++) {
        console.log(chart.data.datasets[i]); // see what's inside the obj.
        text.push('<li class="text-muted text-small">');
        text.push('<span style="background-color:' + chart.data.datasets[i].borderColor + '">' + '</span>');
        text.push(chart.data.datasets[i].label);
        text.push('</li>');
        }
        text.push('</ul></div>');
        return text.join("");
    },
    
    elements: {
        line: {
            tension: 0.4,
        }
    },
    tooltips: {
        backgroundColor: 'rgba(31, 59, 179, 1)',
    }
};

var marketingOverview = new Chart(marketingOverviewChart, {
    type: 'bar',
    data: marketingOverviewData,
    options: marketingOverviewOptions
});

document.getElementById('marketing-overview-legend').innerHTML = marketingOverview.generateLegend();
}

setInterval(fetchPerformanceBarChart, 60000);


// Fetch Ratings Data

$(document).ready(function() {
fetchRatingsData();

function fetchRatingsData() {
    fetch('/ratings-data')
    .then(response => response.json())
    .then(data => {
        updateChart(data);
    })
    .catch(error => console.error(error));
}
});

function updateChart(data) {
    var doughnutChartCanvas = document.getElementById("doughnutChart");
    var doughnutPieData = {
        datasets: [{
            data: [data.satisfied, data.unsatisfied],  // Update chart data with fetched data
            backgroundColor: ["#1F3BB3", "#FDD0C7"],
            borderColor: ["#1F3BB3", "#FDD0C7"],
        }],
        labels: ['Satisfied', 'Unsatisfied'],
    };

    var doughnutPieOptions = {
        cutoutPercentage: 50,
        animationEasing: "easeOutBounce",
        animateRotate: true,
        animateScale: false,
        responsive: true,
        maintainAspectRatio: true,
        showScale: true,
        legend: false,
        legendCallback: function (chart) {
            var text = [];
            text.push('<div class="chartjs-legend"><ul class="justify-content-center">');
            for (var i = 0; i < chart.data.datasets[0].data.length; i++) {
                text.push('<li><span style="background-color:' + chart.data.datasets[0].backgroundColor[i] + '">');
                text.push('</span>');
                if (chart.data.labels[i]) {
                    text.push(chart.data.labels[i]);
                }
                text.push('</li>');
            }
            text.push('</div></ul>');
            return text.join("");
        },
        layout: {
            padding: {
                left: 0,
                right: 0,
                top: 0,
                bottom: 0,
            },
        },
        tooltips: {
            callbacks: {
                title: function (tooltipItem, data) {
                    return data['labels'][tooltipItem[0]['index']];
                },
                label: function (tooltipItem, data) {
                    return data['datasets'][0]['data'][tooltipItem['index']];
                },
                backgroundColor: '#fff',
                titleFontSize: 14,
                titleFontColor: '#0B0F32',
                bodyFontColor: '#737F8B',
                bodyFontSize: 11,
                displayColors: false,
            },
        },
    };

    var doughnutChart = new Chart(doughnutChartCanvas, {
        type: 'doughnut',
        data: doughnutPieData,
        options: doughnutPieOptions,
    });
    document.getElementById('doughnut-chart-legend').innerHTML = doughnutChart.generateLegend();
}

setInterval(fetchRatingsData, 60000);


//Fetch Data for Total Visitor and Visitor Today

function visitorSummary(){
    if ($('#totalVisitors').length) {
        var monthlyVisitorsCount = {{ monthly_visitors }};
        var bar = new ProgressBar.Circle(totalVisitors, {
        color: '#fff',
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 15,
        trailWidth: 15, 
        easing: 'easeInOut',
        duration: 1400,
        text: {
        autoStyleContainer: false
        },
        from: {
        color: '#52CDFF',
        width: 15
        },
        to: {
        color: '#677ae4',
        width: 15
        },
        // Set default step function for all animate calls
        step: function(state, circle) {
        circle.path.setAttribute('stroke', state.color);
        circle.path.setAttribute('stroke-width', state.width);

        var value = Math.round(circle.value() * 100);
        if (value === 0) {
            circle.setText('');
        } else {
            circle.setText(value);
        }

        }
    });

    bar.text.style.fontSize = '0rem';
    bar.animate(monthlyVisitorsCount / 100); // Number from 0.0 to 1.0
    }

    if ($('#visitperday').length) {
        var dailyVisitorsCount = {{ today_visitors }};
        var bar = new ProgressBar.Circle(visitperday, {
            color: '#fff',
            // This has to be the same size as the maximum width to
            // prevent clipping
            strokeWidth: 15,
            trailWidth: 15,
            easing: 'easeInOut',
            duration: 1400,
            text: {
            autoStyleContainer: false
            },
            from: {
            color: '#34B1AA',
            width: 15
            },
            to: {
            color: '#677ae4',
            width: 15
            },
            // Set default step function for all animate calls
            step: function(state, circle) {
            circle.path.setAttribute('stroke', state.color);
            circle.path.setAttribute('stroke-width', state.width);
    
            var value = Math.round(circle.value() * 100);
            if (value === 0) {
                circle.setText('');
            } else {
                circle.setText(value);
            }
        }
    });

    bar.text.style.fontSize = '0rem';
    bar.animate(dailyVisitorsCount / 100); // Number from 0.0 to 1.0
    }
}

visitorSummary();
