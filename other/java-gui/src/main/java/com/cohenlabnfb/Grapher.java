package com.cohenlabnfb;

import java.awt.FlowLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
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


public class Grapher {
    private JFrame frame;
    public static File csvDir;
    private ChartPanel chartPanel;
    private JFreeChart chart;
    private XYSeries series1;
    private XYSeriesCollection dataset;
    private JLabel header;
    private JButton waitForNewCSVButton;
    private JButton selectFileButton;
    private String task;
    private XYSeries correctSeries;
    private XYSeries invalidSeries;
    private XYSeries nopressSeries;
    private XYSeries incorrectSeries;
    private XYSeries hitSeries;
    private XYSeries missSeries;
    private XYSeries crSeries;
    private XYSeries faSeries;

    public Grapher(String task) {
        this.task = task;
    }
    public static File GetCsvPath() {
        return csvDir;
    }
    public void MakeGraphPanel() {
        String csvDirPath;
        String XAxisHeader = "TR";
        String YAxisHeader = "Score";

        if (task == "nfb") {
            csvDirPath = System.getenv("NFB_LOG_DIR");

            series1 = new XYSeries("Score");
            dataset = new XYSeriesCollection();
            dataset.addSeries(series1);

        } else if (task == "rifg") {
            csvDirPath = System.getenv("RIFG_LOG_DIR");

            double totalTRS = 0;
            double numHits = 0; 
            double numMiss = 0;
            double numCR = 0; 
            double numFA = 0; 
            
            hitSeries = new XYSeries("Hits");
            hitSeries.add(totalTRS, numHits);

            missSeries = new XYSeries("Misses");
            missSeries.add(totalTRS, numMiss);
        
            crSeries = new XYSeries("Correct Rejections");
            crSeries.add(totalTRS, numCR);

            faSeries = new XYSeries("False Alarms");
            faSeries.add(totalTRS, numFA);

            dataset = new XYSeriesCollection();
            dataset.addSeries(hitSeries);
            dataset.addSeries(missSeries);
            dataset.addSeries(crSeries);
            dataset.addSeries(faSeries);
            YAxisHeader = "Percent of Trials";

        } else if (task == "msit") {
            csvDirPath = System.getenv("MSIT_LOG_DIR");

            correctSeries = new XYSeries("Percent Correct");
            incorrectSeries = new XYSeries("Percent Incorrect");
            invalidSeries = new XYSeries("Percent Invalid Keypresses");
            nopressSeries = new XYSeries("Percent No Keypresses");
            
            dataset = new XYSeriesCollection();
            dataset.addSeries(correctSeries);
            dataset.addSeries(incorrectSeries);
            dataset.addSeries(invalidSeries);
            dataset.addSeries(nopressSeries);
            YAxisHeader = "Percent of Trials";
       
            
        } else {
            System.out.println("When running grapher, please make param task equal to a valid task.");
            csvDirPath = System.getenv("HOME");
        }

        csvDir = new File(csvDirPath);
        System.out.println("Selected directory: " + csvDir.getAbsolutePath());

        frame = new JFrame("Score Graph");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new FlowLayout());

        int frameWidth = 900;
        int frameHeight = 700;
        frame.setSize(frameWidth, frameHeight);

        chart = ChartFactory.createXYLineChart(
            "Score Graph", 
            XAxisHeader,
            YAxisHeader,
            dataset,
            PlotOrientation.VERTICAL,
            true,    // Show legend
            true,   // Tooltips
            false   // URLs
        );

        // Make panel to put chart on 
        int chartPanelWidth = 800;
        int chartPanelHeight = 600;
        chartPanel = new ChartPanel(chart);
        chartPanel.setPreferredSize(new java.awt.Dimension(chartPanelWidth, chartPanelHeight));
        frame.add(chartPanel);

        header = new JLabel("Please Select a CSV File to Graph.");
        header.setBorder(new EmptyBorder(10, 10, 10,10));
        header.setAlignmentX(JLabel.BOTTOM_ALIGNMENT);
        frame.add(header);
        
        waitForNewCSVButton = new JButton("Wait for a New CSV");
        waitForNewCSVButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                header.setText("Waiting for new CSV ...");
                waitForNewCSVButton.setVisible(false);
                selectFileButton.setVisible(false);

                // Use SwingWorker to perform long-running tasks in the background
                SwingWorker<File, Void> worker = new SwingWorker<File, Void>() {
                    @Override
                    protected File doInBackground() throws Exception {
                        CSVReader reader = new CSVReader(csvDir, chart);
                        return reader.WaitForNewCSV();
                    }

                    @Override
                    protected void done() {
                        try {
                            File csvFilePath = get(); // Retrieve the result of WaitForNewCSV
                            CSVReader reader = new CSVReader(csvDir, chart);
                            if (task == "nfb") {
                                reader.ReadCSVThreadWrapper(
                                    "nfb", 
                                    csvFilePath, 
                                    series1);
                            } else if (task == "msit") {
                                reader.ReadCSVThreadWrapper(
                                    "msit", 
                                    csvFilePath, 
                                    correctSeries, 
                                    incorrectSeries, 
                                    nopressSeries, 
                                    invalidSeries);
                            } else if (task == "rifg") {
                                reader.ReadCSVThreadWrapper(
                                    "rifg", 
                                    csvFilePath,
                                    hitSeries,
                                    missSeries,
                                    crSeries,
                                    faSeries
                                );
                            } else {
                                System.out.println("No valid task was given for method: MakeGraphPanel()");
                                System.exit(0);
                            }
                            
                            header.setText("Reading from File: " + csvFilePath.getName());
                        } catch (Exception ex) {
                            header.setText("Error: " + ex.getMessage());
                        }
                    }
                };
                worker.execute();
            }
        });
        frame.add(waitForNewCSVButton);

        selectFileButton = new JButton("Select a File to Graph");
        selectFileButton.setAlignmentX(JFrame.BOTTOM_ALIGNMENT);
        FileSystemGUI.createFileButton("neurofeedback", selectFileButton, frame, csvFile -> {
            if ( csvFile != null ) {
                System.out.println("Selected CSV File: " +  csvFile);
                File csvFilePath = new File(csvFile);
                header.setText("Reading from File: " + csvFilePath.getName());
                waitForNewCSVButton.setVisible(false);
                selectFileButton.setVisible(false);
                CSVReader reader = new CSVReader(csvDir, chart);

                if (task == "nfb") {
                    reader.ReadCSVThreadWrapper(
                        "nfb", 
                        csvFilePath, 
                        series1);
                } else if (task == "msit") {
                    reader.ReadCSVThreadWrapper(
                        "msit", 
                        csvFilePath, 
                        correctSeries, 
                        incorrectSeries, 
                        nopressSeries, 
                        invalidSeries);
                } else if (task == "rifg") {
                    reader.ReadCSVThreadWrapper(
                        "rifg", 
                        csvFilePath,
                        hitSeries,
                        missSeries,
                        crSeries,
                        faSeries
                    );
                } else {
                    System.out.println("No valid task was given for method: MakeGraphPanel()");
                    System.exit(0);
                }
                
            } else {
                System.out.println("No CSV File selected.");
            }

        });

        frame.add(selectFileButton);

        JButton exitButton = new JButton("Exit");
        exitButton.setAlignmentX(JFrame.BOTTOM_ALIGNMENT);
        exitButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                System.out.println("Exiting Grapher Now.");
                frame.setVisible(false);
            }
        });
        frame.add(exitButton);
        frame.setVisible(true);
    }
    
}