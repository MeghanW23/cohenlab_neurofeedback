package com.cohenlab;

import java.awt.AWTException;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.Rectangle;
import java.awt.Robot;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.image.BufferedImage;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.Timer;

public class ScreenCapturePanel extends JPanel {
    private BufferedImage screenCapture;

    // Constructor
    public ScreenCapturePanel() {
        // Set preferred size for the panel
        this.setPreferredSize(new Dimension(800, 600));

        // Set up a timer to refresh the screen capture
        Timer timer = new Timer(1000, new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                captureScreen();
                repaint();
            }
        });
        timer.start();
    }

    // Capture the screen using the Robot class
    private void captureScreen() {
        try {
            // Create a Robot instance to capture the screen
            Robot robot = new Robot();
            // Capture the screen area, here it captures the full screen
            screenCapture = robot.createScreenCapture(new Rectangle(Toolkit.getDefaultToolkit().getScreenSize()));
        } catch (AWTException e) {
            e.printStackTrace();
        }
    }

    // Override paintComponent to draw the screen capture
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        // If the screen capture is available, draw it onto the JPanel
        if (screenCapture != null) {
            g.drawImage(screenCapture, 0, 0, null);
        }
    }

    public static void main(String[] args) {
        // Set up the JFrame to display the panel
        JFrame frame = new JFrame("Screen Capture");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.add(new ScreenCapturePanel());
        frame.pack();
        frame.setVisible(true);
   
    }
}