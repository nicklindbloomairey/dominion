import javax.swing.JPanel;
import java.awt.Graphics;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JButton;
import javax.swing.JTextField;

import java.io.*;
import java.net.*;

public class ClientScreen extends JPanel implements MouseListener, ActionListener {

    public static final int WIDTH=800, HEIGHT=600;
	private ObjectOutputStream out;
    private Game game = new Game(); //this is a dummy game, will be overwritten once the server sends a copy
    private String lastStatus;
    private int ID;

    private JButton ready, play, buy;
    private JTextField input;
	
	public ClientScreen() {
        this.setLayout(null);
		this.setFocusable(true);
        addMouseListener(this);

        ready = new JButton("ready");
        ready.setBounds(WIDTH/2, HEIGHT/2, 100, 30);
        ready.addActionListener(this);
        this.add(ready);

        play = new JButton("Play");
        play.setBounds( WIDTH/4, HEIGHT-50, 100, 30);
        play.addActionListener(this);

        buy = new JButton("Buy");
        buy.setBounds( (WIDTH/4) + 110, HEIGHT-50, 100, 30);
        buy.addActionListener(this);

        input = new JTextField(20);
        input.setBounds( WIDTH/4, HEIGHT-90, 100, 30);

	}

    public void drawHand(Graphics g, int x, int y) {
        g.drawString("Hand", x, y-30);
        for (int i = 0; i<game.players.get(ID).hand.size(); i++) {
            g.drawString(i + ". " + game.players.get(ID).hand.get(i).toString(), x, y);
            y+=30;
        }
    }

    public void drawPlay(Graphics g, int x, int y) {
        g.drawString("In Play", x, y-30);
        for (int i = 0; i<game.players.get(ID).play.size(); i++) {
            g.drawString(i + ". " + game.players.get(ID).play.get(i).toString(), x, y);
            y+=30;
        }
    }
	
	public void paintComponent(Graphics g){
		super.paintComponent(g);	

        Font font = new Font("Arial", Font.PLAIN, 20);
        g.setFont(font);
        g.setColor(Color.black);

        g.drawString(game.status, 600, 500);
        g.drawString("" + game.players.size(), 600, 450);
        g.drawString("Player " + ID, WIDTH/2, 30);


        if (game.status.equals("not started")) {
            g.drawString("Waiting for players", 100, 100);
            g.drawString("Ready: " + game.players.get(ID).ready, 100, 130);
        } else if (game.status.equals("started")) {
            drawHand(g, WIDTH/4, HEIGHT/2);
            drawPlay(g, WIDTH/2, HEIGHT/2);
            g.drawString("Coins: " + game.players.get(ID).coins, 100, 100);
            g.drawString("Actions: " + game.players.get(ID).actions, 100, 130);
            g.drawString("Buys: " + game.players.get(ID).buys, 100, 160);
        }
        
	}

	public Dimension getPreferredSize() {
        return new Dimension(WIDTH,HEIGHT);
	}
	
    //mouse listener methods
	public void mousePressed(MouseEvent e) {}
	public void mouseReleased(MouseEvent e) {}
	public void mouseEntered(MouseEvent e) {}
	public void mouseExited(MouseEvent e) {}
	public void mouseClicked(MouseEvent e) {}

    //action listener methods
    public void actionPerformed(ActionEvent e) {
        if (e.getSource()==ready) {
            try {
                out.writeObject("ready");
            } catch(IOException ex) {
                ex.printStackTrace();
            }
        } else if (e.getSource()==play) {
            int index = Integer.parseInt(input.getText());
            try {
                out.writeObject("play " + index);
            } catch(IOException ex) {
                ex.printStackTrace();
            }

        }
    }


    public void update() {
        if (!lastStatus.equals(game.status)) {
            this.removeAll();
            if (game.status.equals("not started")) {
                this.add(ready);
            } else if (game.status.equals("started")) {
                this.add(play);
                this.add(input);
                this.add(buy);
            }
        }
    }

	

	public void poll(String hostName) throws IOException{
		
        int portNumber = 8080;
		
		Socket serverSocket = new Socket(hostName, portNumber);
		
		out = new ObjectOutputStream(serverSocket.getOutputStream());
		ObjectInputStream in = new ObjectInputStream(serverSocket.getInputStream());
		
		out.writeObject("A Client connected!");
        try {
            String input = (String) in.readObject(); //wait for the connection successful message
            System.out.println(input);
            ID = Integer.parseInt(input.split("\\s+")[0]);
        } catch (Exception e) {
            e.printStackTrace();
        }
		
		//listens for inputs
		try {

            while (true) {
			    lastStatus = game.status;	
				game = (Game) in.readObject();
                update();
                //String input = (String) in.readObject();
				repaint();
				
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
	}
}
