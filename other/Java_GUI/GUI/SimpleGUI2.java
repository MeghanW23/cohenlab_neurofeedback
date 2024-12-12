package GUI;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class SimpleGUI2 {
    public void MakeSimpleGUI() {
        JFrame frame = new JFrame("Neurofeedback GUI");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(300, 400);
        frame.setBackground(Color.GREEN);

        JPanel panel = new JPanel();
        panel.setLayout(new GridBagLayout());

        GridBagConstraints gbc = new GridBagConstraints();

        JButton nfb_button = new JButton("Start Neurofeedback");

        JButton rifg_button = new JButton("Start RIFG Task");

        JButton msit_button = new JButton("Start MSIT Task");

        JButton end_button = new JButton("Exit");

        gbc.gridx = 1; // Column 1
        gbc.gridy = 1; // Row 0
        panel.add(nfb_button, gbc);

        gbc.gridx = 1;
        gbc.gridy = 2; 
        panel.add(rifg_button, gbc);

        gbc.gridx = 1; 
        gbc.gridy = 3;
        panel.add(msit_button, gbc);

        gbc.gridx = 1; 
        gbc.gridy = 4;
        panel.add(end_button, gbc);

        end_button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e){
                System.exit(0);
            }
        });

        ImageIcon icon = new ImageIcon("/Users/meghan/Desktop/Other/Neurofeedback_Logo.png");
        Image image = icon.getImage();
        Image resizedImage = image.getScaledInstance(300, 200, Image.SCALE_SMOOTH);
        icon = new ImageIcon(resizedImage);

        JLabel label = new JLabel(icon);
        gbc.gridx = 1; // Column 1
        gbc.gridy = 0; // Row 0
        panel.add(label, gbc);

    
        frame.add(panel);
        frame.setVisible(true);
    }
}