// GUI functions
function set_active_task(num_of_tasks, task_id) {
    for(let i = 1; i<=num_of_tasks; i++) {
        document.getElementById("task"+i).classList.remove("closed", "active");
    }
    for(let i = 1; i<task_id; i++) {
        document.getElementById("task"+i).classList.add("closed");
    }
    document.getElementById("task"+task_id).classList.add("active");
}

function click_task(task) {
    axios.get('/graph?task_number='+task)
        .then(response => {
            set_active_task(8, task);
            update_graph(response.data)
        })
        .catch(err => {
            console.error(err)
        });
}

window.onload = () => {
    init_sigma()
    click_task(1);

    for(let i=1; i<=8; i++) {
        document.getElementById("task"+i).onclick = () => {
            click_task(i);
        }
    }
}