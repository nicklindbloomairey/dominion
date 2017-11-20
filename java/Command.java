import java.io.Serializable;

public class Command implements Serializable {
    int player;
    String command;


    //this is the object that the clients send to their server sockets, the server sockets pass the command to the game server
    public Command(int player, String command) {
        this.player = player;
        this.command = command;
    }

    @Override
    public String toString() {
        return command + " from player " + player;
    }

}
