public class Card {
    String name, type;
    int cost;
    String text; //?

    public Card(name) {
        this.name = name;
        if (name.equals("copper")) {
            cost = 0;
            type = "treasure";
        } else if (name.equals("curse")) {
            cost = 0;
            type = "curse";
        }
    }

    public String getName() {
        return name;
    }

    public boolean is(String type) {
        return this.type.equals(type);
    }


}
