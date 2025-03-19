package com.cohenlab;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardWatchEventKinds;
import java.nio.file.WatchEvent;
import java.nio.file.WatchKey;
import java.nio.file.WatchService;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;

import javax.swing.JOptionPane;

import org.jfree.data.category.DefaultCategoryDataset;


public class ReadCSV {

    private final String directoryPath; 
    private String csvPath = null;
    private boolean optedToWaitForCsv = false;

    ReadCSV(String directoryPath) {
        this.directoryPath = directoryPath;
    }

    public void setCsvPath(String inputCsvPath) {
        this.csvPath = inputCsvPath;

    }

    public synchronized String getCsvPath(boolean justGetCSV) {
        if (justGetCSV) {
            return csvPath;
        }
        while (csvPath == null) {
            try {
                wait(); // Wait until notified that csvPath is set
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                System.err.println("Thread interrupted while waiting for CSV path.");
            }
        }
        return csvPath;
    }

    public synchronized void setCsvPathForWaiting(String pathName) {
        this.csvPath = Paths.get(this.directoryPath, pathName).toString();
        notifyAll(); // Notify all waiting threads that csvPath has been set
    }    

    public boolean GetMostRecentCSV() {
        System.out.println("Searching for .csv files in: " + this.directoryPath);
        File directory = new File(this.directoryPath);
        
        // check if directory exists and is a directory 
        if (!directory.exists() || !directory.isDirectory()) {
            throw new IllegalArgumentException("Inputted directoryPath is not a valid Directory"); 
        }
        
        // list all files in the dir
        File[] csvFiles = directory.listFiles();
        
        if (csvFiles == null || csvFiles.length == 0) {
            System.out.println("No Available CSV Files in the Directory: " + this.directoryPath);
            JOptionPane.showMessageDialog(null, "There are no score CSVs to process for this task");
            return false;

        } else {
            // get most recent csv file 
            File mostRecentFile = Arrays.stream(csvFiles)
            .filter(file -> file.getName().endsWith(".csv"))
            .max(Comparator.comparingLong(File::lastModified)).orElse(null);

            if (mostRecentFile == null ) {
                System.out.println("No Available CSV Files in the Directory: " + this.directoryPath);
                JOptionPane.showMessageDialog(null, "There are no score CSVs to process for this task");
                return false;

            } else {
                this.csvPath = mostRecentFile.toString();
                System.out.println("Most Recent File " + this.csvPath);
                return true;

            }
        }
    }

    public void OptToWaitForCsv() {
        this.optedToWaitForCsv = true;
    }
    public void StartWaitingForCSVIfOptedIn() {
        if (this.optedToWaitForCsv) {
            new Thread(() -> WaitForCSV()).start();
        }
       
    }

    public void WaitForCSV() {

        try (WatchService watchService = FileSystems.getDefault().newWatchService()) {
            Path directory = Paths.get(this.directoryPath);

            directory.register(watchService, StandardWatchEventKinds.ENTRY_CREATE);
            System.out.println("Waiting for a New CSV in Directory: " + this.directoryPath);

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
                    Path filePath = (Path) event.context(); // The file affected by the event

                    if (kind == StandardWatchEventKinds.ENTRY_CREATE) {
                        setCsvPathForWaiting(filePath.toString());
                        System.out.println("Using CSV File: " + this.csvPath);

                        break;
                    }
                }
            }
            
        } catch (Exception e) {
            System.out.println("Error Waiting for New CSV: " + e);
        }
    }

    public String getCSVLine() {
        try (BufferedReader br = new BufferedReader(new FileReader(this.csvPath))) {
            String line; 
            String lastLine = null; 

            while ((line = br.readLine()) != null) {
                lastLine = line;
            }
            return lastLine;

        } catch (IOException e) {
            System.out.println(e);
            return null;
        }
    }

    public List<String> getAllCSVLines(boolean removeHeaders, String task) {
        try (BufferedReader br = new BufferedReader(new FileReader(this.csvPath))) {
            String line; 
            List<String> allLines = new ArrayList<>();

            int lineCount = 0;
            while ((line = br.readLine()) != null) {
                System.out.println(line);
                if (removeHeaders) {
                    lineCount += 1;

                    if (lineCount == 1) {

                    } else if ((line.trim().toLowerCase().contains("rest")) && !"Neurofeedback".equals(task)) {

                        System.out.println("Skipping Rest");

                    } else if (line.trim().isEmpty()) {
                        System.out.println("Skipping empty string ");
                        

                    } else {
                        System.out.println("Including: " + line);
                        allLines.add(line);

                    }
                } 
               
            }
            if (allLines.isEmpty()) {
                System.out.println("No Trial Lines Found");
            }   
            return allLines;

        } catch (IOException e) {
            return null;
        }
    }

    public List<String> parseCSVData(String csvLine, String task) {
        String[] values = csvLine.split(",");
        for (int i = 0; i < values.length; i++) {
            if ("nan".equals(values[i])) {
                System.out.println("Changing Nan to 0.");
                values[i] = "0";
            }
        }

        int[] columnsToPlot;

        switch (task) {
            case "nfb":
                columnsToPlot = Constants.nfbColumnsToPlot;
                break;

            case "rifg":
                columnsToPlot = Constants.rifgColumnsToPlot;
                break;

            case "msit":
                columnsToPlot = Constants.msitColumnsToPlot;
                break;

            default:
                return null;
        }
        
        // get values from csv String
        List<String> valuesToPlotList = new ArrayList<>();
        for (int columnIndex : columnsToPlot) {
            System.out.println(values[columnIndex]);
            valuesToPlotList.add(values[columnIndex]);            
        }

        return valuesToPlotList;
    }
    
    public DefaultCategoryDataset addNfbDataToDataset(List<String> valueList, DefaultCategoryDataset dataset) {
        dataset.addValue(Double.valueOf(valueList.get(1)), "Activation", Double.valueOf(valueList.get(0)));
        return dataset;
    }

    public DefaultCategoryDataset addRifgDataToDataset(List<String> valueList, DefaultCategoryDataset dataset) {

        dataset.addValue(Double.valueOf(valueList.get(1)), "Activation", Double.valueOf(valueList.get(0)));
        return dataset;
    }

    public void waitForNewCsvData() {
        try (WatchService watchService = FileSystems.getDefault().newWatchService()) {

            Path csvDirPath = Paths.get(this.directoryPath);
            csvDirPath.register(watchService, StandardWatchEventKinds.ENTRY_MODIFY);

            System.out.println("Waiting for New Data...");

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

                    if (kind == StandardWatchEventKinds.ENTRY_MODIFY) {
                        System.out.println("New Data added to csv");

                        return;
                    }
                }

                // Reset the key so the watchService can continue to monitor the directory
                boolean valid = key.reset();
                if (!valid) {
                    break; // Exit if the key is no longer valid (e.g., directory is deleted)
                }
            }
            
            
        } catch (Exception e) {
            System.out.println("Error Waiting for New CSV: " + e);
        }
    }
}

