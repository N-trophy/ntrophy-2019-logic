function toggleNav() {
    var x = document.getElementById("navDemo");
    if (x.className.indexOf("w3-show") == -1) {
      x.className += " w3-show";
    } else { 
      x.className = x.className.replace(" w3-show", "");
    }
}

const fr = new FileReader();
function parseUploadedFile() {
    if (!window.File || !window.FileReader || !window.FileList || !window.Blob) {
        alert('The File APIs are not fully supported in this browser.');
        return;
    }

    let input = document.getElementById('upload-file');
    if (!input) {
        alert("Couldn't find the file input element.");
    }
    else if (!input.files) {
        alert("Zdá se, že váš prohlížeč nepodporuje nutnou funkcionalitu.");
    }
    else if (!input.files[0]) {
        alert("Vyberte soubor předtím, než stisknete 'Odeslat'");
    }
    else {
        let file = input.files[0];
        fr.onload = receivedText;
        fr.readAsText(file);
    }
}
function isNumber(num) {
    return true;
}

function parseCSV(infile) {
    let lines = infile.split("\n");
    let result = [];

    for (let i = 0; i < lines.length; i++) {

        var currentline = lines[i].split(",");
        if (currentline.length < 2) continue;

        var point = [];
        point.push(parseFloat(currentline[0]));
        point.push(parseFloat(currentline[1]));
        if (!isNaN(point[0]) && !isNaN(point[1])) {
            result.push(point);
        }
    }
    return result;
}
function receivedText(e) {
    var loaded_data = parseCSV(fr.result);
    console.log(loaded_data);

    while(true){
        let keys = Object.keys(nodes._data).filter(key => key[0] == 's')
        if (keys.length == 0) break
        delete_node(keys[0])
    }
    data_to_send = {}
    for (let i = 0; i<loaded_data.length;i++){
        data = loaded_data[i]
        if (station_counter >= max_number_of_stations) break;
        let n = new_station_node(data[0], data[1])
        data_to_send[n.id] = { x:data[0], y:data[1] }
        if (place_anywhere == false) {
            data_to_send[n.id].edge_a = data[2]
            data_to_send[n.id].edge_b = data[3]
        }
        nodes.add([n])
        station_counter++
    }

    let info_elem = document.getElementById('loaded-info');
    info_elem.innerHTML = "Načteno:<br>";
    for (let i = 0; i < loaded_data.length; i++) {
        info_elem.innerHTML += loaded_data[i][0];
        info_elem.innerHTML += ", ";
        info_elem.innerHTML += loaded_data[i][1];
        info_elem.innerHTML += "<br>";
    }
}

function try_eval() {
    document.getElementById('eval-send').disabled = true;

    let info_elem = document.getElementById('eval-info');
    info_elem.style="display: block";
    if (station_counter != max_number_of_stations) {
        info_elem.innerHTML = "Zadejte přesně ";
        if (max_number_of_stations == 1)
            info_elem.innerHTML += "1 nemocnici";
        else
            info_elem.innerHTML += max_number_of_stations + " nemocnic";
        info_elem.innerHTML += " (zadali jste " + station_counter + " nemocnic).";
        return;
    }
    info_elem.innerHTML = "Score: ...";
    eval();
}

function try_submit() {
    document.getElementById('submit-send').disabled = true;

    let info_elem = document.getElementById('submit-info');
    info_elem.style="display: block";
    if (station_counter != max_number_of_stations) {
        info_elem.innerHTML = "Zadejte přesně ";
        if (max_number_of_stations == 1)
            info_elem.innerHTML += "1 nemocnici";
        else
            info_elem.innerHTML += max_number_of_stations + " nemocnic";
        info_elem.innerHTML += " (zadali jste " + station_counter + " nemocnic).";
        return;
    }
    info_elem.innerHTML = "Odevzdali jste řešení.<br>Score: ...";
    submit();
}

function update_remaining_evals_text() {
    let objs = document.getElementsByName("remaining_evals_text");
    if (remaining_evals == 0) {
        document.getElementById("eval-send").style = "display: none;";
    }
    for (let i = 0; i < objs.length; i++) {
        let rem_eval_obj = objs[i];
        if (remaining_evals == 0)
            rem_eval_obj.innerHTML = "Pro tuto úroveň už nemůžete využít žádné vyhodnocení.";
        else if (remaining_evals > 0)
            rem_eval_obj.innerHTML = "Pro tuto úroveň můžete využít ještě " + remaining_evals + " vyhodnocení.";
        else
            rem_eval_obj.innerHTML = "Pro tuto úroveň můžete využít neomezeně vyhodnocení.";
    }
}
