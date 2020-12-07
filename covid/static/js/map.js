// This example requires the Visualization library. Include the libraries=visualization
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization">
let map, heatmap, covidCases, allCounties, tempCounties = [], coordsArray = [], firstLoad;

var button = document.querySelector("#button");
var dateInput = document.getElementById("dateInput");
var today = new Date();
todayArr = today.toString().split(" ");
switch(todayArr[1]) {
    case "Jan":
        todayArr[1] = "01"
        break;
    case "Feb":
        todayArr[1] = "02"
        break;
    case "Mar":
        todayArr[1] = "03"
        break;
    case "Apr":
        todayArr[1] = "04"
        break;
    case "May":
        todayArr[1] = "05"
        break;
    case "Jun":
        todayArr[1] = "06"
        break;
    case "Jul":
        todayArr[1] = "07"
        break;
    case "Aug":
        todayArr[1] = "08"
        break;
    case "Sep":
        todayArr[1] = "09"
        break;
    case "Oct":
        todayArr[1] = "10"
        break;
    case "Nov":
        todayArr[1] = "11"
        break;
    case "Dec":
        todayArr[1] = "12"
        break;
    default:
        // nothing
}

var todayString = todayArr[3] + "-" + todayArr[1] + "-" + todayArr[2];
var date = "";
var slider = document.querySelector("#slider");
var startDate;

slider.addEventListener("change", function(e) {
    var days = addDays(startDate, parseInt(e.target.value));
    var formattedDate = formatDate(days);
    getData(formattedDate);
})

slider.addEventListener("input", function(e) {
    document.querySelector("#dateSpan").innerHTML = addDays(startDate, parseInt(e.target.value)).toDateString();
})

function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;

    return [year, month, day].join('-');
}

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 4,
    center: { lat: 39.8283, lng: -98.5795 },
    mapTypeId: "hybrid",
  });
}

function addDays(date, days) {
    var result = new Date(date);
    result.setDate(result.getDate() + days);
    console.log(typeof result);
    return result;
}

// start by getting data as soon as page loads
fetch("https://storage.googleapis.com/daniels_covid_data/covidcasesdec.json")
.then(response => response.json())
.then(data => {
    covidCases = data;
    startDate = new Date(covidCases[0].date);
    slider.setAttribute("max", (today - startDate)/(1000*60*60*24));
    document.querySelector("#dateSpan").innerHTML = "Adjust slider to select a date";
    firstLoad = true;
    fetch("https://storage.googleapis.com/daniels_covid_data/countieswithcoords.json")
    .then(response => response.json())
    .then(data => {
        allCounties = data;
        allCounties.forEach(item => {
            var fips = item.GEOID.toString();
            while (fips.length < 5) {
                fips = "0" + fips
            }
            item.fips = fips;
        })
        slider.classList.remove("disabled");
        getData(date);
    })
})

function getData(date) {
    tempCounties = [];
    covidCases.forEach(item => {
        if (item.date === date) {
            tempCounties.push({
                fips: item.fips,
                cases: item.cases
            });
        }
    })

    var xy = [];
    for (var i = 0; i < allCounties.length; i++) {
        for (var j = 0; j < tempCounties.length; j++) {
            if (allCounties[i].fips === tempCounties[j].fips) {
                xy.push([allCounties[i].INTPTLAT, allCounties[i].INTPTLONG, tempCounties[j].cases]);
            }
        }
    }
    // create some kind of fetch here, then insert json points into getPoints
    if (!heatmap) {
        heatmap = new google.maps.visualization.HeatmapLayer({
            data: getPoints(xy),
            map: map,
            radius: 20,
            opacity: .7
        });
    } else {
        heatmap.setData(getPoints(xy))
    }
    
    
    function getPoints(xy) {
        coordsArray = [];
        var total = 0;
        for (var i = 0; i < xy.length; i++) {
            coordsArray.push({location: new google.maps.LatLng(xy[i][0], xy[i][1]), weight: parseInt(xy[i][2]) * 100})
            total += parseInt(xy[i][2]);
        }
        totalCases = total.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        if (!firstLoad) {
            document.querySelector("#totalCases").innerHTML = "Total reported COVID-19 cases by " + date + ": ";
            document.querySelector("#totalCasesNumberSpan").innerHTML = totalCases;
        }
        firstLoad = false;
        return coordsArray;
    }
}

function toggleHeatmap() {
    heatmap.setMap(heatmap.getMap() ? null : map);
}

function changeGradient() {
    const gradient = [
        "rgba(0, 255, 255, 0)",
        "rgba(0, 255, 255, 1)",
        "rgba(0, 191, 255, 1)",
        "rgba(0, 127, 255, 1)",
        "rgba(0, 63, 255, 1)",
        "rgba(0, 0, 255, 1)",
        "rgba(0, 0, 223, 1)",
        "rgba(0, 0, 191, 1)",
        "rgba(0, 0, 159, 1)",
        "rgba(0, 0, 127, 1)",
        "rgba(63, 0, 91, 1)",
        "rgba(127, 0, 63, 1)",
        "rgba(191, 0, 31, 1)",
        "rgba(255, 0, 0, 1)",
    ];
        heatmap.set("gradient", heatmap.get("gradient") ? null : gradient);
}

function changeRadius() {
    heatmap.set("radius", heatmap.get("radius") ? null : 20);
}

function changeOpacity() {
    heatmap.set("opacity", heatmap.get("opacity") ? null : 0.2);
}
