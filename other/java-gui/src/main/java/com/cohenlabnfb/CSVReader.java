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
import java.util.concurrent.atomic.AtomicInteger;

import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.ValueAxis;
import org.jfree.chart.plot.XYPlot;
import org.jfree.data.xy.XYSeries;

public class CSVReader {
    File csvDir;

    public CSVReader(File csvDir) {
        this.csvDir = csvDir;
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
        ChartPanel[] charts,
        AtomicInteger blockNum,
        AtomicInteger activeBlock,
        AtomicInteger blockTR,
        XYSeries ... seriesArray) {
        ExecutorService readCsvExecutor = Executors.newSingleThreadExecutor();
        readCsvExecutor.submit(() -> {
            if (task == "nfb") {
                nfbReadCSVFile(
                    csvFile, 
                    seriesArray[0], 
                    seriesArray[1], 
                    charts[0], 
                    charts[1], 
                    blockNum, 
                    activeBlock,
                    blockTR);
            } else if (task == "msit") {
                msitReadCSVFile(
                    csvFile, 
                    seriesArray[0], 
                    seriesArray[1], 
                    seriesArray[2], 
                    seriesArray[3], 
                    seriesArray[4], 
                    charts[0], 
                    charts[1], 
                    blockNum, 
                    activeBlock,
                    blockTR);
            } else if (task == "rifg") {
                rifgReadCSVFile(
                    csvFile, 
                    seriesArray[0], 
                    seriesArray[1], 
                    seriesArray[2], 
                    seriesArray[3], 
                    seriesArray[4], 
                    charts[0], 
                    charts[1], 
                    blockNum, 
                    activeBlock,
                    blockTR);
            }
        });
    }

