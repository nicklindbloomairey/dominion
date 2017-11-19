import javax.swing.JPanel;
import java.awt.Graphics;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import javax.swing.JButton;
import javax.swing.JTextField;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;

public class Screen extends JPanel implements ActionListener {

    public static final int HEIGHT=600, WIDTH=800;

    public Screen() {

        this.setLayout(null);


        button = new JButton("button");
        button.setBounds(x,y, xsize, ysize); //sets the location and size
        button.addActionListener(this); //add the listener
        this.add(button); //add to JPanel

        text = new JTextField(20);
        text.setBounds(x,y, xsize, ysize);
        this.add(text);

        this.setFocusable(true);
    }

    public Dimension getPreferredSize() {
        //Sets the size of the panel
        return new Dimension(Screen.WIDTH,Screen.HEIGHT);
    }

    public void paintComponent(Graphics g) {
        //draw background
        g.setColor(Color.white);
        g.fillRect(0,0,Screen.WIDTH,Screen.HEIGHT);

        //set up font
        Font font = new Font("Arial", Font.PLAIN, 20);
        g.setFont(font);
        g.setColor(Color.blue);
        
    }

    public void actionPerformed(ActionEvent e) {
        if (e.getSource() == button) {
        }

        repaint();
    }
}
