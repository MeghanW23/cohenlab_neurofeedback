import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class SimpleGUI {
    public static void main(String[] args) {
        // Create a new frame (window)
        JFrame frame = new JFrame("Sample Java GUI");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(400, 300);

        // Create a panel to hold components
        JPanel panel = new JPanel();
        frame.add(panel);

        // Add components to the panel
        placeComponents(panel);

        // Make the frame visible
        frame.setVisible(true);
    }

    private static void placeComponents(JPanel panel) {
        panel.setLayout(null); // Use absolute positioning

        // Create a label
        JLabel label = new JLabel("Welcome to Java GUI!");
        label.setBounds(120, 50, 200, 25);
        panel.add(label);

        // Create a button
        JButton button = new JButton("Click Me");
        button.setBounds(150, 100, 100, 40);
        panel.add(button);

        // Add an action listener to the button
        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Show a dialog when the button is clicked
                JOptionPane.showMessageDialog(null, "Hello, world!");
            }
        });
    }
}

