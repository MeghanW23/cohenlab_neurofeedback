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
    private JLabel header;
    private JButton waitForNewCSVButton;
    private JButton selectFileButton;
    private String task;
    private String fontName = "Times New Roman";

    public Grapher(String task) {
        this.task = task;
    }
    public static File GetCsvPath() {
        return csvDir;
    }
    public void MakeGraphPanel() {
        // Set a cross-platform look and feel
        try {
            UIManager.setLookAndFeel(UIManager.getCrossPlatformLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }

        // graph visual knobs 
        int labelFontSize = 20;
        Color panelFrameColor = new Color(211, 211, 211);
        Color backgroundColor = new Color(173, 216, 230);
        int frameWidth = 1200;
        int frameHeight = 625;
        int chartPanelWidth = 500;
        int chartPanelHeight = 400;
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(10, 10, 10, 10);  // top, left, bottom, right padding

        // make frame 
        frame = new JFrame("Task Dashboard");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new GridBagLayout());
        JPanel contentPane = (JPanel) frame.getContentPane();
        contentPane.setBackground(backgroundColor);
        contentPane.setOpaque(true);
        frame.setSize(frameWidth, frameHeight);
        
        // make chart 
        Object[] graphVars = initializeGraphVars(task);
        if (graphVars == null) {
            System.out.println("Invalid task provided to Grapher.initializeGraphVars()");
            System.exit(1);
        }
        XYSeries[] seriesList = (XYSeries[]) graphVars[0];
        csvDir = new File((String) graphVars[2]);
        String[] chartTitles = (String[]) graphVars[1];
        String[] xAxisHeaders = (String[])  graphVars[3];
        String[] yAxisHeaders = (String[])  graphVars[4];        
        int[][] firstChartSeriesNum = (int[][]) graphVars[5];

        System.out.println("Selected directory: " + csvDir.getAbsolutePath());

        // make chart 
        JPanel chartPanel = MakeChart(xAxisHeaders[0], yAxisHeaders[0], seriesList, firstChartSeriesNum[0], chartPanelWidth, chartPanelHeight); // make chart
        //JPanel chartPanel2 = MakeChart(xAxisHeaders[0], yAxisHeaders[0], seriesList, firstChartSeriesNum[0], chartPanelWidth, chartPanelHeight); // make chart
        
        // make chart title panel 
        JLabel chartTile = new JLabel(chartTitles[0]);
        chartTile.setFont(new Font(fontName, Font.BOLD, labelFontSize));
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
        
        // make chart image's grey outside panel 
        JPanel chartPanelFrame = new JPanel();
        chartPanelFrame.setBorder(BorderFactory.createEtchedBorder());
        chartPanelFrame.setOpaque(true); 
        chartPanelFrame.setBackground(panelFrameColor);
        chartPanelFrame.setPreferredSize(new Dimension(chartPanelWidth + 40, chartPanelHeight + 40));
        chartPanelFrame.setLayout(new GridBagLayout());
        GridBagConstraints gbcForChart = new GridBagConstraints();
        gbcForChart.gridx = 0; // Position in the grid (center horizontally)
        gbcForChart.gridy = 0; // Position in the grid (center vertically)
        gbcForChart.anchor = GridBagConstraints.CENTER; // Ensure the component is centered

        // add chart to outer panel and then add outer panel to frame 
        chartPanelFrame.add(chartPanel, gbcForChart);
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
        //JLabel mriScreenTile = new JLabel("Participant View");
        mriScreenTile.setFont(new Font(fontName, Font.BOLD, labelFontSize));
        
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
                        CSVReader reader = new CSVReader(csvDir);
                        return reader.WaitForNewCSV();
                    }

                    @Override
                    protected void done() {
                        try {
                            File csvFilePath = get(); // Retrieve the result of WaitForNewCSV
                            CSVReader reader = new CSVReader(csvDir);
                            if (task == "nfb") {
                                reader.ReadCSVThreadWrapper(
                                    "nfb", 
                                    csvFilePath, 
                                    seriesList[0]);
                            } else if (task == "msit") {
                                reader.ReadCSVThreadWrapper(
                                    "msit",  
                                    csvFilePath, 
                                    seriesList[0], 
                                    seriesList[1], 
                                    seriesList[2], 
                                    seriesList[3]);
                            } else if (task == "rifg") {
                                reader.ReadCSVThreadWrapper(
                                    "rifg", 
                                    csvFilePath,
                                    seriesList[0], 
                                    seriesList[1], 
                                    seriesList[2], 
                                    seriesList[3]);
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
                // get the csv file selected and show user
                System.out.println("Selected CSV File: " +  csvFile);
                File csvFilePath = new File(csvFile);
                header.setText("Reading from File: " + csvFilePath.getName());

                // delete the buttons for getting the csv
                waitForNewCSVButton.setVisible(false);
                selectFileButton.setVisible(false);

                // read the data from the csv file and update the series data
                CSVReader reader = new CSVReader(csvDir);
                if (task == "nfb") {
                    reader.ReadCSVThreadWrapper(
                        "nfb", 
                        csvFilePath, 
                        seriesList[0]);
                } else if (task == "msit") {
                    reader.ReadCSVThreadWrapper(
                        "msit", 
                        csvFilePath, 
                        seriesList[0], 
                        seriesList[1], 
                        seriesList[2], 
                        seriesList[3]);
                } else if (task == "rifg") {
                    reader.ReadCSVThreadWrapper(
                        "rifg",
                        csvFilePath,
                        seriesList[0], 
                        seriesList[1], 
                        seriesList[2], 
                        seriesList[3]);
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

    public JPanel MakeChart(String xAxisHeader, String yAxisHeader, XYSeries[] seriesList, int[] seriesNumsToUse, int chartPanelWidth, int chartPanelHeight) {
        XYSeriesCollection dataset = new XYSeriesCollection(); // make empty dataset 

        
        for (int seriesNum : seriesNumsToUse) {
            dataset.addSeries(seriesList[seriesNum]);
        }

        // make graph chart 
        JFreeChart chart = ChartFactory.createXYLineChart(
            "", 
            xAxisHeader,
            yAxisHeader,
            dataset,
            PlotOrientation.VERTICAL,
            true,    // Show legend
            true,   // Tooltips
            false   // URLs
        );

        // set graph fonts
        XYPlot plot = chart.getXYPlot();
        plot.getDomainAxis().setLabelFont(new Font(fontName, Font.PLAIN, 14)); // X-axis label font
        plot.getDomainAxis().setTickLabelFont(new Font(fontName, Font.PLAIN, 12)); // X-axis tick label font
        plot.getRangeAxis().setLabelFont(new Font(fontName, Font.PLAIN, 14)); // Y-axis label font
        plot.getRangeAxis().setTickLabelFont(new Font(fontName, Font.PLAIN, 12)); // Y-axis tick label font

        // Get the chart's legend and set the font
        LegendTitle legend = chart.getLegend();
        Font legendFont = new Font(fontName, Font.PLAIN, 12); 
        legend.setItemFont(legendFont);

        plot.setInsets(new RectangleInsets(10, 20, 10, 40));  // Top, Left, Bottom, Right padding
        JPanel chartPanel = new ChartPanel(chart);
        chartPanel.setPreferredSize(new java.awt.Dimension(chartPanelWidth, chartPanelHeight));

        return chartPanel;
    }

    private static Object[] initializeGraphVars(String task) {
        switch (task) {
            case "nfb":
                return new Object[] {
                    new XYSeries[]{new XYSeries("Score"), new XYSeries("Activation")}, // Data Series(es)
                    new String[]{"Neurofeedback Score Graph"}, // Graph Title 
                    System.getenv("NFB_SCORE_LOG_DIR"), // Score CSV Directory
                    new String[]{"TR"}, // X Axis Header
                    new String[] {"Neurofeedback Score"}, // Y Axis Header
                    new int[][] {new int[]{0}, new int[]{1}}
                };

            case "rifg":
                return new Object[] {
                    new XYSeries[]{new XYSeries("Hits"), new XYSeries("Misses"), new XYSeries("Correct Rejections"), new XYSeries("False Alarms")},
                    new String[]{"RIFG Task Score Graph"},
                    System.getenv("RIFG_SCORE_LOG_DIR"),
                    new String[]{"TR"},
                    new String[]{"Percent of Trials"},
                    new int[][] {new int[]{0, 1, 2, 3}}
                };

            case "msit":
                return new Object[]{ 
                    new XYSeries[]{new XYSeries("Percent Correct"), new XYSeries("Percent Incorrect"), new XYSeries("Percent No Keypresses"),new XYSeries("Percent Invalid Keypresses")},
                    new String[]{"MSIT Task Score Graph"}, 
                    System.getenv("MSIT_SCORE_LOG_DIR"),
                    new String[]{"TR"},
                    new String[]{"Percent of Trials"},
                    new int[][] {new int[]{0, 1, 2, 3}}
                };      
        }
                return null;
    }
}