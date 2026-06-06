const statusPath = "/status"
const clientPath = "/client"
const clientInfoPath = "/info/client"
const apiUrl = "https://pihole.dacyho.me/api"
let ipAddress

async function fetchResponse(path) {
    const response = await fetch(path);
    return await response.json();
}

async function getClientIp() {
    const clientInfo = await fetchResponse(apiUrl + clientInfoPath)
    for (const element of clientInfo["headers"]) {
        if (element["name"] === "X-Real-IP") {
            return element["value"]
        }
    }
}

async function updateIpText() {
    let element = document.getElementById("client-ip");
    if (element) { element.innerText = `(${ipAddress})`; }
    element = document.getElementById("ip-addr");
    if (element) { element.value = ipAddress; }
}

async function updateStatus(path, timerTextId, statusTextId) {
    const statusInfo = await fetchResponse(path)

    const element = document.getElementById(timerTextId);
    if (!statusInfo["blocking"]) {
        await updateStatusText("disabled", statusTextId);
        if (element) {element.innerText = ` for ${Math.round(statusInfo["timer"])} seconds`;}
    } else {
        await updateStatusText("enabled", statusTextId);
        if (element) {element.innerText = "";}
    }
}

async function updateStatusText(text, statusTextId) {
    const element = document.getElementById(statusTextId);
    if (element) {
        element.innerText = text;
        element.className = text;
    }
}

async function updateStatusMain() {
    await updateStatus(statusPath, "timer-text-main", "status-text-main");
}

async function updateStatusClient() {
    await updateStatus(`${clientPath}/${ipAddress}`, "timer-text-client", "status-text-client");
}

window.onload = async function() {
    ipAddress = await getClientIp()
    await updateIpText()
    await updateStatusMain();
    await updateStatusClient()
    setInterval(updateStatusMain, 5000);
    setInterval(updateStatusClient, 5000);
}
