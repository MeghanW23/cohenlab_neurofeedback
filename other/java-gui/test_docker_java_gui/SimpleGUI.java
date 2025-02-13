import javax.swing.*;
import java.awt.Color;

public class SimpleGUI {
    public static void main(String[] args) {
        // Create a new JFrame (window)
        JFrame frame = new JFrame("Simple Java GUI");
        frame.getContentPane().setBackground(Color.BLUE);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(400, 300);

        // Create a label and add it to the frame
        JLabel label = new JLabel("Java GUI!", SwingConstants.CENTER);
        frame.add(label);

        // Create a button and add it to the frame
        JButton button = new JButton("Click Me");
        frame.add(button, "South");

        // Add an action listener to the button
        button.addActionListener(e -> JOptionPane.showMessageDialog(frame, "Button clicked!"));

        // Set the frame to be visible
        frame.setVisible(true);
    }
}
