// -- Coisas da visualização dos dados
const wmoItens = { // Descrições wmo (Códigos de Interpretação Climática)
    0: "Céu limpo",
    1: "Principalmente limpo", 2: "Parcialmente nublado", 3: "Nublado",
    45: "Névoa", 48: "Névoa depositante de orvalho",
    51: "Chuvisco Leve", 53: "Chuvisco Moderado", 55: "Chuvisco de intensidade densa",
    56: "Chuvisco Congelante Leve", 57: "Chuvisco Congelante Denso",
    61: "Chuva Leve", 63: "Chuva Moderada", 65: "Chuva de intensidade forte",
    66: "Chuva Congelante Leve", 67: "Chuva Congelante Forte",
    71: "Neve Leve", 73: "Neve Moderada", 75: "Neve de intensidade forte",
    77: "Grãos de neve",
    80: "Pancadas de chuva Leve", 81: "Pancadas de chuva Moderada", 82: "Pancadas de chuva Violenta",
    85: "Pancadas de neve Leve", 86: "Pancadas de neve Forte",
    95: "Tempestade Leve ou moderada",
    96: "Tempestade com granizo leve", 99: "Tempestade com granizo forte"
};

function iconeWmo(code) { // Encontra o icone da temperatura
    if (code === 0) return "icon-sun";
    if ([1, 2, 3].includes(code)) return "icon-cloud-sun";
    if ([45, 48].includes(code)) return "icon-cloud-fog";
    if ([51, 53, 55, 61, 63, 65, 80, 81, 82].includes(code)) return "icon-cloud-rain";
    if ([71, 73, 75, 77, 85, 86].includes(code)) return "icon-snowflake";
    if ([95, 96, 99].includes(code)) return "icon-cloud-lightning";
    return "icon-cloud";
}


// -- Sistema de troca de temas
function isNoite(time) {
    const hora = new Date(time).getHours()
    return (hora >= 18 || hora < 6)
}

function climaAtual(code) { // Pega o clima atual com base no codigo da api
    if ([71, 73, 75, 77, 85, 86].includes(code)) {
        return "neve"
    } else if ([51, 53, 55, 61, 63, 65, 80, 81, 82].includes(code)) {
        return "chuva"
    } else {
        return "limpo"
    }
}

function mudarTema(atual) {
    const noite = isNoite(atual.time)
    const clima = climaAtual(atual.weathercode)
    const canvas = document.querySelector("#canvas");
    let img = ""

    if (clima === "chuva") {
        img = noite ? "assets/rain-night.jpg" : "assets/rain-day.jpg"
        controlarChuva(true, img)
    } else if (clima === "neve") {
        img = noite ? "assets/snow-night.jpg" : "assets/snow-day.jpg"
        if (canvas) {
            canvas.style.visibility = "hidden";
            controlarChuva(false)
        }
    } else {
        img = noite ? "assets/night.jpg" : "assets/sunny-day.jpg"
        if (canvas) {
            canvas.style.visibility = "hidden";
            controlarChuva(false)
        }
    }

    document.body.style.backgroundImage = `url('${img}')`
    document.body.style.backgroundSize = "cover"
    document.body.style.backgroundPosition = "center"

    // Ajusta a opacidade do overlay com base no tema
    document.body.style.setProperty("--overlay-opacity", noite ? "0.9" : "0.6")
}


// -- Sistema geral
function updateTela(data, cidade, geoLoc) {
    const climaAtual = data.current_weather
    const wmoCode =  climaAtual.weathercode
    const tempo = new Date(climaAtual.time).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })

    document.getElementById("temp-text").innerHTML = `${Math.round(climaAtual.temperature)}<span>°C</span>`
    document.getElementById("temp-icon").className = `lucide ${iconeWmo(wmoCode)} weather-icon`
    document.getElementById("city-text").innerHTML = cidade
    document.getElementById("extra-text").innerHTML = `${tempo} | Lat: ${geoLoc.lat.toFixed(2)}, Lon: ${geoLoc.lon.toFixed(2)}`

    document.getElementById("wmo-text").innerText = wmoItens[wmoCode] || "Condição desconhecida"
    document.getElementById("timezone-text").innerText = data.timezone
    document.getElementById("wind-text").innerText = `${climaAtual.windspeed} km/h`
    
    mudarTema(climaAtual)
}

async function postData(data) {
    console.log("ENVIANDO DADOS:", data)
    try {
        const resposta = await fetch("http://127.0.0.1:8000/api/v1/weather/salvar-clima", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        if (!resposta.ok) throw new Error(`API retornou ${resposta.status}`)
        
        const respostaData = await resposta.json()
        console.log("Dados enviados com sucesso:", respostaData)
    } catch (error) {
        console.error("[ERROR] Falha ao enviar dados para o servidor:", error)
    }
}

async function getClima(lat, lon, cidade) { // Busca os dados climáticos usando a API do Open-Meteo
    try {
        const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&hourly=temperature_2m,wind_speed_10m,weather_code,relative_humidity_2m&current_weather=true&timezone=auto`
        const resposta = await fetch(url)
        if (!resposta.ok) throw new Error(`API retornou ${resposta.status}`)

        const data = await resposta.json()
        updateTela(data, cidade, {lat, lon})
        postData({ cidade: cidade, clima_data: data })
    } catch (error) {
        console.error("[ERROR] Falha ao buscar dados climáticos:", error)
        alert("Ops... Não foi possível carregar os dados climáticos. Verifique sua conexão ou tente novamente mais tarde.")
    }
}

async function acharCidade(nome) { // Busca a cidade e suas coordenadas usando a API geocoding do Open-Meteo
    try {
        const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(nome)}&count=1&language=pt&format=json`
        const resposta = await fetch(url)
        if (!resposta.ok) throw new Error(`API retornou ${resposta.status}`)

        const data = await resposta.json()
        if (data.results) {
            const resultado = data.results[0]
            getClima(resultado.latitude, resultado.longitude, resultado.name)
        } else {
            alert("Cidade não encontrada. Verifique o nome e tente novamente.");
        }
    } catch (error) {
        console.error("[ERROR] Falha na busca da cidade:", error)
        alert(`Ops... Não foi possível encontrar a cidade ${nome ? nome : "DESCONHECIDO"}. Tente novamente mais tarde!`)
    }
}


// -- Eventos
document.querySelector('.search-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const cidade = document.getElementById('search-city-box').value.trim();
    
    if (cidade) {
        acharCidade(cidade);
    }
});

window.onload = () => { // Carrega o clima de Contagem por padrão
    acharCidade("Contagem")
}