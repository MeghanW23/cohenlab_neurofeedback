package com.cohenlabnfb;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.Rectangle;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.geom.Rectangle2D;
import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;
import javax.swing.SwingWorker;
import javax.swing.UIManager;
import javax.swing.border.EmptyBorder;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYLineAndShapeRenderer;
import org.jfree.chart.title.TextTitle;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

public class Grapher {
    private String task;
    private JFrame frame;
    public static File csvDir;

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

        // set visual knobs 
        String fontName = "Times New Roman";

        Color panelFrameColor = new Color(211, 211, 211);
        Color backgroundColor = new Color(173, 216, 230);

        int optionPanelHeaderXLocation = 0;
        int optionPanelHeaderYLocation = 0;
        int optionPanelWaitButtonXLocation = 1;
        int optionPanelWaitButtonYLocation = 0; 
        int optionPanelSelectFileXLocation = 2;
        int optionPanelSelectFileYLocation = 0;
        int optionPanelExitXLocation = 3;
        int optionPanelExitYLocation = 0;

        int mriViewPanelScreenXLocation = 0;
        int mriViewPanelScreenYLocation = 0;
        int mriViewPanelWordsXLocation = 0;
        int mriViewPanelWordsYLocation = 1;

        int frameWidth = 1050;
        int frameHeight = 950;

        int chartWidth = 500;
        int chartHeight = 375;

        int mriImageWidth = 500;
        int mriImageHeight = 275;

        int frameHGap = 10;
        int frameVGap = 10;

        int[] framePadding = {10, 10, 10, 10};
        int[] optionPanelPadding = {5, 5, 5, 5};
        
        int panelNonTitleFontSize = 15;
        int panelTitleFontSize = 20;
        Font panelNonTitleFont = new Font(fontName, Font.PLAIN, panelNonTitleFontSize);        
        Font panelTitleFont = new Font(fontName, Font.BOLD, panelTitleFontSize);

        // initialize variables 
        AtomicInteger blockNum = new AtomicInteger(0);
        AtomicInteger activeBlock = new AtomicInteger(0); // 0 for control / rest, 1 for activity
        AtomicInteger blockTR = new AtomicInteger(0);

        // make frame 
        frame = new JFrame("Realtime Task Dashboard");
        frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        frame.setSize(new Dimension(frameWidth, frameHeight));
        frame.setLayout(new FlowLayout(FlowLayout.CENTER, frameHGap, frameVGap));
        JPanel contentPane = (JPanel) frame.getContentPane();
        contentPane.setBackground(backgroundColor);
        contentPane.setOpaque(true);
        
        // make title 
        String title = new String();
        if (task == "nfb") {
            title = "Neurofeedback Task Dashboard";
        } else if (task == "rifg") {
            title = "RIFG Task Dashboard";
        } else if (task == "msit") {
            title = "MSIT Task Dashboard";
        } 
        JLabel titleLabel = new JLabel(title);
        titleLabel.setFont(panelTitleFont);

