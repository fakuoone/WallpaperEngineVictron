const xhr = new XMLHttpRequest();
xhr.withCredentials = false;

xhr.addEventListener("readystatechange", function () {
    if (this.readyState === this.DONE) {
        update_html(JSON.parse(this.responseText));
    }
   
});

function get_data() {
    setTimeout(get_data, 1000);
    xhr.open("GET", "http://192.168.178.41:9999");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(null);
}

function get_temp_color(temperature) {
    let normal_dist = Math.exp(-0.5 * ((temperature - 20) / 8)**2);  // 1 = grün, 0 = rot
    let red = Math.round(255 * (1 - normal_dist));
    let green = Math.round(255 * normal_dist);

    red = red / Math.max(red, green) * 255;
    green = green / Math.max(red, green) * 255;

    return 'rgb(' + red + ', '  + green + ', 0)';
    // F08373 bright pastelle red and CEFF47 bright green (triade)
}

function get_soc_color(soc) {
    let red = 255 * (1 - soc / 100);
    let green = 255 * soc / 100;

    red = red / Math.max(red, green) * 255;
    green = green / Math.max(red, green) * 255;

    return 'rgb(' + red + ', '  + green + ', 0)';
}

function update_html(data_struct) {
    let entries = (Object.entries(data_struct));

    for (let i = 0; i < entries.length; i++) {
        let actual_data = Object.entries(entries[i][1]);
        //console.log(actual_data);
    
        let name = actual_data[0][1];
        let data = Object.entries(actual_data[1][1]);

        for (let y = 0; y < data.length; y++)
        {
            //console.log('lbl' + data[y][0]);
            try {
                document.getElementById('lbltxt' + data[y][0]).innerHTML =  data[y][0].replace('Consumption','').replace('Battery ','').replace('Leistung ','').replace('Input Voltage ','').replace('Energie', ' ').replace('Verbrauch ', '').replace('Netzbezug ', '');
                document.getElementById('lblval' + data[y][0]).innerHTML =  data[y][1]["value"] + " " + data[y][1]["unit"];
            }
            catch {

            }
        }
    }

    let soc = Math.floor(Number(data_struct[225]["Data"]["Battery SOC"]["value"]));
    let temp = Math.floor(Number(data_struct[24]["Data"]["Temperatur"]["value"]));
   
    document.getElementById('lblvalBattery SOC').style.color = get_soc_color(soc);
    document.getElementById('lblvalTemperatur').style.color = get_temp_color(temp);

    if (Number(data_struct[225]["Data"]["Battery Power"]["value"] > 50)) {
        document.getElementById('battery_arrow').style.color = '#00ff00'
        document.getElementById('battery_arrow').innerHTML = 'lädt'
    }
    else if (Number(data_struct[225]["Data"]["Battery Power"]["value"] < -50)){
        document.getElementById('battery_arrow').style.color = '#ff0000'
        document.getElementById('battery_arrow').innerHTML = 'entlädt'
    }
    else {
        document.getElementById('battery_arrow').style.color = '#ff0000'
        document.getElementById('battery_arrow').innerHTML = ''
    }
}

get_data();