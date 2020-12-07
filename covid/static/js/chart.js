let covidCases, allCounties, tempCounties = [];
var button = document.querySelector("#button");

var today = new Date().toString();
todayArr = today.split(" ");
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
var dateInput = document.getElementById("date");
dateInput.value = todayString;
dateInput.setAttribute("max", todayString);
var date = "";

button.addEventListener("click", function() {
    date = dateInput.value;
    getData(date);
});

// start by getting data as soon as page loads
fetch("https://storage.googleapis.com/daniels_covid_data/covidcasesdec.json")
.then(response => response.json())
.then(data => {
    covidCases = data;
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
        button.classList.remove("disabled");
        button.innerHTML = "Check";
    })
})

function getData(date) {
    tempCounties = [];
    console.log(tempCounties);
    covidCases.forEach(item => {
        if (item.date === date) {
            tempCounties.push({
                fips: item.fips,
                cases: item.cases,
                state: item.state,
                county: item.county,
                deaths: item.deaths ? item.deaths : 0
            });
        }
    })

    var table = document.getElementById("tbody");
    if (table.children.length > 0) {
        table.children[0].remove();
    }

    var cases = 0;
    for (var i = 0; i < allCounties.length; i++) {
        for (var j = 0; j < tempCounties.length; j++) {
            if (allCounties[i].fips === tempCounties[j].fips) {
                var rowCount = table.rows.length;
                var row = table.insertRow(rowCount);
                let cell = tempCounties[j];
                row.insertCell(0).innerHTML = cell.state;
                row.insertCell(1).innerHTML = cell.county;
                row.insertCell(2).innerHTML = cell.cases;
                row.insertCell(3).innerHTML = cell.deaths;
                cases += parseInt(cell.cases);
            }
        }
    }
    totalCases = cases.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")
    document.querySelector("#totalCases").innerHTML = "Total reported COVID-19 cases by " + date + ": ";
    document.querySelector("#totalCasesNumberSpan").innerHTML = totalCases;

}