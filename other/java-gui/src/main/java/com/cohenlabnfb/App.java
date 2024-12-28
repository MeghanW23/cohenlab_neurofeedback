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
import javax.swing.ButtonGroup;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JRadioButton;
import javax.swing.UIManager;
import javax.swing.UnsupportedLookAndFeelException;
import javax.swing.border.EmptyBorder;

public class App {
        public static void main(String[] args) {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            } catch (UnsupportedLookAndFeelException | ClassNotFoundException | InstantiationException | IllegalAccessException e) {
                e.printStackTrace();
            }
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
        JPanel contentPane = (JPanel) frame.getContentPane();
        contentPane.setBackground(backgroundColor);
        contentPane.setOpaque(true);
        

        // Add option menu panel to GUI
        JPanel optionMenu = new JPanel();
        int optionLabelWidth = 250;
        int optionLabelHeight = 350;
        Color optionLabelColor = new Color(211, 211, 211);
        
        optionMenu.setLayout(new BoxLayout(optionMenu, BoxLayout.Y_AXIS)); // Vertical stacking
        optionMenu.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        optionMenu.setBorder(BorderFactory.createEtchedBorder());
        optionMenu.setOpaque(true); 
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

        String nfbLogoPath = System.getenv("NEUROFEEDBACK_LOGO_IMAGE");
        ImageIcon nfbLogo = new ImageIcon(nfbLogoPath); 
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
        
        JButton nfbButton = new JButton("Graph Task Data");
        nfbButton.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        nfbButton.setPreferredSize(new Dimension(buttonWidth, buttonHeight));
        nfbButton.setMaximumSize(new Dimension(buttonWidth, buttonHeight));
        nfbButton.setFont(new Font(buttonFont, Font.PLAIN, buttonFontSize));
        nfbButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                ChooseTask();
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
                    
    public static void ChooseTask() {
        String taskFont = "Times New Roman";
        int taskFontSize = 15;
        int taskOptionsFontSize = 15;

        int taskFrameWidth = 375;
        int taskFrameHeight = 150;
        JFrame taskFrame = new JFrame("Task Chooser");
        taskFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        taskFrame.setSize(taskFrameWidth, taskFrameHeight);
        taskFrame.setLayout(new FlowLayout());

        int taskFrameLabelLeftPadding = 10;
        int taskFrameLabelTopPadding = 10;
        int taskFrameLabelBottomPadding = 10;
        JLabel taskFrameLabel = new JLabel("What task is the data associated with? ");
        taskFrameLabel.setFont(new Font(taskFont, Font.BOLD, taskFontSize));
        taskFrameLabel.setBorder(BorderFactory.createEmptyBorder(taskFrameLabelTopPadding, taskFrameLabelLeftPadding, taskFrameLabelBottomPadding, 0));
        taskFrame.add(taskFrameLabel);

        int taskOptionsLeftPadding = 10;
        int taskOptionsBottomPadding = 5;

        ButtonGroup taskOptionGroup = new ButtonGroup();
        JRadioButton nfbChoice = new JRadioButton("Neurofeedback");
        JRadioButton rifgChoice = new JRadioButton("RIFG Task");
        JRadioButton msitChoice = new JRadioButton("MSIT Task");
        taskOptionGroup.add(nfbChoice);
        taskOptionGroup.add(rifgChoice);
        taskOptionGroup.add(msitChoice);
        nfbChoice.setFont(new Font(taskFont, Font.PLAIN, taskOptionsFontSize));
        rifgChoice.setFont(new Font(taskFont, Font.PLAIN, taskOptionsFontSize));
        msitChoice.setFont(new Font(taskFont, Font.PLAIN, taskOptionsFontSize));
        nfbChoice.setBorder(BorderFactory.createEmptyBorder(0, taskOptionsLeftPadding, taskOptionsBottomPadding, 0));
        rifgChoice.setBorder(BorderFactory.createEmptyBorder(0, taskOptionsLeftPadding, taskOptionsBottomPadding, 0));
        msitChoice.setBorder(BorderFactory.createEmptyBorder(0, taskOptionsLeftPadding, taskOptionsBottomPadding, 0));
        taskFrame.add(nfbChoice);
        taskFrame.add(rifgChoice);
        taskFrame.add(msitChoice);
        
        JButton selectButton = new JButton("Select");
        selectButton.setFont(new Font(taskFont, Font.PLAIN, taskFontSize));
        taskFrame.add(selectButton);
        selectButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                if (nfbChoice.isSelected()) {
                    NFBGraph NFBGraph = new NFBGraph();
                    NFBGraph.MakeGraphPanel();
                    taskFrame.setVisible(false);
                } else if (rifgChoice.isSelected()) {
                    RIFGGraph RIFGGraph = new RIFGGraph();
                    RIFGGraph.MakeGraphPanel();
                    taskFrame.setVisible(false);
                } else if (msitChoice.isSelected()) {
                    MSITGraph MSITGraph = new MSITGraph();
                    MSITGraph.MakeGraphPanel();
                    taskFrame.setVisible(false);
                } else {
                    JOptionPane.showMessageDialog(taskFrame, "Please Select a Task to continue.");
                }
            }
        });

        taskFrame.setVisible(true);

    }
}


