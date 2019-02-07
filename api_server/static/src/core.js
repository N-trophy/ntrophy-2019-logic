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

function readFloat(str) {
    console.log("Reading position: " + str.trim());
    let num = Number(str.trim());
    if (isNaN(num)) {
        console.warn("Is not number");
        return null;
    }
    return Math.round(num * 100) / 100;
}

function readId(str) {
    str = str.trim();
    console.log("Reading id: " + str);
    if (str.indexOf('.') > -1) {
        console.warn("Id is not expected to have floating point");
        return null;
    }

    if (str.charAt(0) == '"' && str.charAt(str.length - 1) == '"') {
        str = str.slice(1, -1);
    }

    let i = str.indexOf('-');
    if (i < 0) {
        console.warn("Didn't find '-' in id");
        return null;
    }

    let num1 = Number(str.slice(0, i));
    let num2 = Number(str.slice(i + 1));

    if (isNaN(num1) || isNaN(num2)) {
        console.warn("Not numbers in id");
        return null;
    }
    return '"' + num1 + '-' + num2 + '"';
}

function parseCSV(infile) {
    let lines = infile.split("\n");
    let result = [];

    for (let i = 0; i < lines.length; i++) {
        var currentline = lines[i].split(",");
        if (currentline.length == 0) continue;
        if (currentline[currentline.length - 1].trim() == "")
            currentline = currentline.slice(0, -1);
        if (currentline.length == 0) continue;

        if (place_anywhere) {
            if (currentline.length != 2)
                return null;
        } else {
            if (currentline.length != 4)
                return null;
        }

        var point = [];
        point.push(readFloat(currentline[0]));
        point.push(readFloat(currentline[1]));
        if (place_anywhere == false) {
            point.push(readId(currentline[2]));
            point.push(readId(currentline[3]));
        }
        if (point[0] === null || point[1] === null) return null;
        if (place_anywhere == false)
            if (point[2] === null || point[3] === null) return null;

        result.push(point);
    }
    return result;
}

function receivedText(e) {
    var loaded_data = parseCSV(fr.result);
    console.log(loaded_data);

    if (loaded_data === null) {
        let info_elem = document.getElementById('loaded-info');
        info_elem.innerHTML = "<b>Chyba při načítání. (Špatný formát)</b><br><br>Pokud byste měli pocit, že váš soubor má správný formát, kontaktujte organizátory.";
        return;
    }

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
    info_elem.innerHTML = "Načteno:";
    for (let i = 0; i < loaded_data.length; i++) {
        info_elem.innerHTML += '<br>';
        info_elem.innerHTML += loaded_data[i][0];
        info_elem.innerHTML += ', ';
        info_elem.innerHTML += loaded_data[i][1];
        if (place_anywhere == false) {
            info_elem.innerHTML += ', ';
            info_elem.innerHTML += loaded_data[i][2];
            info_elem.innerHTML += ', ';
            info_elem.innerHTML += loaded_data[i][3];
        }
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
    info_elem.innerHTML = "Hodnota vzdálenostní funkce: ...";
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
    info_elem.innerHTML = "Odevzdali jste řešení.<br>Hodnota vzdálenostní funkce: ...";
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

function after_eval(res) {
    score = res.data.score;
    remaining_evals = res.data.remaining;
    update_remaining_evals_text();

    score_elem = document.getElementById('score');
    score_elem.innerText = score;
    document.getElementById('eval-info').innerHTML = "Hodnota vzdálenostní funkce: " + score;
}

function set_style_id(id, style) {
    let elem = document.getElementById(id);
    if (elem)
        elem.style = style;
}

function after_submit(res) {
    score = res.data.score;

    score_elem = document.getElementById('score');
    score_elem.innerText = score;
    document.getElementById('submit-info').innerHTML = "Odevzdali jste řešení.<br>Hodnota vzdálenostní funkce: " + score;
    set_style_id('submit-menu', "display: none!important;");
    set_style_id('submit-menu-small', "display: none!important;");
    set_style_id('next-level-menu', "display: block;");
    set_style_id('next-level-menu-small', "display: block;");
    set_style_id('next-level-menu-small', '')

    set_style_id('next-level', 'display: block;');
}

function resize_level_status() {
    for (let i = 1; i <= 10; i++) {
        set_style_id('status-' + i, '');
    }
    var max_width = 0;
    for (let i = 1; i <= 10; i++) {
      let width = document.getElementById("status-" + i).offsetWidth;
      if (width > max_width)
        max_width = width;
    }
    for (let i = 1; i <= 10; i++) {
        set_style_id('status-' + i, 'width: ' + max_width + 'px;');
    }
}
