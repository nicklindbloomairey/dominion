import java.io.Serializable;

public class Command implements Serializable {
    int player;
    String command, arg1, arg2;

    /*
    // command list
    // 
    // ready
    // play [index in hand]
    // buy [name of card]

    */


    //this is the object that the clients send to their server sockets, the server sockets pass the command to the game server
    public Command(int player, String command) {
        this.player = player;
        String[] temp = command.split("\\s+");
        this.command = temp[0];
        if (temp.length > 1) {
            this.arg1 = temp[1];
            this.arg2 = "NULL";
        } else if (temp.length > 2) {
            this.arg1 = temp[1];
            this.arg2 = temp[2];
        } else {
            this.arg1 = "NULL";
            this.arg2 = "NULL";
        }

    }

    @Override
    public String toString() {
        return command + " from player " + player;
    }

}
