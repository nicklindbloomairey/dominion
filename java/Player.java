import java.util.ArrayList;
import java.util.Random;
import java.io.Serializable;

public class Player implements Serializable {
    public ArrayList<Card> deck, hand, play, discard;
    public int coins = -1, actions = -1, buys = -1;
    boolean ready = false;

    public Player() {
        deck = new ArrayList<Card>();
        hand = new ArrayList<Card>();
        play = new ArrayList<Card>();
        discard = new ArrayList<Card>();
    }

    public void gain(Card c) {
        discard.add(c);
    }

    public void draw(int n) {
        for (int i = 0; i<n; i++) {
            if (deck.isEmpty()) {
                reset();
            }
            hand.add(deck.remove(deck.size()-1));
        }
    }

    public void drawHand() {
        draw(5);
        coins = 0;
        actions = 1;
        buys = 1;
    }

    public void shuffle(ArrayList<Card> pile) {
        Random rand = new Random();
        for (int i = 0; i<pile.size()-1; i++) {
            int j = rand.nextInt(pile.size());
            Card temp = pile.get(j);
            pile.set(j, pile.get(i));
            pile.set(i, temp);
        }
    }

    public void reset() {
        shuffle(discard);
        ArrayList<Card> temp = discard;
        discard = deck;
        deck = temp;
    }


    public int score() {
        return 0;
    }

    public void play(int index) {
        play.add(hand.remove(index));
    }
}

