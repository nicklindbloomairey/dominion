import java.util.ArrayList;
import java.util.Stack;
import java.io.Serializable;

public class Game implements Serializable, Runnable {
    Player p1, p2, p3, p4;
    ArrayList<Player> players;
    int numPlayers;
    int turn = 0;

    Stack<Card> trash, copper, silver, gold, curse, estate, duchy, province;
    ArrayList<Stack<Card>> kingdom;

    public Game() {
    }

    public Game(int numPlayers, String[] kingdomCards) {
        this.numPlayers = numPlayers;

        trash = new Stack<Card>();

        copper = new Stack<Card>();
        for (int i = 0; i<60; i++) { //60 coppers in supply
            copper.push(new Card("copper"));
        }

        silver = new Stack<Card>();
        for (int i = 0; i<40; i++) { //40 silvers in supply
            silver.push(new Card("silver"));
        }

        gold = new Stack<Card>();
        for (int i = 0; i<40; i++) { //30 gold in supply
            gold.push(new Card("gold"));
        }

        int num = 0;
        if (numPlayers == 2) {
            num = 14;
        } else if (numPlayers == 3) {
            num = 21;
        } else if (numPlayers == 4) {
            num = 24;
        }
        estate = new Stack<Card>();
        for (int i = 0; i<num; i++) {
            estate.push(new Card("estate"));
        }
        num -= (3*numPlayers);
        duchy = new Stack<Card>();
        for (int i = 0; i<num; i++) {
            duchy.push(new Card("duchy"));
        }
        province = new Stack<Card>();
        for (int i = 0; i<num; i++) {
            province.push(new Card("province"));
        }

        num = 10 *(numPlayers-1);
        curse = new Stack<Card>();
        for (int i = 0; i<num; i++) {
            curse.push(new Card("curse"));
        }

        players = new ArrayList<Player>();
        for (int i = 0; i<numPlayers; i++) {
            players.add(new Player());
            for (int j = 0; j<7; j++) {
                players.get(i).gain(copper.pop());
            }
            for (int j = 0; j<3; j++) {
                players.get(i).gain(estate.pop());
            }
            players.get(i).drawHand(); 
        }
    }

    public void setupKingdom(int numPlayers, String[] kingdomCards) {
        this.numPlayers = numPlayers;

        trash = new Stack<Card>();

        copper = new Stack<Card>();
        for (int i = 0; i<60; i++) { //60 coppers in supply
            copper.push(new Card("copper"));
        }

        silver = new Stack<Card>();
        for (int i = 0; i<40; i++) { //40 silvers in supply
            silver.push(new Card("silver"));
        }

        gold = new Stack<Card>();
        for (int i = 0; i<40; i++) { //30 gold in supply
            gold.push(new Card("gold"));
        }

        int num = 0;
        if (numPlayers == 2) {
            num = 14;
        } else if (numPlayers == 3) {
            num = 21;
        } else if (numPlayers == 4) {
            num = 24;
        }
        estate = new Stack<Card>();
        for (int i = 0; i<num; i++) {
            estate.push(new Card("estate"));
        }
        num -= (3*numPlayers);
        duchy = new Stack<Card>();
        for (int i = 0; i<num; i++) {
            duchy.push(new Card("duchy"));
        }
        province = new Stack<Card>();
        for (int i = 0; i<num; i++) {
            province.push(new Card("province"));
        }

        num = 10 *(numPlayers-1);
        curse = new Stack<Card>();
        for (int i = 0; i<num; i++) {
            curse.push(new Card("curse"));
        }

        players = new ArrayList<Player>();
        for (int i = 0; i<numPlayers; i++) {
            players.add(new Player());
            for (int j = 0; j<7; j++) {
                players.get(i).gain(copper.pop());
            }
            for (int j = 0; j<3; j++) {
                players.get(i).gain(estate.pop());
            }
            players.get(i).drawHand(); 
        }
    }
    
    public void turn() {
        System.out.println("It is " + players.get(turn).toString() + "turn");
    }

    public boolean isGameOver() {
        if (province.isEmpty()) {
            return true;
        } else {
            int stacksEmpty = 0;
            for (Stack<Card> pile : kingdom) {
                if (pile.isEmpty()) {
                    stacksEmpty ++;
                }
            }
            if (stacksEmpty >= 3) {
                return true;
            }
        }
        return false;
    }

    public void run() {
        boolean start = false;
        while (!start) {
            if (Server.allReady) {
                    String[] kingdom = {"cellar", "market", "merchant", "militia", "mine", "moat", "remodel", "smithy", "village", "workshop"};

                setupKingdom(Server.count, kingdom);
                start = true;

                System.out.println("Game started with " + numPlayers + " players with the first set kingdom cards");

            } else {
                System.out.println("WHy arent you ready");
            }

        }


        //game has started from here on out
    }
    




}
