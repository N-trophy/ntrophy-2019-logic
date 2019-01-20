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