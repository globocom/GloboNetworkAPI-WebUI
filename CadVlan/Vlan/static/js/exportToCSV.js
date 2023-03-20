const download = function (text, fileName) {
    const link = document.createElement('a');
    link.setAttribute('href', `data:text/csv;charset=utf-8,${encodeURIComponent(text)}`);
    link.setAttribute('download', fileName);

    link.style.display = 'none';
    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);
    $(".loading").hide()
};

const startSearch = 0

function exportToCSV(method, url, fileName) {
    let request = new XMLHttpRequest()
    let cookies = `;${document.cookie}`;
    let cookiesSplited = cookies.split(`; csrftoken=`)
    let token = null
    if (cookiesSplited.length == 2) {
        token = cookiesSplited.pop().split(';').shift()
    }

    // GET DATA FROM THE FORM TO SUBMIT NEW SEARCH
    let ipVersion = document.getElementById("ip_v4").value
    let number = document.getElementById("id_number").value
    let name = document.getElementById("id_name").value
    let environment = document.getElementById("id_environment").value
    let netType = document.getElementById("id_net_type").value
    let oct1 = document.getElementsByName("oct1")[0].value
    let oct2 = document.getElementsByName("oct2")[0].value
    let oct3 = document.getElementsByName("oct3")[0].value
    let oct4 = document.getElementsByName("oct4")[0].value
    let oct5 = document.getElementsByName("oct5")[0].value
    let oct6 = document.getElementsByName("oct6")[0].value
    let oct7 = document.getElementsByName("oct7")[0].value
    let oct8 = document.getElementsByName("oct8")[0].value
    let oct9 = document.getElementsByName("oct9")[0].value
    let subnet = ""

    if (ipVersion == environment == netType == number.length == name.length == oct1.length == oct2.length == oct3.length == oct4.length == oct5.length == oct6.length == oct7.length == oct8.length == 0){
        window.alert("Por favor faça uma busca mais específica. Buscas com todos os filtros em branco não são elegíveis para uma exportação de arquivos CSV.")
        let btnExport = document.getElementById("exportCSV")

        btnExport.setAttribute("disabled", "true")
        btnExport.setAttribute("aria-disabled", "true")
        btnExport.classList.add("ui-state-disabled", "ui-button-disabled")
        return
    }

    let subnet_1 = document.getElementById("id_subnet_1")
    let subnet_0 = document.getElementById("id_subnet_0")
    if (subnet_1.checked){
        subnet = "1"
    } else if (subnet_0.checked){
        subnet = "0"
    }

    let exact = document.getElementById("id_iexact").checked.toString()

    let entries = 99999

    if (!window.confirm("Esta ação pode levar algum tempo, não atualize a página.")){
        return
    }
    $(".loading").show()

    // SUBMIT FORM TO GENERATE A CSV FILE
    let fullUrl = `${url}?csrfmiddlewaretoken=${token}&networkv4=&networkv6=&ip_version=${ipVersion}&number=${number}&name=${name}&environment=${environment}&net_type=${netType}&oct1=${oct1}&oct2=${oct2}&oct3=${oct3}&oct4=${oct4}&oct5=${oct5}&oct6=${oct6}&oct7=${oct7}&oct8=${oct8}&oct9=${oct9}&subnet=${subnet}&iexact=${exact}&sEcho=2&iColumns=8&sColumns=&iDisplayStart=0&iDisplayLength=${entries}`//&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&iSortingCols=0&bSortable_0=false&bSortable_1=false&bSortable_2=true&bSortable_3=true&bSortable_4=true&bSortable_5=true&bSortable_6=true&bSortable_7=false&_=1678200991699`
    request.open(method, fullUrl)
    request.send()
    request.responseType = "json"
    request.onload = () => {
        if (request.readyState == 4 && request.status == 200) {
            const response = request.response
            let jsonData = response.jsonData
            if (jsonData.length === 0){
                $(".loading").hide()
                window.alert("Houve um erro ao exportar os dados. Refaça a busca.")
                window.location.reload()
                return
            }
            let csvData = objectToCSV(jsonData)
            download(csvData, `${fileName}.csv`)
        } else {
            $(".loading").hide()
            console.log(`Error: ${request.status}`)
        }
    }
}

function objectToCSV(data) {
    var rows = []

    var headers = Object.keys(data[0])

    rows.push(headers.join(','))

    for (var row of data) {
        var values = headers.map(header => {
            let val = row[header]
            if (header === "network4") {
                if (val.length === 0) {
                    return "-"
                }
                if (Array.isArray(val)) {
                    let redesv4 = ""
                    for (var arrObject of val) {
                        redeV4 = arrObject['Rede_IPV4']
                        redesv4 += `${redeV4} | `
                    }
                    return `"${redesv4.slice(0, -2)}"`
                }
            }
            if (header === "network6") {
                if (val.length === 0) {
                    return "-"
                }
                if (Array.isArray(val)) {
                    let redesv6 = ""
                    for (var arrObject of val) {
                        redeV6 = arrObject['Rede_IPV6']
                        redesv6 += `${redeV6} | `
                    }
                    return `"${redesv6.slice(0, -2)}"`
                }
            }
            return `"${val}"`
        })
        rows.push(values.join(','))
    }

    return rows.join('\n')
}

window.onload = function () {
    // const pag =

    var targetNode = document.getElementById('table_body');


    var config = {
        attributes: true,
        childList: true,
        subtree: true
    };

    var observer = new MutationObserver(callback);


    observer.observe(targetNode, config);
}

// Callback function to execute when mutations are observed
var callback = function (mutationsList) {
    let btnExport = document.getElementById("exportCSV")
    for (var mutation of mutationsList) {
        if (mutation.type == 'childList') {
            let tableBody = document.getElementById("table_body")
            if (tableBody.childNodes[0].childNodes[0].textContent == "Nenhum registro encontrado.") {
                btnExport.setAttribute("disabled", "true")
                btnExport.setAttribute("aria-disabled", "true")
                btnExport.classList.add("ui-state-disabled", "ui-button-disabled")
                return
            }
            let tableBodyLength = 0
            if (tableBody === null) {
                tableBodyLength = 0
            } else {
                tableBodyLength = tableBody.childNodes.length
            }
            if (tableBodyLength === 0) {
                btnExport.setAttribute("disabled", "true")
                btnExport.setAttribute("aria-disabled", "true")
                btnExport.classList.add("ui-state-disabled", "ui-button-disabled")

                return
            } else {
                btnExport.classList.remove("ui-state-disabled", "ui-button-disabled")
                btnExport.setAttribute("aria-disabled", "false")
                btnExport.setAttribute("onclick", "exportToCSV('GET', '/vlan/find/0', 'CadVlan_export')")
                btnExport.removeAttribute("disabled")
                return
            }

        } else if (mutation.type == 'attributes') {
            console.log('The ' + mutation.attributeName + ' attribute was modified.');
        }
    }
};
