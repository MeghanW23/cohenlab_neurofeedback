package Main;

import GraphCSV.*;
import java.io.File;
import java.util.Arrays;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.Timer;




public class Main {
    public static void main(String[] args) {
        JFrame frame = new JFrame("ADHD Stimulant Project Graphical User Interface");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(300, 300);
        System.out.println("SimpleGUI Object and JFrame Created.");
        

        // Boot GUI 
        System.out.println("Creating Panel ...");
        JPanel panel = new JPanel();
        panel.setLayout(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        // gbc.insets = new Insets(10, 10, 10, 10); // Padding around components 
        JButton nfb_button = new JButton("Graph Neurofeedback Score");
        JButton end_button = new JButton("Exit");

        ImageIcon imageIcon = new ImageIcon("/Users/meghan/cohenlab_neurofeedback/other/Java_GUI/Neurofeedback_Logo.png");
        Image originalImage = imageIcon.getImage();
        Image scaledImage = originalImage.getScaledInstance(300, 200, Image.SCALE_SMOOTH);
        ImageIcon scaledIcon = new ImageIcon(scaledImage);
        JLabel imageLabel = new JLabel(scaledIcon);
        

        gbc.gridx = 1;
        gbc.gridy = 0;
        panel.add(imageLabel, gbc);

        gbc.gridx = 1; // Column 1
        gbc.gridy = 1; // Row 1
        panel.add(nfb_button, gbc);
        
        gbc.gridx = 1; 
        gbc.gridy = 2;
        panel.add(end_button, gbc);

        end_button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                System.out.println("Exit button clicked. Closing application.");
                System.exit(0);
            }
        });

        nfb_button.addActionListener(new ActionListener() {
            String directoryPath = "/Users/meghan/cohenlab_neurofeedback/tasks_run/data/nfb_logs";
            File mostrecentcsv = GetMostRecentCSV(directoryPath);
            
            @Override
            public void actionPerformed(ActionEvent e) {
                CSVReader csvGrapher = new CSVReader(mostrecentcsv);
                // Graph CSV Information 
                Timer timer = new Timer(1000, new ActionListener() {
                    @Override
                    public void actionPerformed(ActionEvent e) {
                        Object[] graph_information = csvGrapher.ReadData();
                        csvGrapher.GraphData(graph_information);
                    }
                });
                timer.start();
            }
        });

        System.out.println("Adding Panel to frame ...");
        frame.add(panel);

        System.out.println("Showing Panel ...");
        frame.setVisible(true);
    }

    public static File GetMostRecentCSV(String directoryPath) {
        File directory = new File(directoryPath);
        File[] csvFiles = directory.listFiles((dir, name) -> name.endsWith(".csv") && name.contains("score"));

        if (csvFiles == null || csvFiles.length == 0) {
            System.out.println("NO CSV FILES FOUND.");
            System.exit(0);
        }

        // Sort files by last modified date in descending order
        return Arrays.stream(csvFiles)
             .sorted((f1, f2) -> Long.compare(f2.lastModified(), f1.lastModified()))
             .findFirst()
             .orElse(null); // Return the most recent file

    }
}