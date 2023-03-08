const download = function (text, fileName) {
    const link = document.createElement('a');
    link.setAttribute('href', `data:text/csv;charset=utf-8,${encodeURIComponent(text)}`);
    link.setAttribute('download', fileName);

    link.style.display = 'none';
    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);
};

function exportToCSV(method, url, fileName){
    let request = new XMLHttpRequest()
    let cookies = `;${document.cookie}`;
    let cookiesSplited = cookies.split(`; csrftoken=`)
    let token = null
    if (cookiesSplited.length ==2) {
        token = cookiesSplited.pop().split(';').shift()
    }

    let fullUrl = `${url}?csrfmiddlewaretoken=${token}&networkv4=&networkv6=&ip_version=0&number=&name=&environment=0&net_type=0&oct1=&oct2=&oct3=&oct4=&oct5=&oct6=&oct7=&oct8=&oct9=&subnet=0&iexact=false&sEcho=2&iColumns=8&sColumns=&iDisplayStart=0&iDisplayLength=25&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&iSortingCols=0&bSortable_0=false&bSortable_1=false&bSortable_2=true&bSortable_3=true&bSortable_4=true&bSortable_5=true&bSortable_6=true&bSortable_7=false&_=1678200991699`
    request.open(method, fullUrl)
    request.send()
    request.responseType = "json"
    request.onload = () => {
        if (request.readyState == 4 && request.status == 200){
            const response = request.response
            let jsonData = response.jsonData
            let csvData = objectToCSV(jsonData)
            download(csvData, `${fileName}.csv`)
        } else {
            console.log(`Error: ${request.status}`)
        }
    }
}

function objectToCSV(data){
    var rows = []

    var headers = Object.keys(data[0])

    rows.push(headers.join(','))

    for (var row of data){
        var values = headers.map(header => {
            let val = row[header]
            if (header === "network4"){
                if (val.length === 0){
                    return "-"
                }
                if (Array.isArray(val)){
                    let redesv4 = ""
                    for (var arrObject of val){
                        redeV4 = arrObject['Rede_IPV4']
                        redesv4 += `${redeV4} | `
                    }
                    return `"${redesv4.slice(0, -2)}"`
                }
            }
            if (header === "network6"){
                if (val.length === 0){
                    return "-"
                }
                if (Array.isArray(val)){
                    let redesv6 = ""
                    for (var arrObject of val){
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