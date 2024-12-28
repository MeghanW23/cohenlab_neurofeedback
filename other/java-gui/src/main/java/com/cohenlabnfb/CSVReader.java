package com.cohenlabnfb;

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

import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.XYPlot;
import org.jfree.data.xy.XYSeries;

public class CSVReader {
    File csvDir;
    JFreeChart chart;

    public CSVReader(File csvDir, JFreeChart chart) {
        this.csvDir = csvDir;
        this.chart = chart;
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
    
    public void ReadCSVThreadWrapper(
        String task, 
        File csvFile, 
        XYSeries ... seriesArray) {
        ExecutorService readCsvExecutor = Executors.newSingleThreadExecutor();
        readCsvExecutor.submit(() -> {
            if (task == "nfb") {
                nfbReadCSVFile(csvFile, seriesArray[0]);
            } else if (task == "msit") {
                msitReadCSVFile(csvFile, seriesArray[0], seriesArray[1], seriesArray[2], seriesArray[3]);
            } else if (task == "rifg") {
                rifgReadCSVFile(csvFile, seriesArray[0], seriesArray[1], seriesArray[2], seriesArray[3]);
            }
        });
    }

    public void nfbReadCSVFile(
        File csvFile, 
        XYSeries series1) {
        // Initialize Headers and Vars  
        String line; 

        // FileReader opens the file for reading., BufferedReader adds efficiency by reading chunks of data at a time, rather than one character at a time.
        while (true) {
            try (BufferedReader br = new BufferedReader(new FileReader(csvFile))) {
                while ((line = br.readLine()) != null) {
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
                   
                    if (line.contains("nan")) {
                        System.out.println("Line includes value: 'nan'. Skipping ...");
                        continue;
                    } else if (lines.length != 2 ) {
                        System.out.println("Skipping line due to unexpected data formatting.");
                        continue;
                    } else if (line.trim().matches("[-]?\\d+\\s*,\\s*[-]?\\d+\\.?\\d*")) {
                        double x_point = Double.parseDouble(lines[0]);
                        double y_point = Double.parseDouble(lines[1]);
                        System.out.println("X Point: " + x_point);
                        System.out.println("Y Point: " + y_point);
                        series1.add(x_point, y_point);
                        } else {
                            XYPlot plot = chart.getXYPlot();
                            plot.getDomainAxis().setLabel(lines[0]);
                            plot.getRangeAxis().setLabel(lines[1]);
                            System.out.println("Found New X Axis: " + lines[0] + " and Y Axis: " + lines[1]);   
                        }
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

    public void msitReadCSVFile(
        File csvFile, 
        XYSeries correctSeries, 
        XYSeries incorrectSeries,
        XYSeries nopressSeries, 
        XYSeries invalidSeries) {

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

    public void rifgReadCSVFile(
        File csvFile,
        XYSeries hitSeries,
        XYSeries missSeries,
        XYSeries crSeries,
        XYSeries faSeries) {
        // Initialize Headers and Vars  
        String line; 

        // FileReader opens the file for reading., BufferedReader adds efficiency by reading chunks of data at a time, rather than one character at a time.
        while (true) {
            double totalTRS = 0;
            double numHits = 0; 
            double numMiss = 0;
            double numCR = 0; 
            double numFA = 0; 

            try (BufferedReader br = new BufferedReader(new FileReader(csvFile))) {
                while ((line = br.readLine()) != null) {
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
                    System.out.println("Reading Line: " + line);
                    if (line.contains("nan")) {
                        System.out.println("Line includes value: 'nan'. Skipping ...");
                        continue;
                    } else if (lines.length != 2 ) {
                        System.out.println("Skipping line due to unexpected data formatting.");
                        continue;
                    } else if (line.trim().contains("hit")) {
                        totalTRS = Double.parseDouble(lines[0]);
                        numHits = numHits + 1;
                        System.out.println("TR: " + totalTRS + ", Hit");
                    } else if (line.trim().contains("miss")) {
                        totalTRS = Double.parseDouble(lines[0]);
                        numMiss = numMiss + 1;
                        System.out.println("TR: " + totalTRS + ", Miss");
                    } else if (line.trim().contains("correct")) {
                        totalTRS = Double.parseDouble(lines[0]);
                        numCR = numCR + 1;
                        System.out.println("TR: " + totalTRS + ", Correct Rejection");
                    }  else if (line.trim().contains("false")) {
                        totalTRS = Double.parseDouble(lines[0]);
                        numFA = numFA + 1;
                        System.out.println("TR: " + totalTRS + ", False Alarm");
                    } 
                    hitSeries.add(totalTRS, numHits / totalTRS);
                    missSeries.add(totalTRS, numMiss / totalTRS);
                    crSeries.add(totalTRS, numCR / totalTRS);
                    faSeries.add(totalTRS, numFA / totalTRS);
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
}
