function createGroup(){
            let host = window.location.origin;
        $.ajax({
            type:"GET",
            url: host + "/Ajax-handler",
            data: {"action": "create_group", "id": id },
            success: function(data){
                console.log(data);
                let result = JSON.parse(data);
                $('#results').text(result);

            },
            error: function (e) {
                console.log(e); // logging the error object to console
            },
        })
}
function joinGroup(){
    let host = window.location.origin;
    let group = $('#groupID').val();
    if(group && group != null && group != '')
        $.ajax({
            type:"GET",
            url: host + "/Ajax-handler",
            data: {"action": "join_group", "id": id, "groupID": group},
            success: function(data){
                console.log(data);
                let result = data;
                $('#results').text(result);

            },
            error: function (e) {
                console.log(e); // logging the error object to console
                alert(e)
            },
        })
    else alert("Please fill out group invite code")
}