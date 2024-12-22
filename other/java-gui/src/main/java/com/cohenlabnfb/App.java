package com.cohenlabnfb;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.Image;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Date;
import javax.swing.BorderFactory;
import javax.swing.BoxLayout;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.border.EmptyBorder;

public class App {
    public static void main(String[] args) {
        Date now = new Date();
        String welcomeMessage = "Welcome! \nStarting time: " + now;
        System.out.println(welcomeMessage);
        System.out.println("Booting Neurofeedback GUI Now...");

        // Make main GUI
        int frameWidth = 300;
        int frameHeight = 400;
        Color backgroundColor = new Color(173, 216, 230);
        JFrame frame = new JFrame("ADHD Stimulant Project Graphical User Interface");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(frameWidth, frameHeight);
        frame.setLayout(new FlowLayout());
        frame.getContentPane().setBackground(backgroundColor);
        

        // Add option menu panel to GUI
        JPanel optionMenu = new JPanel();
        int optionLabelWidth = 250;
        int optionLabelHeight = 350;
        Color optionLabelColor = new Color(211, 211, 211);
        
        optionMenu.setLayout(new BoxLayout(optionMenu, BoxLayout.Y_AXIS)); // Vertical stacking
        optionMenu.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        optionMenu.setBorder(BorderFactory.createEtchedBorder());
        optionMenu.setBackground(optionLabelColor); // RGB for light blue
        optionMenu.setPreferredSize(new Dimension(optionLabelWidth, optionLabelHeight));

        // Make title 
        String titleLabelFont = "Times New Roman";
        int titleLabelFontSize = 25;
        Color titleLabelColor = new Color(211, 211, 211);
        int[] titlePadding = {10, 10, 10, 10};

        JLabel titleLabel = new JLabel("Neurofeedback GUI", JLabel.CENTER);
        titleLabel.setBorder(new EmptyBorder(titlePadding[0], titlePadding[1], titlePadding[2], titlePadding[3]));
        titleLabel.setFont(new Font(titleLabelFont, Font.BOLD, titleLabelFontSize));
        titleLabel.setAlignmentX(JLabel.CENTER_ALIGNMENT);
        titleLabel.setOpaque(true); // Required to show background color
        titleLabel.setBackground(titleLabelColor); // Light orange background for the box
        optionMenu.add(titleLabel);

        // Make logo image
        int nfbImageWidth = 300;
        int nfbImageHeight = 200;

        ImageIcon nfbLogo = new ImageIcon("/Users/meghan/cohenlab_neurofeedback/other/Java_GUI/Neurofeedback_Logo.png"); 
        Image nfbLogoImage = nfbLogo.getImage();
        Image nfbScaledLogoImage = nfbLogoImage.getScaledInstance(nfbImageWidth, nfbImageHeight, Image.SCALE_SMOOTH);
        ImageIcon nfbScaledLogo = new ImageIcon(nfbScaledLogoImage);
        JLabel imageLabel = new JLabel(nfbScaledLogo);
        imageLabel.setAlignmentX(JPanel.CENTER_ALIGNMENT);

        optionMenu.add(imageLabel);

        // Make Buttons on option menu
        int buttonWidth = 200;
        int buttonHeight = 40;
        String buttonFont = "Times New Roman";
        int buttonFontSize = 16;
        
        JButton nfbButton = new JButton("Graph Neurofeedback");
        nfbButton.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        nfbButton.setPreferredSize(new Dimension(buttonWidth, buttonHeight));
        nfbButton.setMaximumSize(new Dimension(buttonWidth, buttonHeight));
        nfbButton.setFont(new Font(buttonFont, Font.PLAIN, buttonFontSize));
        nfbButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                NFBGraph NFBGraph = new NFBGraph();
                NFBGraph.ChooseTask();
            }
        });

        optionMenu.add(nfbButton);

        JButton stopButton = new JButton("Exit");
        stopButton.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        stopButton.setPreferredSize(new Dimension(buttonWidth, buttonHeight));
        stopButton.setMaximumSize(new Dimension(buttonWidth, buttonHeight));
        stopButton.setFont(new Font(buttonFont, Font.PLAIN, buttonFontSize));

        stopButton.addActionListener(new ActionListener() {
            // Stop button exits on close
            @Override
            public void actionPerformed(ActionEvent e) {
                System.out.println("Exiting GUI.");
                System.exit(0);
            }
        });

        optionMenu.add(stopButton);
        
        // Make visible
        frame.add(optionMenu);
        frame.setVisible(true);
    }
}


