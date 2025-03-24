package com.cohenlab;

import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Map;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.border.CompoundBorder;
import javax.swing.border.EmptyBorder;
import javax.swing.border.EtchedBorder;

public class StatisticsPanel {
    Map<String, Map<String, Integer>> csvColumnIndices;
    String task; 

    public StatisticsPanel(String task) {
        this.task = task;
        this.csvColumnIndices = Constants.getColumnIndices();
    }

    public JPanel makeStatisticsPanel() {
        JPanel panel = new JPanel();
        panel.setPreferredSize(new Dimension(Constants.statPanelWidth, Constants.statPanelHeight));
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBackground(Constants.blueColor);
        panel.setBorder(BorderFactory.createEmptyBorder(0, 0, 0, 20));

        if ("Neurofeedback".equals(this.task)) {
            makeMaskPanel(panel);
        }
        makeDicomCountingPanel(panel);

        try {
           new ProcessBuilder("ls", "/Users/meghan").start();
        } catch (IOException e) {
            System.out.println("Error doing shell process: " + e);
        }
                
        return panel;

    }

    public void updateInfo(String csvLine) {
        System.out.println(csvLine);
        System.out.println(this.task);

        
    }
    @SuppressWarnings("ConvertToStringSwitch")
    public File getLastModified(String fileType){
        String directoryFilePath = null;
        if (null != fileType) switch (fileType) {
            case "mask":
                directoryFilePath = Constants.maskDir;
                break;
            case "logDir":
                if (null != this.task) switch (this.task) {
                    case "Neurfeedback":
                        directoryFilePath = Constants.csvNfbDirLogPath;
                        break;
                    case "RIFG":
                        directoryFilePath = Constants.csvRifgDirLogPath;
                        break;
                    case "MSIT":
                        directoryFilePath = Constants.csvMsitDirLogPath;
                        break;
                    default:
                        break;
                }   break;
            case "dicomDir":
                directoryFilePath = Constants.sambashareDirPath;
                break;
            default:
                break;
        }
        File directory = new File(directoryFilePath);
        File[] elements = directory.listFiles();
        long lastModifiedTime = Long.MIN_VALUE;
        File chosenFile = null;

        if (elements != null){
            for (File element : elements){
                if ("mask".equals(fileType)) {
                    if (! element.toString().contains("nii")) {
                    }
                    else if (element.lastModified() > lastModifiedTime) {
                        chosenFile = element;
                        lastModifiedTime = element.lastModified();
                    }
                } else if ("dicomDir".equals(fileType)) {
                    
                    if (! element.isDirectory()) {
                    }
                    else if (element.lastModified() > lastModifiedTime) {
                        chosenFile = element;
                        lastModifiedTime = element.lastModified();
                    }
                    
                } else if ("logDir".equals(fileType)) {
                    if (! element.toString().contains(".txt")) {
                    }
                    else if (element.lastModified() > lastModifiedTime) {
                        chosenFile = element;
                        lastModifiedTime = element.lastModified();
                    }               
                }
            }
        }
        return chosenFile;
    }

    public void makeMaskPanel(JPanel outerPanel) {
        outerPanel.add(Box.createVerticalStrut(10));

        JPanel maskPanel = new JPanel();
        maskPanel.setLayout(new BoxLayout(maskPanel, BoxLayout.Y_AXIS));
        maskPanel.setBackground(Constants.greyColor);
        maskPanel.setBorder(new CompoundBorder(
            new EtchedBorder(), 
            new EmptyBorder(5, 10, 5, 10)
            ));

        JLabel maskTitle = new JLabel("ROI Mask");
        maskTitle.setFont(Constants.statPanelTitleFont);
        maskTitle.setBorder(new EmptyBorder(0, 0, 5,0));
        maskTitle.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        maskPanel.add(maskTitle);

        JLabel maskName = new JLabel(getLastModified("mask").getName());
        maskName.setFont(Constants.statPanelNonTitleFont);
        maskName.setBorder(new EmptyBorder(0, 0, 5, 0));
        maskName.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        maskPanel.add(maskName);

        JButton openMask = new JButton("View Mask");
        openMask.setFont(Constants.statPanelNonTitleFont);
        openMask.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        maskPanel.add(openMask);

        openMask.addActionListener((ActionEvent e) -> {
            String[] command = {
                "ssh", "meghan@${HOST_IP}", 
                "open",  "/Users/meghan/cohenlab_neurofeedback" + getLastModified("mask").toString().replace("projectDir", "")
            };
            ProcessBuilder processBuilder = new ProcessBuilder(command);
            processBuilder.redirectErrorStream(true);
            try {
                Process process = processBuilder.start();
                
                // Check if there's any error output
                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                String line;
                boolean hasOutput = false;

                while ((line = reader.readLine()) != null) {
                    System.out.println(line);  // Output any results, although it's unlikely with 'open'
                    hasOutput = true;
                }

                // Check if there were any errors during process execution
                int exitCode = process.waitFor();
                if (exitCode != 0) {
                    System.out.println("Error: SSH command failed with exit code " + exitCode);
                } else if (!hasOutput) {
                    System.out.println("The command was executed successfully, but there was no output.");
                }
            } catch (IOException | InterruptedException e1) {
                System.out.println("Error opening mask: " + e1);
            }

        });

        outerPanel.add(maskPanel);
    }

    public void makeDicomCountingPanel(JPanel outerPanel) {
        outerPanel.add(Box.createVerticalStrut(10));

        JPanel dcmPanel = new JPanel();
        dcmPanel.setLayout(new BoxLayout(dcmPanel, BoxLayout.Y_AXIS));
        dcmPanel.setBackground(Constants.greyColor);
        dcmPanel.setBorder(new CompoundBorder(
            new EtchedBorder(), 
            new EmptyBorder(5, 10, 5, 10)
            ));

        JLabel dcmTitle = new JLabel("DICOM Directory");
        dcmTitle.setFont(Constants.statPanelTitleFont);
        dcmTitle.setBorder(new EmptyBorder(0, 0, 5,0));
        dcmTitle.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        dcmPanel.add(dcmTitle);

        JLabel dcmDirFilename = new JLabel(getLastModified("dicomDir").getName());
        dcmDirFilename.setFont(Constants.statPanelNonTitleFont);
        dcmDirFilename.setBorder(new EmptyBorder(0, 0, 5, 0));
        dcmDirFilename.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        dcmPanel.add(dcmDirFilename);

        JButton dcmButton = new JButton("Open Dicom Directory");
        dcmButton.setFont(Constants.statPanelNonTitleFont);
        dcmButton.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        dcmPanel.add(dcmButton);

        outerPanel.add(dcmPanel);

    }
}
