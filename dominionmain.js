var playerCount = 2;

var supply = {
    copper: 60-(playerCount*7),
    silver: 40,
    gold: 30,
    estate: 12,
    duchy: 12,
    province: 4*playerCount,
    curse: 10*(playerCount-1),

    //the beginner ten cards
    cellar: 10,
    market: 10,
    merchant: 10,
    militia: 10,
    mine: 10,
    moat: 10,
    remodel: 10, 
    smithy: 10,
    village: 10,
    workshop: 10,
    trash: []
}



function shuffleArray(array) {
  var i = 0
    , j = 0
    , temp = null

  for (i = array.length - 1; i > 0; i -= 1) {
    j = Math.floor(Math.random() * (i + 1))
    temp = array[i]
    array[i] = array[j]
    array[j] = temp
  }
}


function Player(name) {
    this.name = name;
    this.money = 0;
    this.buys = 0;
    this.actions = 0;
    this.cards = 0;
    this.hand = [];
    this.deck = [];
    this.discard = [];
    this.play = [];

    for (var i = 0; i < 3; i++) {
        this.deck.push(new Card("estate", 2, ["victory"]));
    }
    for (var i = 0; i < 7; i++) {
        this.deck.push(new Card("copper", 0, ["treasure"]));
    }

    shuffleArray(this.deck, true);
}

Player.prototype.shuffleDiscard = function() {
    this.deck = this.discard;
    this.discard = [];
    shuffleArray(this.deck, true);
}

Player.prototype.draw = function(amount) {
    for (var i = 0; i < amount; i++) {
        if (this.deck.length == 0) {
            this.shuffleDiscard();
        }
        this.hand.push(this.deck.pop());
    }
}

Player.prototype.cleanUp = function() {
    while (this.hand.length > 0) {
        temp = this.hand.pop();
        console.log(temp);
        this.discard.push(temp);
    }
    while (this.play.length > 0) {
        temp = this.play.pop();
        console.log(temp);
        this.discard.push(temp);
    }
}

Player.prototype.gain = function(card) {
    if (supply[card.name] > 0) {
        supply[card.name] -= 1;
        document.getElementById(card.name+"Supply").innerHTML = card.name + ": " + supply[card.name];
        this.discard.push(card);
    } else {
        console.log("no more " + card.name);
    }

}


function Card(name, cost, types) {
    this.name = name;
    this.cost = cost;
    this.types = types;
}



//START OF PROGRAM

var player1 = new Player("Tom");
var player2 = new Player("Daisy");
var players = [player1, player2];

var supplyView = document.getElementById("supply");
console.log(supplyView);

for (let i in supply) {
    var item = document.createElement("li");
    item.innerHTML = i + ": " + supply[i];
    item.id = i+"Supply";
    supplyView.append(item);
}

for (let j in players) {
    console.log(j);
    for (let i in players[j].deck) {
        var item = document.createElement("li");
        item.innerHTML = players[j].deck[i].name;
        item.id = i;
        document.getElementsByClassName("player")[j].getElementsByClassName("deck")[0].append(item);
    }
}