    public void nfbReadCSVFile(
        File csvFile, 
        XYSeries scoreSeries,
        XYSeries activationSeries,
        ChartPanel scoreChartPanel,
        ChartPanel activationChartPanel,
        AtomicInteger blockNum, 
        AtomicInteger activeBlock, 
        AtomicInteger blockTR) {
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
                    } else {
                        try {
                            blockTR.set(Integer.parseInt(lines[0]));
                            if (blockTR.get() < 20 || blockTR.get() > 140 ) {
                                activeBlock.set(0);
                            } else {
                                activeBlock.set(1);
                            }

                            double totalTR = Double.parseDouble(lines[2]);
                            double nfbScore = Double.parseDouble(lines[1]);
                            double activationMean = Double.parseDouble(lines[4]);
                            blockNum.set(Integer.parseInt(lines[3])); // set instead of re-assign
                            System.out.println("totalTR: " + totalTR);
                            System.out.println("NFB Score: " + nfbScore);
                            System.out.println("Mean Activation Value: " + activationMean);
                            System.out.println("Block Num: " + blockNum);
                            
                            
                            scoreSeries.add(totalTR, nfbScore);
                            activationSeries.add(totalTR, activationMean);
                            
                            // set yaxis based on activation for the activation score graph
                            JFreeChart activationChart = activationChartPanel.getChart();
                            XYPlot plot = activationChart.getXYPlot();
                            ValueAxis yAxisActivationChart = plot.getRangeAxis();
                            double yAxisMin = activationSeries.getMinY();
                            double yAxisMax = activationSeries.getMaxY();

                            yAxisActivationChart.setRange(yAxisMin - 1, yAxisMax + 1);
                            
                            
                        } catch (Exception e) {
                            if (line.contains("TR")) {
                                System.out.println("Header Line Likely Detected: " + line);
                            } else {
                                System.out.println("Error parsing line: " + line);
                                System.out.println(e);  
                            }
                        }
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
        XYSeries invalidSeries,
        XYSeries allNotCorrectSeries, 
        ChartPanel scoreChartPanel,
        ChartPanel notCorrectChartPanel,
        AtomicInteger blockNum,
        AtomicInteger activeBlock,
        AtomicInteger blockTR) {

        // Initialize Headers and Vars  
        String line; 

        // FileReader opens the file for reading., BufferedReader adds efficiency by reading chunks of data at a time, rather than one character at a time.
        while (true) {
            double numCorrect = 0;
            double numIncorrect = 0;
            double trialNum = 0;   
            double numInvalid = 0;
            double numNp = 0;
            int activeBlockCurrLineVal = 0;
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
                    } else if (line.trim().contains("rest")) {
                        trialNum = Double.parseDouble(lines[0]);
                        System.out.println("Read Rest Block");
                    } else {
                        System.out.println("Invalid Data, continuing ...");
                        continue;
                    }

                    if (line.contains("rest")) {
                        activeBlockCurrLineVal = 0;
                    } else if (line.contains("333")) {
                        activeBlockCurrLineVal = 1;
                    } else if (line.contains("444")) {
                        activeBlockCurrLineVal = 2;
                    }
                    System.out.println("Trial Number: " + trialNum);
                    correctSeries.add(trialNum, (numCorrect / trialNum) * 100);
                    nopressSeries.add(trialNum, (numNp / trialNum) * 100);
                    invalidSeries.add(trialNum, (numInvalid / trialNum) * 100);
                    incorrectSeries.add(trialNum, (numIncorrect / trialNum) * 100);

                    allNotCorrectSeries.add(trialNum, ((numNp + numInvalid + numIncorrect) / trialNum) * 100);
                    
                    System.out.println("% Incorrect: " + (numNp / trialNum) * 100);
                    System.out.println("Number of no presses: " + numNp);
                    System.out.println("Number of trial: " + trialNum);
                    // add xaxis 0 - 100% for the correct % (-10 to 110 so we can see values at 0 and 100)
                    JFreeChart notCorrectChart = notCorrectChartPanel.getChart();
                    XYPlot plot = notCorrectChart.getXYPlot();
                    ValueAxis yAxisNotCorrectChart = plot.getRangeAxis();
                    yAxisNotCorrectChart.setRange(-10, 110);

                    JFreeChart scoreChart = scoreChartPanel.getChart();
                    XYPlot scorePlot = scoreChart.getXYPlot();
                    ValueAxis yAxisCcoreChartPanel = scorePlot.getRangeAxis();
                    yAxisCcoreChartPanel.setRange(-10, 110);
        
                }
            } catch (IOException e) {
                System.err.println("Error Reading CSV File: " + e);
            }

            activeBlock.set(activeBlockCurrLineVal);

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
        XYSeries faSeries,
        XYSeries percentCorrectSeries,
        ChartPanel scoreChartPanel,
        ChartPanel correctChartPanel, 
        AtomicInteger blockNum,
        AtomicInteger activeBlock,
        AtomicInteger blockTR) {
        // Initialize Headers and Vars  
        String line; 

        // FileReader opens the file for reading., BufferedReader adds efficiency by reading chunks of data at a time, rather than one character at a time.
        while (true) {
            double totalTRS = 0;
            double numHits = 0; 
            double numMiss = 0;
            double numCR = 0; 
            double numFA = 0; 
            int activeBlockCurrLineVal = 0;

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
                    } else if (line.trim().contains("rest")) {
                        totalTRS = Double.parseDouble(lines[0]);
                        System.out.println("Read Rest Block");
                        activeBlockCurrLineVal = 0;
                    } 

                    if (line.contains("buzz")) {
                        activeBlockCurrLineVal = 1;
                    } else if (line.trim().contains("bear")) {
                        activeBlockCurrLineVal = 2;
                    }

                    hitSeries.add(totalTRS, (numHits / totalTRS) * 100);
                    missSeries.add(totalTRS, (numMiss / totalTRS) * 100);
                    crSeries.add(totalTRS, (numCR / totalTRS) * 100);
                    faSeries.add(totalTRS, (numFA / totalTRS) * 100);
                    percentCorrectSeries.add(totalTRS, ((numHits + numCR) / totalTRS) * 100);

                    // add xaxis 0 - 100% for the correct % (-10 to 110 so we can see values at 0 and 100)
                    JFreeChart correctChart = correctChartPanel.getChart();
                    XYPlot plot = correctChart.getXYPlot();
                    ValueAxis yAxisCorrectChart = plot.getRangeAxis();
                    yAxisCorrectChart.setRange(-10, 110);

                    JFreeChart scoreChart = scoreChartPanel.getChart();
                    XYPlot scorePlot = scoreChart.getXYPlot();
                    ValueAxis yAxisCcoreChartPanel = scorePlot.getRangeAxis();
                    yAxisCcoreChartPanel.setRange(-10, 110);
                }

            } catch (IOException e) {
                System.err.println("Error Reading CSV File: " + e);
            }

            activeBlock.set(activeBlockCurrLineVal);

            try {
                System.out.println("Waiting ...");
                Thread.sleep(10);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
