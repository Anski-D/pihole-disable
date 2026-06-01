const statusPath = "/status"
const clientPath = "/client"

async function fetchIp() {
    const response = await fetch(clientPath);
    const result = await response.json();
    await updateIp(result["IP"]);
}

async function updateIp(address) {
    const element = document.getElementById("client-ip");
    if (element) { element.innerHTML = address; }
}

async function fetchStatus() {
    const response = await fetch(statusPath);
    const result = await response.json();
    await updateStatus(result);
}

async function updateStatusText(text) {
    const element = document.getElementById("status-text");
    if (element) {
        element.innerHTML = text;
        element.className = text;
    }
}

async function updateStatus(result) {
    const element = document.getElementById("timer-text");
    if (!result["blocking"]) {
        await updateStatusText("disabled");
        if (element) {element.innerHTML = ` for ${Math.round(result["timer"])} seconds`;}
    } else {
        await updateStatusText("enabled");
        if (element) {element.innerHTML = "";}
    }
}

window.onload = async function() {
    await fetchIp();
    await fetchStatus();
    setInterval(fetchStatus, 5000);
}
