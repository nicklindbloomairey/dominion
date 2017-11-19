import java.io.*;
import java.net.*;
import java.util.Scanner;

public class Client {
    public static void main(String[] args) throws IOException {

        Scanner scanscan = new Scanner(System.in);

        boolean ready = false;

        String hostname = args[0];
        int portnumber = 8080;

        Socket serverSocket = new Socket(hostname, portnumber);

        ObjectOutputStream out = new ObjectOutputStream(serverSocket.getOutputStream());
        ObjectInputStream in = new ObjectInputStream(serverSocket.getInputStream());
        
        out.writeObject("A client connected!");
        try {
            String input = (String) in.readObject();
            System.out.println(input);
        } catch (Exception e) {
            e.printStackTrace();
        }

        try {
            while(true) { //game loop - where everything goes
                if (!ready) 
                    System.out.println("Welcome to dominion");
                while(!ready) {
                    System.out.println("Are you ready? (y/n)");
                    String input = scanscan.nextLine();
                    if (input.trim().equals("y")) {
                        ready = true;
                    }
                }

                out.writeObject("ready");

            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
