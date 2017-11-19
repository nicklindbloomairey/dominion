import java.io.*;
import java.net.*;
import java.util.ArrayList;

public class Server implements Runnable {
    private Socket connection;
    private String TimeStamp;
    private int ID;

    public static int count = 0;
    public static ArrayList<Boolean> ready;
    public static boolean allReady = false;


    public static void main(String[] args) {

        Runnable gameRunnable = new Game();
        Thread gameThread = new Thread(gameRunnable);
        gameThread.start();

        ready = new ArrayList<Boolean>();

        int portNumber = 8080;

        try {
            ServerSocket serverSocket = new ServerSocket(portNumber);
            System.out.println("Server Started");

            while (true) {
                Socket connection = serverSocket.accept(); //this thread stops everytime, waiting for a connection
                Runnable runnable = new Server(connection, ++Server.count);
                Thread thread = new Thread(runnable);
                thread.start();
                Server.ready.add(false);
                allReady = false;

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

    public void run() {
        ObjectOutputStream out;
        ObjectInputStream in;

        try {
            out = new ObjectOutputStream(connection.getOutputStream());
            in = new ObjectInputStream(connection.getInputStream());
        } catch (Exception e) {
            e.printStackTrace();
            out = null;
            in = null;
        }

        try {

            out.writeObject("Connection successful with id " + ID);

            String input = (String) in.readObject();
            System.out.println(input);
        } catch (Exception e) {
            e.printStackTrace();
        }

        //listen
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

}
