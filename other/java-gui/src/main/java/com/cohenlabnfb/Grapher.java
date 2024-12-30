package com.cohenlabnfb;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.SwingWorker;
import javax.swing.UIManager;
import javax.swing.border.EmptyBorder;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.title.LegendTitle;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
import org.jfree.ui.RectangleInsets;


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
        try {
            // Set a cross-platform look and feel
            UIManager.setLookAndFeel(UIManager.getCrossPlatformLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }
        String csvDirPath;
        String xAxisHeader = "TR";
        String yAxisHeader = "Score";
        String graphTitle = "Score Graph";
        String labelFont = "Times New Roman";
        int labelFontSize = 20;
        Color panelFrameColor = new Color(211, 211, 211);
        Color backgroundColor = new Color(173, 216, 230);
        
        // get csv data and setup data collection objects and vars
        if (task == "nfb") {
            graphTitle = "Neurofeedback Score Graph";
            csvDirPath = System.getenv("NFB_SCORE_LOG_DIR");

            series1 = new XYSeries("Score");
            dataset = new XYSeriesCollection();
            dataset.addSeries(series1);

        } else if (task == "rifg") {
            csvDirPath = System.getenv("RIFG_SCORE_LOG_DIR");
            graphTitle = "RIFG Task Score Graph";

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
            yAxisHeader = "Percent of Trials";

        } else if (task == "msit") {
            csvDirPath = System.getenv("MSIT_SCORE_LOG_DIR");
            graphTitle = "MSIT Task Score Graph";

            correctSeries = new XYSeries("Percent Correct");
            incorrectSeries = new XYSeries("Percent Incorrect");
            invalidSeries = new XYSeries("Percent Invalid Keypresses");
            nopressSeries = new XYSeries("Percent No Keypresses");
            
            dataset = new XYSeriesCollection();
            dataset.addSeries(correctSeries);
            dataset.addSeries(incorrectSeries);
            dataset.addSeries(invalidSeries);
            dataset.addSeries(nopressSeries);
            yAxisHeader = "Percent of Trials";
        } else {
            System.out.println("When running grapher, please make param task equal to a valid task.");
            csvDirPath = System.getenv("HOME");
        }
        csvDir = new File(csvDirPath);
        System.out.println("Selected directory: " + csvDir.getAbsolutePath());

        // make frame 
        frame = new JFrame("Score Graph");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        // frame.setLayout(new FlowLayout());
        frame.setLayout(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(10, 10, 10, 10);  // top, left, bottom, right padding
        JPanel contentPane = (JPanel) frame.getContentPane();
        contentPane.setBackground(backgroundColor);
        contentPane.setOpaque(true);
        int frameWidth = 1200;
        int frameHeight = 625;
        frame.setSize(frameWidth, frameHeight);
        
        // make graph title 
        JLabel chartTile = new JLabel(graphTitle);
        chartTile.setFont(new Font(labelFont, Font.BOLD, labelFontSize));
        
        JPanel chartTitlePanel = new JPanel(new FlowLayout());
        chartTitlePanel.setOpaque(true); 
        chartTitlePanel.setBackground(panelFrameColor);
        chartTitlePanel.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createEtchedBorder(),
            new EmptyBorder(5, 10, 5, 10)));

        gbc.gridx = 0;  // Column position
        gbc.gridy = 0;  // Row position
        chartTitlePanel.add(chartTile, gbc);
        frame.add(chartTitlePanel);

        // make graph chart 
        chart = ChartFactory.createXYLineChart(
            "", 
            xAxisHeader,
            yAxisHeader,
            dataset,
            PlotOrientation.VERTICAL,
            true,    // Show legend
            true,   // Tooltips
            false   // URLs
        );

        // Get the chart's legend and set the font
        LegendTitle legend = chart.getLegend();
        Font legendFont = new Font("Times New Roman", Font.PLAIN, 14); // Change font and size
        legend.setItemFont(legendFont); // Set the legend font


        // Make panel to put chart on 
        XYPlot plot = chart.getXYPlot();
        
        plot.setInsets(new RectangleInsets(10, 20, 10, 40));  // Top, Left, Bottom, Right padding
        int chartPanelWidth = 500;
        int chartPanelHeight = 400;
        chartPanel = new ChartPanel(chart);
        chartPanel.setPreferredSize(new java.awt.Dimension(chartPanelWidth, chartPanelHeight));

        JPanel chartPanelFrame = new JPanel();
        chartPanelFrame.setBorder(BorderFactory.createEtchedBorder());
        chartPanelFrame.setOpaque(true); 
        chartPanelFrame.setBackground(panelFrameColor);
        chartPanelFrame.setPreferredSize(new Dimension(chartPanelWidth + 40, chartPanelHeight + 40));
        chartPanelFrame.setLayout(new GridBagLayout());
        GridBagConstraints gbcChart = new GridBagConstraints();

        gbcChart.gridx = 0; // Position in the grid (center horizontally)
        gbcChart.gridy = 0; // Position in the grid (center vertically)
        gbcChart.anchor = GridBagConstraints.CENTER; // Ensure the component is centered
        chartPanelFrame.add(chartPanel, gbcChart);

        gbc.gridx = 0;  // Column position
        gbc.gridy = 1;  // Row position
        frame.add(chartPanelFrame, gbc);

        // get MRI Screen 
        Object[] mriInfo = SecondMonitorViewer.MakeMRIScreen(frame);
        JLabel mriScreen = (JLabel) mriInfo[0];
        int mriImageWidth = (int) mriInfo[1];
        int mriImageHeight = (int) mriInfo[2];

        // make Panel for MRI Screen 
        JPanel mriScreenPanel = new JPanel();
        mriScreenPanel.setBorder(BorderFactory.createEtchedBorder());
        mriScreenPanel.setOpaque(true); 
        mriScreenPanel.setBackground(panelFrameColor);
        mriScreenPanel.setPreferredSize(new Dimension(mriImageWidth + 40, mriImageHeight + 40));
        mriScreenPanel.setLayout(new GridBagLayout());
        GridBagConstraints gbcMriScreen = new GridBagConstraints();
        gbcMriScreen.anchor = GridBagConstraints.CENTER;
        mriScreenPanel.add(mriScreen, gbcMriScreen);

        // Add title for MRI screen 
        JLabel mriScreenTile = new JLabel("Participant View");
        mriScreenTile.setFont(new Font(labelFont, Font.BOLD, labelFontSize));
        
        JPanel mriScreenTilePanel = new JPanel(new FlowLayout());
        mriScreenTilePanel.setOpaque(true); 
        mriScreenTilePanel.setBackground(panelFrameColor);
        mriScreenTilePanel.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createEtchedBorder(),
            new EmptyBorder(5, 10, 5, 10)));

        gbc.gridx = 0;  // Column position
        gbc.gridy = 0;  // Row position
        mriScreenTilePanel.add(mriScreenTile, gbc);
        frame.add(mriScreenTilePanel);

        gbc.gridx = 1;  // Column position
        gbc.gridy = 1;  // Row position
        gbc.anchor = GridBagConstraints.CENTER;
        frame.add(mriScreenPanel, gbc);
        
        // make option panel and buttons for getting data
        JPanel optionPanel = new JPanel(new FlowLayout());
        optionPanel.setOpaque(true); 
        optionPanel.setBackground(panelFrameColor);
        optionPanel.setBorder(BorderFactory.createEtchedBorder());

        header = new JLabel("Please Select a CSV File to Graph.");
        header.setBorder(new EmptyBorder(10, 10, 10,10));
        optionPanel.add(header);
        
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
        optionPanel.add(waitForNewCSVButton);

        selectFileButton = new JButton("Select a File to Graph");
        FileSystemGUI.createFileButton(selectFileButton, frame, csvFile -> {
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
        optionPanel.add(selectFileButton);

        JButton exitButton = new JButton("Exit");
        exitButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                System.out.println("Exiting Grapher Now.");
                frame.setVisible(false);
            }
        });
        optionPanel.add(exitButton);
        gbc.gridx = 0;  // Column position
        gbc.gridy = 2;  // Row position
        gbc.gridwidth = 2;  // Spans 2 columns
        frame.add(optionPanel, gbc);
        frame.setVisible(true);
    }
}