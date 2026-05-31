const path = "/status"

async function fetchData() {
    const response = await fetch(path)
    const result = await response.json();
    await updatePage(result);
}

async function updateStatusText(text) {
    const element = document.getElementById("status_text")
    element.innerHTML = text;
    element.className = text
}

async function updatePage(result) {
    if (!result["blocking"]) {
        await updateStatusText("disabled");
        document.getElementById("timer_text").innerHTML = ` for ${Math.round(result["timer"])} seconds`;
    } else {
        await  updateStatusText("enabled");
        document.getElementById("timer_text").innerHTML = "";
    }
}

window.onload = async function() {
    await fetchData();
    setInterval(fetchData, 5000);
}
