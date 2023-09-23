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


function linear_color_blend(colors,  control, control_max, control_min) {
    // takes a list of rgb colors, a variable parameter control and its limits and blends between all colors which are distributed equally in respect to control
    let i = 0;
    let color_out = [0, 0, 0];
    let color_amount = colors.length;

    let division_scaler = 10000;
    let control_normalized = (control - control_min) / (control_max - control_min) * division_scaler;
    let segment_size = division_scaler / (color_amount - 1);
    let control_wrapped = 0;
    let control_segment = Math.min(Math.floor(control_normalized / segment_size), (color_amount - 2));

    if (control < control_max) {
        control_wrapped = Math.min(Math.max(control_normalized % segment_size / segment_size, 0), 1);
    }
    else {
        control_wrapped = 1;
    }

    for (i = 0; i < 3; i++) {
        color_out[i] = colors[control_segment][i] + control_wrapped * (colors[control_segment + 1][i] - colors[control_segment][i]);
    }

    for (i = 0; i < 3; i++) {
        color_out[i] = Math.round(color_out[i] / Math.max.apply(null, color_out) * 255);
    }

    return 'rgb(' + color_out[0] + ', '  + color_out[1] + ', '+ color_out[2] + ')';
}

function update_html(data_struct) {
    let entries = (Object.entries(data_struct));

    for (let i = 0; i < entries.length; i++) {
        let actual_data = Object.entries(entries[i][1]);
        let name = actual_data[0][1];
        let data = Object.entries(actual_data[1][1]);

        for (let y = 0; y < data.length; y++)
        {
            try {
                document.getElementById('lbltxt' + data[y][0]).innerHTML =  data[y][0].replace('Consumption','').replace('Battery ','').replace('Leistung ','').replace('Input Voltage ','').replace('Energie', ' ').replace('Verbrauch ', '').replace('Netzbezug ', '');
                document.getElementById('lblval' + data[y][0]).innerHTML =  data[y][1]["value"] + " " + data[y][1]["unit"];
            }
            catch {

            }
        }
    }

    let soc = Math.floor(Number(data_struct[225]["Data"]["Battery SOC"]["value"]));
    let solar1 = Math.floor(Number(data_struct[100]["Data"]["Leistung String 1"]["value"]));
    let temp = Math.floor(Number(data_struct[24]["Data"]["Temperatur"]["value"]));

   
    document.getElementById('lblvalLeistung String 1').style.color = linear_color_blend([[255, 255, 255], [255, 141, 41], [255, 255, 0]], solar1, 4000, 0);
    document.getElementById('lblvalBattery SOC').style.color = linear_color_blend([[255, 0, 0],[0, 255, 0]], soc, 0, 100);

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
