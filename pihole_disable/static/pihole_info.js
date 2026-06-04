const statusPath = "/status"
const clientPath = "/client"

async function fetchResponse(path) {
    const response = await fetch(path);
    return await response.json();
}

async function updateIpText() {
    const clientInfo = await fetchResponse(clientPath)
    const ipText = `(${clientInfo["ip"]})`

    let element = document.getElementById("client-ip");
    if (element) { element.innerText = ipText; }
    element = document.getElementById("ip-addr");
    if (element) { element.value = ipText; }
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
    await updateStatus(clientPath, "timer-text-client", "status-text-client");
}

window.onload = async function() {
    await updateIpText()
    await updateStatusMain();
    await updateStatusClient()
    setInterval(updateStatusMain, 5000);
    setInterval(updateStatusClient, 5000);
}
