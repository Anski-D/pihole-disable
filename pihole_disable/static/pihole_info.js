const statusPath = "/status"
const clientPath = "/client"

async function fetchIp() {
    const response = await fetch(clientPath);
    const result = await response.json();
    await updateIp(result["IP"]);
}

async function updateIp(address) {
    let element = document.getElementById("client-ip");
    if (element) { element.innerText = address; }
    element = document.getElementById("ip-addr");
    if (element) { element.value = address; }
}

async function fetchStatus() {
    const response = await fetch(statusPath);
    const result = await response.json();
    await updateStatus(result);
}

async function updateStatusText(text) {
    const element = document.getElementById("status-text");
    if (element) {
        element.innerText = text;
        element.className = text;
    }
}

async function updateStatus(result) {
    const element = document.getElementById("timer-text");
    if (!result["blocking"]) {
        await updateStatusText("disabled");
        if (element) {element.innerText = ` for ${Math.round(result["timer"])} seconds`;}
    } else {
        await updateStatusText("enabled");
        if (element) {element.innerText = "";}
    }
}

window.onload = async function() {
    await fetchIp();
    await fetchStatus();
    setInterval(fetchStatus, 5000);
}
