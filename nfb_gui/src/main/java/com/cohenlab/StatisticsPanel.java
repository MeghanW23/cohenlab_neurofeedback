package com.cohenlab;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.FileSystems;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardWatchEventKinds;
import java.nio.file.WatchEvent;
import java.nio.file.WatchKey;
import java.nio.file.WatchService;
import java.util.Map;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.SwingWorker;
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

    public JPanel[] makeStatisticsPanel() {
        JPanel panel1 = new JPanel();
        panel1.setPreferredSize(new Dimension(Constants.statPanelWidth1, Constants.statPanelHeight1));
        panel1.setLayout(new BoxLayout(panel1, BoxLayout.Y_AXIS));
        panel1.setBackground(Constants.blueColor);
        panel1.setBorder(BorderFactory.createEmptyBorder(0, 0, 0, 10));

        makeDicomCountingPanel(panel1);

        JPanel panel2 = new JPanel();
        panel2.setPreferredSize(new Dimension(Constants.statPanelWidth2, Constants.statPanelHeight2));
        panel2.setLayout(new BoxLayout(panel2, BoxLayout.Y_AXIS));
        panel2.setBackground(Constants.blueColor);
        panel2.setBorder(BorderFactory.createEmptyBorder(0, 0, 0, 10));

        if ("Neurofeedback".equals(this.task)) {
            makeMaskPanel(panel2);
            panel2.add(Box.createVerticalStrut(10));

            
        }
        createLogPanel(panel2, getLastModified("logDir").toString());

        return new JPanel[]{panel1, panel2};

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
                    case "Neurofeedback":
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
                System.out.println(this.task + " not recognized as a task");
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
            new EmptyBorder(5, 15, 5, 15)
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

        File dicomDir = getLastModified("dicomDir");

        JLabel dcmDirFilename = new JLabel(dicomDir.getName());
        dcmDirFilename.setFont(Constants.statPanelNonTitleFont);
        dcmDirFilename.setBorder(new EmptyBorder(0, 0, 5, 0));
        dcmDirFilename.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        dcmPanel.add(dcmDirFilename);


        JLabel dcmLabel = new JLabel("Dicom Count: " + countDicoms(dicomDir.toString()));
        dcmLabel.setFont(Constants.statPanelNonTitleFont);
        dcmLabel.setBorder(new EmptyBorder(0, 0, 5, 0));
        dcmLabel.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        dcmPanel.add(dcmLabel);

        outerPanel.add(dcmPanel);

        Runnable dicomCountTask = () -> waitForNewDicom(dcmLabel, dicomDir.toString());
        Thread thread = new Thread(dicomCountTask);
        thread.start(); // Starts the thread and calls the function

    }

    public void waitForNewDicom(JLabel labelToUpdate, String dicomDir) {
        try (WatchService watchService = FileSystems.getDefault().newWatchService()) {
            Path directory = Paths.get(dicomDir);

            directory.register(watchService, StandardWatchEventKinds.ENTRY_CREATE);

            WatchKey key;
            while (true) { 
                try {
                    // Wait for an event
                    key = watchService.take();
                    
                } catch (InterruptedException e) {
                    System.err.println("Watch service interrupted");
                    System.err.println(e);
                    continue;
                }

                for (WatchEvent<?> event : key.pollEvents()) {
                    WatchEvent.Kind<?> kind = event.kind();

                    if (kind == StandardWatchEventKinds.ENTRY_CREATE) {
                        labelToUpdate.setText("Dicom Count: " + countDicoms(dicomDir));
                    }
                }

                // Reset the key to continue listening for new events
                boolean valid = key.reset();
                if (!valid) {
                    System.err.println("Watch key no longer valid. Exiting...");
                    break;
                }
            }
            
        } catch (Exception e) {
            System.out.println("Error Getting Dicom Count: " + e);
        }
    }
    public int countDicoms(String directoryPath) {
        return new File(directoryPath).listFiles().length;
    }

    public static void createLogPanel(JPanel outerPanel, String logFilePath) {
        
        // Create the panel
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));

        panel.setBackground(Constants.greyColor);
        panel.setBorder(new CompoundBorder(
            new EtchedBorder(), 
            new EmptyBorder(5, 10, 5, 10)
            ));

        JLabel logTitle = new JLabel("Text Log File");
        logTitle.setFont(Constants.statPanelTitleFont);
        logTitle.setBorder(new EmptyBorder(0, 10, 5,10));
        logTitle.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        panel.add(logTitle);

        JLabel logFileName = new JLabel(new File(logFilePath).getName());
        logFileName.setFont(Constants.statPanelNonTitleFont);
        logFileName.setBorder(new EmptyBorder(0, 10, 5,10));
        logFileName.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        panel.add(logFileName);
        
    
        JTextArea textArea = new JTextArea();
        textArea.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(textArea);

        panel.add(scrollPane, BorderLayout.CENTER);

        outerPanel.add(panel);

        // Create a SwingWorker to tail the log file
        SwingWorker<Void, String> logTailWorker = new SwingWorker<Void, String>() {
            @Override
            protected Void doInBackground() {
                try {
                    // Start the "tail -f" process
                    ProcessBuilder processBuilder = new ProcessBuilder("tail", "-f", logFilePath);
                    Process process = processBuilder.start();
                    try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                        String line;
                        while ((line = reader.readLine()) != null && !isCancelled()) {
                            publish(line);
                        }
                    }
                } catch (IOException e) {
                    publish("Error: " + e.getMessage());
                }
                return null;
            }

            @Override
            protected void process(java.util.List<String> chunks) {
                for (String line : chunks) {
                    textArea.append(line + "\n");
                    textArea.setCaretPosition(textArea.getDocument().getLength());
                }
            }
        };

        logTailWorker.execute();
    }

}
