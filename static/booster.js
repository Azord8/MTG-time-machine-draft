var test;
function getSet(setcode){
    console.log(setcode);
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
                result += '<div><div class="card text-center"><div class="card-body"><h4>' + obj[objKey]['Name'] + '</h4>';
                if(typeof obj[objKey]['Mana cost'] !== "undefined" )
                    result+= '<p>' + obj[objKey]['Mana cost'] + '</p>';
                result += '<p>' + obj[objKey]['Rarity'] + '</p>';
                if(typeof obj[objKey]['Text'] !== "undefined" )
                    result += '<p class="card-text">' + obj[objKey]['Text'] + '</p>';
                result+= '</div></div></div>'
                // result += '<button value="' + obj[objKey][0] + '" onclick="saveCards(this.value)">' + obj[objKey][1] + '</button>';
            }
            $('.owl-carousel1').html(result);
            carousels();

        },
        error: function (e) {
            console.log(e); // logging the error object to console
        },
    })
}


function saveCards(cardUUID) {
    let host = window.location.origin;
    let group = $('#groupID').val();
    console.log(cardUUID);
    cards = {};
    cards[cardUUID] = 1;

    $.ajax({
        type: "GET",
        url: host + "/Ajax-handler",
        data: {"action": "save_cards", "id": id, "groupID": group, "cards": JSON.stringify(cards)},
        success: function (data) {
            console.log(data)
            console.log("Cards Saved!");
        }
    })
}

function savePoints(points) {
    let host = window.location.origin;
    let group = $('#groupID').val();
    console.log(points);

    $.ajax({
        type: "GET",
        url: host + "/Ajax-handler",
        data: {"action": "save_points", "id": id, "groupID": group, "points": points},
        success: function (data) {
            console.log(data);
            console.log("Points work");
        }
    })
}

var carousels = function () {
    $(".owl-carousel1").owlCarousel({
        loop: true,
        center: true,
        margin: 0,
        responsiveClass: true,
        nav: false,
        dots:false,
        animateIn: true,
        responsive: {
            0: {
              items: 2,
            },
            680: {
              items: 3,
            },
            1000: {
              items: 5,
            },
            1600: {
              items: 7,
            }
        }
    });
};

carousels();

