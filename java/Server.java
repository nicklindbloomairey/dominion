import java.io.*;
import java.net.*;
import java.util.ArrayList;

public class Server implements Runnable {
    private Socket connection;
    private String TimeStamp;
    private int ID;

    public static int count = -1;
    //public static ArrayList<Boolean> ready;
    //public static boolean allReady = false;
    //public static Game gameObject = new Game();
    public static GameServer gameServer;


    public static void main(String[] args) {

        gameServer = new GameServer();
        Thread gameThread = new Thread(gameServer);
        gameThread.start();

        //ready = new ArrayList<Boolean>();

        int portNumber = 8080;

        try {
            ServerSocket serverSocket = new ServerSocket(portNumber);
            System.out.println("Server Started");

            while (true) {
                Socket connection = serverSocket.accept(); //this thread stops everytime, waiting for a connection
                gameServer.addConnection(connection, ++Server.count);
                Runnable runnable = new Server(connection, Server.count);
                Thread thread = new Thread(runnable);
                thread.start();
                //Server.ready.add(false);
                //allReady = false;

                //this code never gets run
                /*
                if (check) {
                    System.out.println("All users ready, starting game with " + Server.count + " players");
                    String[] kingdom = {"cellar", "market", "merchant", "militia", "mine", "moat", "remodel", "smithy", "village", "workshop"};
                    game = new Game(Server.count, kingdom);
                } else {
                    System.out.println("not all players ready");
                }
                */
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    Server(Socket s, int i) {
        this.connection = s;
        this.ID = i;
    }

/*
    public void run() {
        ObjectInputStream in;

        try {
            in = new ObjectInputStream(connection.getInputStream());
        } catch (Exception e) {
            e.printStackTrace();
            in = null;
        }

        try {

            String input = (String) in.readObject();
            System.out.println(input);
        } catch (Exception e) {
            e.printStackTrace();
        }

        //listen do not send anything from here
        try {
            while (true) {
                //listen for input from clients and update game object accordingly
                if (!Server.ready.get(ID-1)) {
                    String input = (String) in.readObject();
                    if (input.equals("ready")) {
                        Server.ready.set(ID-1, true);
                        System.out.println("Client with ID " + ID + " is ready");

                        //update the allready variable
                        boolean check = true;
                        for (int i = 0; i<Server.ready.size(); i++) {
                            if (!Server.ready.get(i)) {
                                check = false;
                            }
                        }
                        if (Server.ready.size()>1) {
                            Server.allReady = check;
                        }

                        System.out.println(allReady);
                    }
                } 

                if (gameObject.start) {
                    //if it is this players turn ask what they want to do
                    if (gameObject.turn == ID) {
                        out.writeObject("It is your turn.");
                    } else {
                        out.writeObject("Waiting for player " + (gameObject.turn+1) + "");
                    }
                }

            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        finally {
            try {
                out.close();
                connection.close();
                Server.count--; 
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

    }
*/

    public void run() {
        ObjectInputStream in;

        try {
            in = new ObjectInputStream(connection.getInputStream());
        } catch (Exception e) {
            e.printStackTrace();
            in = null;
        }

        try {

            String input = (String) in.readObject();
            System.out.println(input);
        } catch (Exception e) {
            e.printStackTrace();
        }

        //listen do not send anything from here
        try {
            while (true) {
                //listen for input from clients and update game object accordingly
                String s = (String) in.readObject(); 
                Command c = new Command(ID, s);
                gameServer.update(c);
                System.out.println(c);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }


        finally {
            try {
                connection.close();
                //gameServer.closeConnection(ID);
                Server.count--; 
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

    }

}
