public class Card {
    String name, type;
    int cost, victory_points, treasure_points;
    String text; //?
    Player owner;

    public Card(String name) {
        this(name, new Player());
    }

    public Card(String name, Player owner) {
        this.name = name;
        this.owner = owner;
        if (name.equals("copper")) {
            cost = 0;
            type = "treasure";
            treasure_points = 1;
        } else if (name.equals("silver")) {
            cost = 3;
            type = "treasure";
            treasure_points = 2;
        } else if (name.equals("gold")) {
            cost = 6;
            type = "treasure";
            treasure_points = 3;
        } else if (name.equals("curse")) {
            cost = 0;
            type = "curse";
            victory_points = -1;
        } else if (name.equals("estate")) {
            cost = 2;
            type = "victory";
            victory_points = 1;
        } else if (name.equals("duchy")) {
            cost = 5;
            type = "victory";
            victory_points = 3;
        } else if (name.equals("province")) {
            cost = 8;
            type = "victory";
            victory_points = 6;
        } else if (name.equals("village")) {
            cost = 3;
            type = "action";
            text = "+1 Card \n+2 Actions";
        } else if (name.equals("cellar")) {
            cost = 2;
            type = "action";
            text = "+1 Action\nDiscard any number of cards, then draw that many.";
        } else if (name.equals("chapel")) {
            cost = 2;
            type = "action";
            text = "Trash up to 4 cards from your hand.";
        } else if (name.equals("moat")) {
            cost = 2;
            type = "reaction";
            text = "+2 Cards\n\nWhen another player plays an Attack card, you may first reveal this from your hand, to be unaffected by it.";
        } else if (name.equals("harbinger")) {
            cost = 3;
            type = "action";
            text = "+1 Card\n+1 Action\nLook through your discard pile. You may put a card from it onto your deck.";
        } else if (name.equals("merchant")) {
            cost = 3;
            type = "action";
            text = "+1 card\n+1 Action\nThe first time you play a Silver this turn, +1 Coin.";
        } else if (name.equals("vassal")) {
            cost = 3;
            type = "action";
            text = "+2 Coins\nDiscard the top card of your deck. If it's an Action card, you may play it.";
        } else if (name.equals("workshop")) {
            cost = 3;
            type = "action";
            text = "Gain a card costing up to 4 Coins.";
        } else if (name.equals("bureaucrat")) {
            cost = 4;
            type = "action";
            text = "Gain a Silver onto your deck. Each other player reveals a Victory card from their hand and puts it onto their deck (or reveals a hand with no Victory cards).";
        } else if (name.equals("gardens")) {
            cost = 4;
            type = "victory";
            text = "Worth 1 Victory Point per 10 cards you have (round down).";
        } else if (name.equals("militia")) {
            cost = 4;
            type = "action";
            text = "+2 Coins\nEach other player discards down to 3 cards in hand.";
        } else if (name.equals("moneylender")) {
            cost = 4;
            type = "action";
            text = "You may trash a Copper from your hand for +3 Coins.";
        } else if (name.equals("poacher")) {
            cost = 4;
            type = "action";
            text = "+1 Card\n+1 Action\n+1 Coin\nDiscard a card per empty Supply pile.";
        }

    }

    public String getName() {
        return name;
    }

    public boolean is(String type) {
        return this.type.equals(type);
    }


}
