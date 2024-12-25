package com.cohenlabnfb;

import java.awt.FlowLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Path;
import java.nio.file.StandardWatchEventKinds;
import java.nio.file.WatchEvent;
import java.nio.file.WatchKey;
import java.nio.file.WatchService;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;

import javax.swing.SwingWorker;
import javax.swing.border.EmptyBorder;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;


public class MSITGraph {
    private JFrame msitFrame;
    public static File csvDir;
    private ChartPanel chartPanel;
    private JFreeChart chart;
    private XYSeries correctSeries;
    private XYSeries invalidSeries;
    private XYSeries nopressSeries;
    private XYSeries incorrectSeries;
    private XYSeriesCollection dataset;
    private JLabel header;
    private JButton waitForNewCSVButton;
    private JButton selectFileButton;

    public static File GetCsvPath() {
        return csvDir;
    }
    public void MakeGraphPanel() {
        String csvDirPath = System.getenv("MSIT_LOG_DIR");
        csvDir = new File(csvDirPath);
        System.out.println("Selected directory: " + csvDir.getAbsolutePath());
        msitFrame = new JFrame("MSIT Graph");
        msitFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        msitFrame.setLayout(new FlowLayout());

        int msitFrameWidth = 900;
        int msitFrameHeight = 700;
        msitFrame.setSize(msitFrameWidth, msitFrameHeight);

        correctSeries = new XYSeries("Percent Correct");
        incorrectSeries = new XYSeries("Percent Incorrect");
        invalidSeries = new XYSeries("Percent Invalid Keypresses");
        nopressSeries = new XYSeries("Percent No Keypresses");
       
        dataset = new XYSeriesCollection();
        dataset.addSeries(correctSeries);
        dataset.addSeries(invalidSeries);
        dataset.addSeries(nopressSeries);
        dataset.addSeries(incorrectSeries);

        chart = ChartFactory.createXYLineChart(
            "MSIT Task Graph", 
            "TR",
            "Percent Correct",
            dataset,
            PlotOrientation.VERTICAL,
            true,    // Show legend
            true,   // Tooltips
            false   // URLs
        );

        // Make panel to put chart on 
        chartPanel = new ChartPanel(chart);
        chartPanel.setPreferredSize(new java.awt.Dimension(800, 600));
        msitFrame.add(chartPanel);

        header = new JLabel("Please Select a CSV File to Graph.");
        header.setBorder(new EmptyBorder(10, 10, 10,10));
        header.setAlignmentX(JLabel.BOTTOM_ALIGNMENT);
        msitFrame.add(header);
        
        waitForNewCSVButton = new JButton("Wait for a New CSV");
        waitForNewCSVButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                header.setText("Waiting for new CSV ...");

                // Use SwingWorker to perform long-running tasks in the background
                SwingWorker<File, Void> worker = new SwingWorker<File, Void>() {
                    @Override
                    protected File doInBackground() throws Exception {
                        return WaitForNewCSV();
                    }

                    @Override
                    protected void done() {
                        try {
                            File csvFilePath = get(); // Retrieve the result of WaitForNewCSV
                            ReadCSVThreadWrapper(csvFilePath); // Process the CSV file
                            header.setText("Reading from File: " + csvFilePath.getName());
                        } catch (Exception ex) {
                            header.setText("Error: " + ex.getMessage());
                        }
                    }
                };
                worker.execute();
            }
        });
        msitFrame.add(waitForNewCSVButton);

        selectFileButton = new JButton("Select a File to Graph");
        selectFileButton.setAlignmentX(JFrame.BOTTOM_ALIGNMENT);
        FileSystemGUI.createFileButton("msit", selectFileButton, msitFrame, csvFile -> {
            if ( csvFile != null ) {
                System.out.println("Selected CSV File: " +  csvFile);
                File csvFilePath = new File(csvFile);
                header.setText("Reading from File: " + csvFilePath.getName());
                 // Remove get data buttons 
                 ReadCSVThreadWrapper(csvFilePath);
            } else {
                System.out.println("No CSV File selected.");
            }

        });

        msitFrame.add(selectFileButton);

        JButton exitButton = new JButton("Exit");
        exitButton.setAlignmentX(JFrame.BOTTOM_ALIGNMENT);
        exitButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                System.out.println("Exiting Grapher Now.");
                msitFrame.setVisible(false);
                
            }
        });

        msitFrame.add(exitButton);
        msitFrame.setVisible(true);
    }
    public void ReadCSVFile(File csvFile) {
        // Initialize Headers and Vars  
        String line; 

        // FileReader opens the file for reading., BufferedReader adds efficiency by reading chunks of data at a time, rather than one character at a time.
        while (true) {
            double numCorrect = 0;
            double numIncorrect = 0;
            double trialNum = 0;   
            double numInvalid = 0;
            double numNp = 0;
            System.out.println("Starting Graph ...");

            try (BufferedReader br = new BufferedReader(new FileReader(csvFile))) {
                System.out.println("Reading Data ...");
                while ((line = br.readLine()) != null) {
                    System.out.println("Found Data ...");
                    if (line.trim().isEmpty() || line.trim().equals(",")) {
                        System.out.println("Skipping Empty Line...");
                        continue;
                    } 

                    String[] lines;
                    if (line.contains(",")) {
                        lines = line.trim().split(",");
                    } else {
                        System.out.println("The line does not inclue a comma. Skipping ...");
                        continue; 
                    }
                    System.out.println("Reading line: " + line);
                    if (line.contains("nan")) {
                        System.out.println("Line includes value: 'nan'. Skipping ...");
                        continue;

                    } else if (lines.length != 2 ) {
                        System.out.println("Skipping line due to unexpected data formatting.");
                        continue;

                    } else if (line.trim().contains("correct") && !line.trim().contains("incorrect")) {
                        trialNum = Double.parseDouble(lines[0]);
                        System.out.println("Read Correct Trial");
                        numCorrect = numCorrect + 1;
                    } else if (line.trim().contains("incorrect")) { 
                        trialNum = Double.parseDouble(lines[0]);
                        System.out.println("Read Non Correct Trial");
                        numIncorrect = numIncorrect + 1;
                    } else if (line.trim().contains("invalid_press")) {
                        trialNum = Double.parseDouble(lines[0]);
                        System.out.println("Read Invalid Keypress Trial");
                        numInvalid = numInvalid + 1;
                    } else if (line.trim().contains("no_press")) {
                        trialNum = Double.parseDouble(lines[0]);
                        System.out.println("Read No Keypress Trial");
                        numNp = numNp + 1;
                    } else {
                        System.out.println("Invalid Data, continuing ...");
                        continue;
                        // trialNum = Double.parseDouble(lines[0]);
                        // System.out.println("Unexpected data for TR: " + trialNum + ": " + lines[1]);
                    }

                    System.out.println("Trial Number: " + trialNum);
                    correctSeries.add(trialNum, (numCorrect / trialNum) * 100);
                    nopressSeries.add(trialNum, (numNp / trialNum) * 100);
                    invalidSeries.add(trialNum, (numInvalid / trialNum) * 100);
                    incorrectSeries.add(trialNum, (numIncorrect / trialNum) * 100);
        
                }
            } catch (IOException e) {
                System.err.println("Error Reading CSV File: " + e);
            }


            try {
                System.out.println("Waiting ...");
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public File WaitForNewCSV() {
        System.out.println("Starting Listener...");
        Path csvDirPath = csvDir.toPath();
        
        try (WatchService watchService = FileSystems.getDefault().newWatchService()) {
            csvDirPath.register(watchService, StandardWatchEventKinds.ENTRY_CREATE);

            boolean fileFound = false; 
            while (!fileFound) {
                // Thread waits for an event, then returns a WatchKey with event info 
                WatchKey key = watchService.take(); // Wait for an event
                for (WatchEvent<?> event : key.pollEvents()) {
                    WatchEvent.Kind<?> kind = event.kind();
                    if (kind == StandardWatchEventKinds.ENTRY_CREATE) {
                        Path pathToCreatedFile = csvDirPath.resolve((Path) event.context());
                        System.out.println("New File Created in Dir: " + pathToCreatedFile);
                        if (pathToCreatedFile.getFileName().toString().contains(".csv") && pathToCreatedFile.getFileName().toString().contains("score")) {
                            System.out.println("File accepted. Graphing ...");
                            fileFound = true;
                            return pathToCreatedFile.toFile();
                        } else {
                            System.out.println("File not accepted");
                        }
                    }
                }
                // Reset the WatchKey to continue monitoring
                boolean valid = key.reset();
                if (!valid) {
                    break; // Exit the loop if the key is no longer valid
                }
            }
    } catch (IOException | InterruptedException e) {
        e.printStackTrace();
    }
    return null;
    }
    public void ReadCSVThreadWrapper(File csvFile) {
        ExecutorService readCsvExecutor = Executors.newSingleThreadExecutor();
        readCsvExecutor.submit(() -> {
            ReadCSVFile(csvFile);
        });
    }
}