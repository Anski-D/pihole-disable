const pathStatusMain = "/status"
const pathStatusClient = "/client"
const pathInfoClient = "/info/client"
const apiUrl = "https://pihole.dacyho.me/api"
let ipAddress

async function fetchResponse(path) {
    const response = await fetch(path);
    return await response.json();
}

async function getClientIp() {
    const clientInfo = await fetchResponse(apiUrl + pathInfoClient)
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

async function updateStatus(statusInfo, timerTextId, statusTextId) {
    const element = document.getElementById(timerTextId);
    if (!statusInfo["blocking"]) {
        await updateStatusText("disabled", statusTextId);
            if (element) {
                if (statusInfo["timer"] > 0) {
                    element.innerText = ` for ${Math.round(statusInfo["timer"])} seconds`;
                    if (statusTextId === "status-text-client") {
                        element.innerHTML += ` <a id="cancel-link" href="/enable/${ipAddress}">Cancel</a>`;
                    }
                }
                else {
                    element.innerText = "";
                }
            }
    } else {
        await updateStatusText("enabled", statusTextId);
        if (element) { element.innerText = ""; }
    }
}

async function updateStatusText(text, statusTextId) {
    const element = document.getElementById(statusTextId);
    if (element) {
        element.innerText = text;
        element.className = text;
    }
}

async function updatePiholeInfo() {
    const statusInfoMain = await fetchResponse(pathStatusMain)
    const statusInfoClient = await fetchResponse(`${pathStatusClient}/${ipAddress}`)

    if (!statusInfoMain["blocking"]) {
        statusInfoClient["blocking"] = false
        statusInfoClient["timer"] = 0
    }

    await updateStatus(statusInfoMain, "timer-text-main", "status-text-main");
    await updateStatus(statusInfoClient, "timer-text-client", "status-text-client");
}

window.onload = async function() {
    ipAddress = await getClientIp()
    await updateIpText()
    await updatePiholeInfo();
    setInterval(updatePiholeInfo, 5000);
}
