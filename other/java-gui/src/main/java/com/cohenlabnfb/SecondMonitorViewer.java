package com.cohenlabnfb;

import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;

public class SecondMonitorViewer {
    public static Object[] MakeMRIScreen(JFrame frame) {
        Object[] informationToReturn = new Object[4];

        JLabel displayLabel = new JLabel();
        informationToReturn[0] = displayLabel;
        displayLabel.setHorizontalAlignment(JLabel.CENTER);

        int imageWidth = 300;
        int imageHeight = 200;

        frame.add(displayLabel);
        frame.setVisible(true);

        // Start a thread to capture the second monitor and update the display
        new Thread(() -> {
            try {
                GraphicsEnvironment ge = GraphicsEnvironment.getLocalGraphicsEnvironment();
                GraphicsDevice[] screens = ge.getScreenDevices();

                if (screens.length < 2) {
                    JOptionPane.showMessageDialog(frame, "No second monitor detected!");
                    return;
                }

                GraphicsDevice secondMonitor = screens[1]; // Second monitor (index 1)
                Rectangle screenBounds = secondMonitor.getDefaultConfiguration().getBounds();
                informationToReturn[3] = screenBounds;
                System.out.println("Second Monitor Bounds: " + screenBounds); // Debugging

                // Ensure you're capturing just the second monitor's screen area
                Robot robot = new Robot(secondMonitor);

                while (true) {
                    // Capture only the second monitor by specifying its bounds
                    BufferedImage screenshot = robot.createScreenCapture(screenBounds);
                    BufferedImage resizedScreenshot = resizeImage(screenshot, imageWidth, imageHeight);
                    informationToReturn[1] = imageWidth;
                    informationToReturn[2] = imageHeight;

                        // Update the JLabel with the screenshot
                        SwingUtilities.invokeLater(() -> {
                        // Create an ImageIcon without scaling
                            ImageIcon imageIcon = new ImageIcon(resizedScreenshot);
                            displayLabel.setIcon(imageIcon);
                        });
                        // Refresh every 100ms
                        Thread.sleep(10);
                    }
                    
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }).start();

            return informationToReturn;
    }
        // Method to resize the image
    private static BufferedImage resizeImage(BufferedImage originalImage, int targetWidth, int targetHeight) {
        // Create a new buffered image with the target size
        BufferedImage resizedImage = new BufferedImage(targetWidth, targetHeight, originalImage.getType());

        // Create a Graphics2D object to perform the resizing
        Graphics2D g2d = resizedImage.createGraphics();
        
        // Set rendering hints for better image quality
        g2d.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_BICUBIC);  // No direct Lanczos3 support
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
        g2d.setRenderingHint(RenderingHints.KEY_COLOR_RENDERING, RenderingHints.VALUE_COLOR_RENDER_QUALITY);
        g2d.setRenderingHint(RenderingHints.KEY_DITHERING, RenderingHints.VALUE_DITHER_ENABLE);

        // Use the drawImage method to scale the image
        g2d.drawImage(originalImage, 0, 0, targetWidth, targetHeight, null);

        // Dispose of the Graphics2D object to free resources
        g2d.dispose();

        return resizedImage;
    }
}
