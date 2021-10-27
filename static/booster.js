var test;
function getSet(setcode){
    console.log(setcode);
    console.log("test");
    let host = window.location.origin;
    $.ajax({
        type:"GET",
        url: host + "/Ajax-handler",
        data: {"action": "get_booster", "setcode": setcode},
        success: function(data){
            console.log(data);
            test = data;
            let obj = JSON.parse(data);
            console.log("parsed")
            console.log(obj)
            result = "";
            for (const objKey in obj) {
                result += '<button value="' + obj[objKey][0] + '" onclick="saveCards(this.value)">' + obj[objKey][1] + '</button>';
            }
            $('#results').html(result);

        },
        error: function (e) {
            console.log(e); // logging the error object to console
        },
    })
}


function saveCards(cardUUID) {
    let host = window.location.origin;
    console.log(cardUUID);
    cards = {};
    cards[cardUUID] = 1;

    $.ajax({
        type: "GET",
        url: host + "/Ajax-handler",
        data: {"action": "save_cards", "id": 'DUMMY', "groupID": '2WN6SIM', "cards": JSON.stringify(cards)},
        success: function (data) {
            console.log(data)
            console.log("Cards Saved!");
        }
    })
}

function savePoints(points) {
    let host = window.location.origin;
    console.log(points);

    $.ajax({
        type: "GET",
        url: host + "/Ajax-handler",
        data: {"action": "save_points", "points": points},
        success: function (data) {
            console.log(data);
            console.log("Cards Saved!");
        }
    })
}
