import java.util.ArrayList;
import java.io.*;
import java.net.*;

public class GameServer implements Runnable {
    //ArrayList<Sockets> connections;
    ArrayList<ObjectOutputStream> out;
    Game game;

    public GameServer() {
        out = new ArrayList<ObjectOutputStream>();
        game = new Game();
    }

    public void addConnection(Socket c) {
        try {
            ObjectOutputStream output = new ObjectOutputStream(c.getOutputStream());
            out.add(output);
            if (game.addPlayer()) {
                output.writeObject("Connection Successful");
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    /*
    public void closeConnection(int id) {
        try {
            out.get(id).close();
            out.remove(id);
            game.removePlayer(id);
        } catch (IOException e) {
        }
    }
    */

    public void run() {
        //update all clients with the game object
        while (true) {
            send(game);

            try { 
                Thread.sleep(1000); //wait a second between updating the clients
            } catch (Exception e) {
                System.out.println(e);
            }
        }
    }

    public void send(Game o) {
        for (ObjectOutputStream client : out) {
            try {
                client.reset();
                client.writeObject(o); 
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    public void update(Command c ) {
        if (game.status.equals("not started")) {
            if (c.command.equals("ready")) {
                game.players.get(c.player).ready = true; 

                //check if all players are now ready
                boolean check = true; //assume true
                for (int i = 0; i<game.players.size(); i++) {
                    if (game.players.get(i).ready == false) {
                        check = false; //change to false if someone isn't ready
                    }
                }
                if (check) {
                    if (game.players.size()>1) { //need more than one player to start
                        System.out.println("start");
                        game.start();
                    }
                }
            }
        } else if (game.status.equals("started")) {
            if (c.player >= game.players.size()) {
                //ignore the command, this player is not in the game!
            } else {
            }

        }
    }
}
