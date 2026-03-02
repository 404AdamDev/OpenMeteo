let raindrop = null;
let canvas = null;

function init() {
    if (canvas) return;
    canvas = document.querySelector("#canvas");

    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
}

function raindropFX(status, bg) {
    if (status) {
        if (raindrop) return;

        init();

        raindrop = new RaindropFX({
            canvas: canvas,
            spawnSize: [30, 80],
            spawnInterval: [0.1, 0.2],
            mistBlurStep: 1,
            dropletsPerSecond: 1000,
            background: bg ? bg : "https://www.shutterstock.com/shutterstock/videos/10016534/thumb/1.jpg?ip=x480",
        });

        raindrop.start();

        window.addEventListener("resize", tamanhoTela);
    } else {
        if (!raindrop) return;
        
        raindrop.stop();
        raindrop = null;

        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        window.removeEventListener("resize", tamanhoTela);
    }
}

function tamanhoTela() {
    if (!raindrop) return;

    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    raindrop.resize(rect.width, rect.height);
}

window.raindropFX = raindropFX