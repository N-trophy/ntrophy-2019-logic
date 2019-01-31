function init(level_id){
    window.onload = () => {
        axios.get('/level/'+level_id+'/graph')
            .then(response => {
                init_graph(level_id, response.data)
            })
            .catch(err => {
                console.error(err)
            });
    }
}

function toggleNav() {
    var x = document.getElementById("navDemo");
    if (x.className.indexOf("w3-show") == -1) {
      x.className += " w3-show";
    } else { 
      x.className = x.className.replace(" w3-show", "");
    }
  }