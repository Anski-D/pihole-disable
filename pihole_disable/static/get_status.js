const path = "/status"

async function fetchData() {
    let response = await fetch(path)
    let result = await response.json();
    updatePage(result);
}

function updatePage(result) {
    if (!result["blocking"]) {
        document.getElementById("status_text").innerHTML = "disabled";
        document.getElementById("status_text").className = "disabled";
        document.getElementById("timer_text").innerHTML = ` for ${Math.round(result["timer"])} seconds`;
    } else {
        document.getElementById("status_text").innerHTML = "enabled";
        document.getElementById("status_text").className = "enabled";
        document.getElementById("timer_text").innerHTML = "";
    }
}

window.onload = async function () {
    await fetchData();
    setInterval(fetchData, 5000);
}