        JPanel titlePanel = new JPanel();
        titlePanel.setOpaque(true); 
        titlePanel.setBackground(panelFrameColor);
        titlePanel.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createEtchedBorder(), 
            new EmptyBorder(optionPanelPadding[0], optionPanelPadding[1], optionPanelPadding[2], optionPanelPadding[3])
            ));
        
        titlePanel.add(titleLabel);
        frame.add(titlePanel);

        // make graph panel
        JPanel graphPanel = new JPanel();
        graphPanel.setOpaque(true); 
        graphPanel.setBackground(panelFrameColor);
        graphPanel.setLayout(new FlowLayout(FlowLayout.LEFT, 0, 5));
        graphPanel.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createEtchedBorder(), 
            new EmptyBorder(optionPanelPadding[0], optionPanelPadding[1], optionPanelPadding[2], optionPanelPadding[3])
            ));
        frame.add(graphPanel);

        // make mri view panel
        JPanel mriViewPanel = new JPanel();
        mriViewPanel.setOpaque(true); 
        mriViewPanel.setBackground(panelFrameColor);
        mriViewPanel.setLayout(new GridBagLayout());
        GridBagConstraints gbcMriPanel = new GridBagConstraints();
        gbcMriPanel.insets = new Insets(framePadding[0], framePadding[1], framePadding[2], framePadding[3]);
        mriViewPanel.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createEtchedBorder(), 
            new EmptyBorder(optionPanelPadding[0], optionPanelPadding[1], optionPanelPadding[2], optionPanelPadding[3])
            )); 
            
        // add mri viewer to mri panel
        Object[] mriInfo = SecondMonitorViewer.MakeMRIScreen(frame, mriImageWidth, mriImageHeight);

        JLabel mriScreen = (JLabel) mriInfo[0];
        gbcMriPanel.gridx = mriViewPanelScreenXLocation;
        gbcMriPanel.gridy = mriViewPanelScreenYLocation;
        mriViewPanel.add(mriScreen, gbcMriPanel);
        Rectangle monitorBounds = (Rectangle) mriInfo[3];
        String mriResolutionInformation = new String("No MRI Monitor Detected.");
        try {
            Double monitorWidth = monitorBounds.getWidth();
            Double monitorHeight = monitorBounds.getHeight();
            Double monitorXOff = monitorBounds.getX();
            Double monitorYOff = monitorBounds.getY();
            mriResolutionInformation = new String("MRI Screen Width: " + monitorWidth + ", " + "Height: " + monitorHeight + ", " + "X: " + monitorXOff + ", " + "Y: " + monitorYOff);
        } catch (Exception e) {
            System.out.println("Could not get second montior bounds.");
            mriViewPanel.setPreferredSize(new Dimension(400, 300));
        }
    
        JLabel mriResolutionInformationLabel = new JLabel(mriResolutionInformation);
        mriResolutionInformationLabel.setFont(panelNonTitleFont);
        gbcMriPanel.gridx = mriViewPanelWordsXLocation;
        gbcMriPanel.gridy = mriViewPanelWordsYLocation;
        mriViewPanel.add(mriResolutionInformationLabel, gbcMriPanel);

        frame.add(mriViewPanel);

        // make data panel and add labels 
        JPanel dataPanel = new JPanel();
        dataPanel.setOpaque(true); 
        dataPanel.setBackground(panelFrameColor);
        dataPanel.setLayout(new GridBagLayout());
        GridBagConstraints gbcDataPanel = new GridBagConstraints();
        gbcDataPanel.insets = new Insets(1, 5, 1, 1);
        dataPanel.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createEtchedBorder(), 
            new EmptyBorder(optionPanelPadding[0], optionPanelPadding[1], optionPanelPadding[2], optionPanelPadding[3])
            )); 
        

        JLabel dataPanelTitleLabel = new JLabel(" Task Session Information ");
        dataPanelTitleLabel.setFont(panelTitleFont);

        JPanel dataPanelTitlePanel = new JPanel(new BorderLayout());
        dataPanelTitlePanel.setOpaque(true); 
        dataPanelTitlePanel.setBackground(panelFrameColor);
        dataPanelTitlePanel.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createEtchedBorder(), 
            new EmptyBorder(optionPanelPadding[0], optionPanelPadding[1], optionPanelPadding[2], optionPanelPadding[3])
            )); 
        dataPanelTitlePanel.add(dataPanelTitleLabel, BorderLayout.CENTER);

        gbcDataPanel.gridx = 0;
        gbcDataPanel.gridy = 0;
        dataPanel.add(dataPanelTitlePanel, gbcDataPanel);

        JLabel dataPanelTrialTypeString = new JLabel("Trial Type: " + "Not yet started.");
        dataPanelTrialTypeString.setFont(panelNonTitleFont);
        gbcDataPanel.gridx = 0;
        gbcDataPanel.gridy = 1;
        dataPanel.add(dataPanelTrialTypeString, gbcDataPanel);

        JLabel dataPanelBlockString = new JLabel("Block Number: " + 0);
        dataPanelBlockString.setFont(panelNonTitleFont);
        gbcDataPanel.gridx = 0;
        gbcDataPanel.gridy = 2;
        dataPanel.add(dataPanelBlockString, gbcDataPanel);
        if (task == "rifg") {
            dataPanelBlockString.setVisible(false);
        }

        JLabel dataPanelTrialString = new JLabel("Net Trial Number: " + 0);
        dataPanelTrialString.setFont(panelNonTitleFont);
        gbcDataPanel.gridx = 0;
        gbcDataPanel.gridy = 3;
        dataPanel.add(dataPanelTrialString, gbcDataPanel);

        JLabel dataPanelBlockTrialNumber = new JLabel("Block-Specific Trial Number: " + blockTR);
        dataPanelBlockTrialNumber.setFont(panelNonTitleFont);
        gbcDataPanel.gridx = 0;
        gbcDataPanel.gridy = 4;
        dataPanel.add(dataPanelBlockTrialNumber, gbcDataPanel);
        if (task == "rifg") {
            dataPanelBlockTrialNumber.setVisible(false);
        }

        frame.add(dataPanel);

        // make option panel 
        JPanel optionPanel = new JPanel(new FlowLayout());
        optionPanel.setOpaque(true); 
        optionPanel.setBackground(panelFrameColor);
        optionPanel.setBorder(BorderFactory.createEtchedBorder());
        optionPanel.setLayout(new GridBagLayout());
        GridBagConstraints gbcOptionPanel = new GridBagConstraints();
        gbcOptionPanel.insets = new Insets(optionPanelPadding[0], optionPanelPadding[1], optionPanelPadding[2], optionPanelPadding[3]);  // top, left, bottom, right padding
        frame.add(optionPanel);

        // make option panel header
        JLabel optionHeader = new JLabel("Please Choose an Option to Start:");
        optionHeader.setBorder(new EmptyBorder(10, 10, 10,10));
        optionHeader.setFont(panelNonTitleFont);

        gbcOptionPanel.gridx = optionPanelHeaderXLocation;
        gbcOptionPanel.gridy = optionPanelHeaderYLocation;
        optionPanel.add(optionHeader, gbcOptionPanel);

        // make buttons and add to option panel
        JButton waitForNewCSVButton = new JButton("Wait for a New CSV");
        gbcOptionPanel.gridx = optionPanelWaitButtonXLocation;
        gbcOptionPanel.gridy = optionPanelWaitButtonYLocation;
        optionPanel.add(waitForNewCSVButton, gbcOptionPanel);

        JButton selectFileButton = new JButton("Select a File to Graph");
        gbcOptionPanel.gridx = optionPanelSelectFileXLocation;
        gbcOptionPanel.gridy = optionPanelSelectFileYLocation;
        optionPanel.add(selectFileButton, gbcOptionPanel);

        JButton exitButton = new JButton("Exit");
        gbcOptionPanel.gridx = optionPanelExitXLocation;
        gbcOptionPanel.gridy = optionPanelExitYLocation;
        optionPanel.add(exitButton, gbcOptionPanel);

        // setup graph variables 
        Object[] graphVariables = InitializeGraphVars(task);
        if (graphVariables == null) {
            System.out.println("Invalid task provided to Grapher.InitializeGraphVars()");
            System.exit(1);
        }
        csvDir = new File((String) graphVariables[2]);
        System.out.println("Selected directory: " + csvDir.getAbsolutePath());

        XYSeries[] seriesList = (XYSeries[]) graphVariables[0];
        String[] chartTitles = (String[]) graphVariables[1];
        String[] xAxisHeaders = (String[])  graphVariables[3];
        String[] yAxisHeaders = (String[])  graphVariables[4];        
        int[][] firstChartSeriesNum = (int[][]) graphVariables[5];
    
        // make graphs and add to panel 
        ChartPanel chart = MakeChart(
            chartTitles[0], 
            xAxisHeaders[0], 
            yAxisHeaders[0], 
            seriesList, 
            firstChartSeriesNum[0], 
            chartWidth, 
            chartHeight, 
            panelNonTitleFont, 
            panelTitleFont,
            new Color[]{Color.RED, Color.BLUE, Color.GREEN, Color.YELLOW});
        graphPanel.add(chart);

        ChartPanel chart2 = MakeChart(
            chartTitles[1], 
            xAxisHeaders[0], 
            yAxisHeaders[1], 
            seriesList, 
            firstChartSeriesNum[1], 
            chartWidth, 
            chartHeight, 
            panelNonTitleFont, 
            panelTitleFont,
            new Color[]{Color.MAGENTA});

        graphPanel.add(chart2);

        updateDataPanel(new Object[]{dataPanelTrialTypeString, dataPanelBlockString, dataPanelTrialString, dataPanelBlockTrialNumber}, seriesList, task, blockNum, activeBlock, blockTR);
        
        // add action listeners to buttons
        waitForNewCSVButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                optionHeader.setText("Waiting for new CSV ...");
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
                                    new ChartPanel[]{chart, chart2},
                                    blockNum,
                                    activeBlock,
                                    blockTR,
                                    seriesList[0],
                                    seriesList[1]);
                            } else if (task == "msit") {
                                reader.ReadCSVThreadWrapper(
                                    "msit",  
                                    csvFilePath, 
                                    new ChartPanel[]{chart, chart2},
                                    blockNum,
                                    activeBlock,
                                    blockTR,
                                    seriesList[0], 
                                    seriesList[1], 
                                    seriesList[2], 
                                    seriesList[3],
                                    seriesList[4]);
                            } else if (task == "rifg") {
                                reader.ReadCSVThreadWrapper(
                                    "rifg", 
                                    csvFilePath,
                                    new ChartPanel[]{chart, chart2},
                                    blockNum,
                                    activeBlock,
                                    blockTR,
                                    seriesList[0], 
                                    seriesList[1], 
                                    seriesList[2], 
                                    seriesList[3],
                                    seriesList[4]);
                            } else {
                                System.out.println("No valid task was given for method: MakeGraphPanel()");
                                System.exit(0);
                            }
                            
                            optionHeader.setText("Reading from File: " + csvFilePath.getName());
                        } catch (Exception ex) {
                            optionHeader.setText("Error: " + ex.getMessage());
                        }
                    }
                };
                worker.execute();
            }
        });

        FileSystemGUI.createFileButton(selectFileButton, frame, csvFile -> {
            if ( csvFile != null ) {
                // get the csv file selected and show user
                System.out.println("Selected CSV File: " +  csvFile);
                File csvFilePath = new File(csvFile);
                optionHeader.setText("Reading from File: " + csvFilePath.getName());

                // delete the buttons for getting the csv
                waitForNewCSVButton.setVisible(false);
                selectFileButton.setVisible(false);

                // read the data from the csv file and update the series data
                CSVReader reader = new CSVReader(csvDir);
                if (task == "nfb") {
                    reader.ReadCSVThreadWrapper(
                        "nfb", 
                        csvFilePath, 
                        new ChartPanel[]{chart, chart2},
                        blockNum,
                        activeBlock,
                        blockTR,
                        seriesList[0],
                        seriesList[1]);
                } else if (task == "msit") {
                    reader.ReadCSVThreadWrapper(
                        "msit", 
                        csvFilePath, 
                        new ChartPanel[]{chart, chart2},
                        blockNum,
                        activeBlock,
                        blockTR,
                        seriesList[0], 
                        seriesList[1], 
                        seriesList[2], 
                        seriesList[3], 
                        seriesList[4]);
                } else if (task == "rifg") {
                    reader.ReadCSVThreadWrapper(
                        "rifg",
                        csvFilePath,
                        new ChartPanel[]{chart, chart2},
                        blockNum,
                        activeBlock,
                        blockTR,
                        seriesList[0], 
                        seriesList[1], 
                        seriesList[2], 
                        seriesList[3], 
                        seriesList[4]);
                } else {
                    System.out.println("No valid task was given for method: MakeGraphPanel()");
                    System.exit(0);
                }
                
            } else {
                System.out.println("No CSV File selected.");
            }

        });

        exitButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                System.out.println("Exiting Grapher Now.");
                frame.setVisible(false);
            }
        });
        
        // show whole frame
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
    }

    private static Object[] InitializeGraphVars(String task) {
        switch (task) {
            case "nfb":
                return new Object[] {
                    new XYSeries[]{new XYSeries("Score"), new XYSeries("Voxel Intensity")}, // Data Series(es)
                    new String[]{"Neurofeedback Score Graph", "ROI Activation Graph"}, // Graph Title 
                    System.getenv("NFB_SCORE_LOG_DIR"), // Score CSV Directory
                    new String[]{"TR"}, // X Axis Header
                    new String[] {"Neurofeedback Score", "Mean Voxel Intensity"}, // Y Axis Header
                    new int[][] {new int[]{0}, new int[]{1}}
                };
            case "rifg":
                return new Object[] {
                    new XYSeries[]{new XYSeries("Hits"), new XYSeries("Misses"), new XYSeries("Correct Rejections"), new XYSeries("False Alarms"), new XYSeries("Percent Correct")},
                    new String[]{"Task Trial Graph", "Percent Correct"},
                    System.getenv("RIFG_SCORE_LOG_DIR"),
                    new String[]{"TR"},
                    new String[]{"Percent of Trials", "Percent of Trials"},
                    new int[][] {new int[]{0, 1, 2, 3}, new int[]{4}}
                };
                
            case "msit":
                return new Object[]{ 
                    new XYSeries[]{new XYSeries("Correct"), new XYSeries("Incorrect"), new XYSeries("No Response"),new XYSeries("Invalid Response"), new XYSeries("Incorrect, Invalid, or No Response")},
                    new String[]{"Task Trial Graph", "Percent Incorrect, Invalid, or No Response"}, 
                    System.getenv("MSIT_SCORE_LOG_DIR"),
                    new String[]{"TR"},
                    new String[]{"Percent of Trials", "Percent of Trials"},
                    new int[][] {new int[]{0, 1, 2, 3}, new int[]{4}}
                };      
        }
        return null;
    }
    
    public ChartPanel MakeChart(
        String chartTitle,
        String xAxisHeader, 
        String yAxisHeader, 
        XYSeries[] seriesList, 
        int[] seriesNumsToUse,
        int chartPanelWidth, 
        int chartPanelHeight, 
        Font TextFont, 
        Font TitleFont,
        Color[] colors) {

        XYSeriesCollection dataset = new XYSeriesCollection(); // make empty dataset 

        for (int seriesNum : seriesNumsToUse) {
            dataset.addSeries(seriesList[seriesNum]);
        }

        // make graph chart 
        JFreeChart chart = ChartFactory.createXYLineChart(
            chartTitle, 
            xAxisHeader,
            yAxisHeader,
            dataset,
            PlotOrientation.VERTICAL,
            true,    // Show legend
            true,   // Tooltips
            false   // URLs
        );

        // add title 
        chart.setTitle(new TextTitle(chartTitle, TitleFont));

        // set graph fonts        
        XYPlot plot = chart.getXYPlot();
        plot.getDomainAxis().setLabelFont(TextFont); // X-axis label font
        plot.getDomainAxis().setTickLabelFont(TextFont); // X-axis tick label font
        plot.getRangeAxis().setLabelFont(TextFont); // Y-axis label font
        plot.getRangeAxis().setTickLabelFont(TextFont); // Y-axis tick label font
        chart.getLegend().setItemFont(TextFont);// Get the chart's legend and set the font

        // set size
        ChartPanel chartPanel = new ChartPanel(chart);
        chartPanel.setPreferredSize(new java.awt.Dimension(chartPanelWidth, chartPanelHeight));

        // Set line color and point size
        XYLineAndShapeRenderer renderer = new XYLineAndShapeRenderer();
        int seriesIndex = 0;
        for (@SuppressWarnings("unused") int seriesNum: seriesNumsToUse) {
            renderer.setSeriesPaint(seriesIndex, colors[seriesIndex]);
            renderer.setSeriesShape(seriesIndex, new Rectangle2D.Double(-1, -1, 2, 2)); // Small square (4x4 pixels)
            renderer.setSeriesShapesVisible(seriesIndex, true); // Enable shapes
            seriesIndex++;
        }
        
        plot.setRenderer(renderer);

        return chartPanel;
    }

    public Object[] getInformation(XYSeries series) {
        int itemCount = series.getItemCount();
        Number mostRecentTrial = series.getX(itemCount - 1);
        return new Object[]{mostRecentTrial};
    }

    public void updateDataPanel(
        Object[] componentsToUpdate,
        XYSeries[] seriesList,
        String task,
        AtomicInteger blockNum,
        AtomicInteger activeBlock,
        AtomicInteger blockTR) {
            
        JLabel dataPanelTrialTypeString = (JLabel) componentsToUpdate[0];
        JLabel dataPanelBlockString = (JLabel) componentsToUpdate[1];
        JLabel dataPanelTrialString = (JLabel) componentsToUpdate[2];
        JLabel dataPanelBlockTrialNumber = (JLabel) componentsToUpdate[3];


        Map<String, Set<String>> trialTypeOptions = new HashMap<>();

        Set<String> nfbOptions = new LinkedHashSet<>();
        nfbOptions.add("Rest");
        nfbOptions.add("Neurofeedback");

        Set<String> rifgOptions = new LinkedHashSet<>();
        rifgOptions.add("Rest");
        rifgOptions.add("Buzz");
        rifgOptions.add("Bear");
        
        Set<String> msitOptions = new LinkedHashSet<>();
        msitOptions.add("Rest");
        msitOptions.add("Control");
        msitOptions.add("Interference");
        
        trialTypeOptions.put("nfb", nfbOptions);
        trialTypeOptions.put("rifg", rifgOptions);
        trialTypeOptions.put("msit", msitOptions);
        
        new Thread( () -> {
            boolean waitingTextPrinted = false;

            while (true) {

                if (seriesList[0].getItemCount() > 0) {
                    // get trial types 
                    Set<String> options = trialTypeOptions.get(task);
                    List<String> optionList = new ArrayList<>(options);

                    // get trial number 
                    Object[] dataToAdd = getInformation(seriesList[0]);
                    int newTrialNumber = (int) Math.round((double) dataToAdd[0]);
                    
                    SwingUtilities.invokeLater(() -> {
                        String trialType = "None";
                        dataPanelTrialString.setText("Net Trial Number: " + newTrialNumber);
                        if (task != "rifg") {
                            dataPanelBlockString.setText("Block Number: " + blockNum.get());
                            dataPanelBlockTrialNumber.setText("Block-Specific Trial Number: " + blockTR);
                        } 
                        
                        // get trial type
                        if (activeBlock.get() == 0) {  
                            trialType = optionList.get(0); // Access the first element
                        } else if (activeBlock.get() == 1) {
                            trialType = optionList.get(1); 
                        } else if (activeBlock.get() == 2){
                            trialType = optionList.get(2); 
                        }
                        dataPanelTrialTypeString.setText("Trial Type: "  + trialType);
                    });

                } else {
                    if (waitingTextPrinted == false) {
                        System.out.println("Waiting for Data ...");
                        waitingTextPrinted = true;
                    }
                }

                try {
                    Thread.sleep(10);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }
}
