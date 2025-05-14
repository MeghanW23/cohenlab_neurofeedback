package com.cohenlab;
import java.awt.Color;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Image;
import java.awt.event.ActionEvent;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.swing.BorderFactory;
import javax.swing.ButtonGroup;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JRadioButton;
import javax.swing.border.EmptyBorder;

import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.IntervalMarker;
import org.jfree.chart.plot.XYPlot;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;



public class GUI {
    public void StartingWindow() {

        // Make frame 
        JFrame frame = new JFrame("ADHD Stimulant Project Graphical User Interface");

        frame.setSize(Constants.startingFrameWidth, Constants.startingFrameHeight);

        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        frame.setLayout(new FlowLayout());

        frame.getContentPane().setBackground(Constants.blueColor);

        // make panel 
        JPanel panel = new JPanel();

        panel.setPreferredSize(new Dimension(Constants.startingPanelWidth, Constants.startingPanelHeight));

        panel.setAlignmentX(JPanel.CENTER_ALIGNMENT);

        panel.setBorder(BorderFactory.createEtchedBorder());

        panel.setLayout(new FlowLayout(FlowLayout.CENTER, 20, 10));

        panel.setOpaque(true); 

        panel.setBackground(Constants.greyColor);

        frame.add(panel);

        // make title 
        JLabel title = new JLabel("Real-Time fMRI Task Tracker");

        title.setFont(Constants.startingTitleFont);
        
        title.setAlignmentX(JLabel.CENTER_ALIGNMENT);

        panel.add(title);

        // make logo 
        if (Files.notExists(Paths.get(Constants.logoPath))) {

            System.out.println("Could not find path to logo image: " + Constants.logoPath);

        }

        ImageIcon nfbLogoIcon = new ImageIcon(Constants.logoPath);

        Image nfbLogoImage = nfbLogoIcon.getImage();

        Image nfbScaledLogoImage = nfbLogoImage.getScaledInstance(
            Constants.logoWidth, 
            Constants.logoHeight, 
            Image.SCALE_SMOOTH);

        ImageIcon nfbScaledLogo = new ImageIcon(nfbScaledLogoImage);

        JLabel logoLabel = new JLabel(nfbScaledLogo);

        logoLabel.setAlignmentX(JPanel.CENTER_ALIGNMENT);

        panel.add(logoLabel);

        // make action buttons 
        String[] startingActionsList = {"Start", "Exit"};

        for (String action : startingActionsList) {

            JButton actionButton = new JButton(action); 

            actionButton.setAlignmentX(JPanel.CENTER_ALIGNMENT);

            actionButton.setFont(Constants.startingActionButtonFont);

            actionButton.setPreferredSize(new Dimension(
                Constants.actionButtonWidth, 
                Constants.actionButtonHeight));
            
            panel.add(actionButton);

            actionButton.addActionListener((ActionEvent e) -> {
                if ("Start".equals(action)){
                    // show options window and destroy this one
                    System.out.println("Starting GUI");
                    panel.setVisible(false);
                    OptionsWindow(frame);
                    
                } else if ("Exit".equals(action)) {
                    System.out.println("Exiting");
                    System.exit(0);
                }
            });
        }
        frame.setVisible(true);
    }
    
    public void OptionsWindow(JFrame frame) {

        // make task panel
        JPanel taskPanel = new JPanel();
        taskPanel.setBackground(Constants.greyColor);
        taskPanel.setLayout(new GridBagLayout());
        taskPanel.setPreferredSize(new Dimension(Constants.optionsPanelWidth, Constants.optionsPanelHeight));
        taskPanel.setBorder(BorderFactory.createEtchedBorder());
        GridBagConstraints c = new GridBagConstraints();
        c.gridx = 0;
        c.gridy = 0;
        frame.add(taskPanel);

        // make task label 
        c.gridy += 1;
        JLabel taskLabel = new JLabel("Please Select the Task of Interest");
        taskLabel.setFont(Constants.optionLabelButtonFont);
        taskLabel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        taskPanel.add(taskLabel, c);

        // make task buttons 
        ButtonGroup taskGroup = new ButtonGroup();
        String[] taskList = {"Neurofeedback", "RIFG", "MSIT"};
        Map<String, JRadioButton> taskButtons = new HashMap<>();
        for (String task : taskList) {
            c.gridy += 1;
            JRadioButton taskButton = new JRadioButton(task);
            taskButton.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
            taskButton.setBackground(Constants.greyColor);
            taskButton.setFont(Constants.optionButtonFont);
            taskPanel.add(taskButton, c);
            taskGroup.add(taskButton);
            taskButtons.put(task, taskButton);
        }       

        // make csv panel
        JPanel csvPanel = new JPanel();
        csvPanel.setBackground(Constants.greyColor);
        csvPanel.setLayout(new GridBagLayout());
        csvPanel.setPreferredSize(new Dimension(Constants.optionsPanelWidth, Constants.optionsPanelHeight));
        csvPanel.setBorder(BorderFactory.createEtchedBorder());
        frame.add(csvPanel);

        // make task label 
        c.gridy += 1;
        JLabel csvLabel = new JLabel("Please Select the CSV Aquisition Method");
        csvLabel.setFont(Constants.startingActionButtonFont);
        csvLabel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        csvPanel.add(csvLabel, c);

        // make csv buttons 
        ButtonGroup csvGroup = new ButtonGroup();
        String[] csvList = {"Wait for New CSV", "Select CSV", "Get Most Recent CSV"};
        Map<String, JRadioButton> csvButtons = new HashMap<>();
        for (String option : csvList) {
            c.gridy += 1;
            JRadioButton csvButton = new JRadioButton(option);
            csvButton.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
            csvButton.setBackground(Constants.greyColor);
            csvButton.setFont(Constants.optionButtonFont);
            csvPanel.add(csvButton, c);
            csvGroup.add(csvButton);
            csvButtons.put(option, csvButton);
        }      

        // make action buttons 
        String[] startingActionsList = {"Select", "Exit"};

        for (String action : startingActionsList) {

            JButton actionButton = new JButton(action); 

            actionButton.setAlignmentX(JPanel.CENTER_ALIGNMENT);

            actionButton.setFont(Constants.startingActionButtonFont);

            actionButton.setPreferredSize(new Dimension(
                Constants.actionOptionsButtonWidth, 
                Constants.actionOptionsButtonHeight));
            
                frame.add(actionButton);

            actionButton.addActionListener((ActionEvent e) -> {
                if ("Select".equals(action)){
                    // get selected info from the button presses
                    List<String> selectedInfo = onSelectedOptions(taskButtons, taskList, csvButtons, csvList);
                    
                    // get csv class instance from (csv option, task)
                    ReadCSV csvReader = getCSVFromOptions(selectedInfo.get(1), selectedInfo.get(0));
                    
                    // make main window
                    if (csvReader != null) {
                        frame.getContentPane().removeAll();
                        frame.revalidate();  // Revalidate the frame layout
                        frame.repaint();  // Repaint the frame to reflect the changes
                        
                        MainWindow(frame, selectedInfo.get(0), csvReader);
                    }
                    
                } else if ("Exit".equals(action)) {
                    System.out.println("Exiting");
                    App.newGuiSession(); 
                }
            });
        }
        frame.setVisible(true);
    }

    public List<String> onSelectedOptions(Map<String, JRadioButton> taskButtons, String[] taskList, Map<String, JRadioButton> csvButtons, String[] csvList) {
        List<String> selectedInfo = new ArrayList<>();
        
        for (String task : taskList) {
            JRadioButton button = taskButtons.get(task);
            if (button.isSelected()) {
                selectedInfo.add(task);
            }
        }

        for (String option : csvList) {
            JRadioButton button = csvButtons.get(option);
            if (button.isSelected()) {
                selectedInfo.add(option);
            }
        }

        if (selectedInfo.size() != 2) {
            // user didnt select both options 
            System.out.println("Please Select Both a Task and CSV Aquisition Method");
            return null;
        } 
        return selectedInfo;
    }

    public ReadCSV getCSVFromOptions(String optionsMethod, String task) {
        String csvDir = null;
        if (null != task) {
            switch (task) {
            case "Neurofeedback":
                csvDir = Constants.csvNfbDirScorePath;
                break;
            case "RIFG":
                csvDir = Constants.csvRifgDirScorePath;
                break;
            case "MSIT":
                csvDir = Constants.csvMsitDirScorePath;
                break;
            default:
                System.out.println("Invalid task specified: " + task);
                return null;
            }
        }

        // Check if csvDir was successfully assigned
        if (csvDir == null) {
            System.out.println("csvDir is null, cannot proceed.");
            return null;
        }
        
        ReadCSV csvReader = new ReadCSV(csvDir);
        if (null != optionsMethod) switch (optionsMethod) {
            case "Wait for New CSV":
                System.out.println("Waiting for New CSV");
                csvReader.OptToWaitForCsv();
                return csvReader;
            case "Get Most Recent CSV":
                System.out.println("Getting Most Recent CSV");

                // return only if a csv was found (and true was returned)
                if (csvReader.GetMostRecentCSV()) {
                    return csvReader;
                } else {
                    break;
                }
                
            case "Select CSV":
                String csvPath = FileChooser.getFile(csvDir);
                if (csvPath != null) {
                    csvReader.setCsvPath(csvPath);
                    return csvReader;
                } else {
                    return null;
                }
                

            default:
                return csvReader;
        }
        
        return null;
    }

    public void MainWindow(JFrame frame, String task, ReadCSV csvReader) {
        

        JPanel panelForTitle = new JPanel();
        panelForTitle.setBackground(Constants.greyColor);
        panelForTitle.setBorder(BorderFactory.createEtchedBorder());
        frame.add(panelForTitle);

        JLabel title = new JLabel(task + " Task");
        title.setFont(Constants.titleFont);
        title.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        panelForTitle.add(title);

        addExitButton(frame);

        JPanel panelForStatus = new JPanel();
        panelForStatus.setBackground(Constants.greyColor);
        panelForStatus.setBorder(BorderFactory.createEtchedBorder());
        frame.add(panelForStatus);

        JLabel status = new JLabel("Waiting for CSV File...");
        status.setFont(Constants.waitingStatusFont);
        status.setBorder(BorderFactory.createEmptyBorder(10, 25, 10, 25));
        panelForStatus.add(status);

        frame.setVisible(true);

        new Thread(() -> makeUpdatingElements(csvReader, task, frame, status)).start();
        
    }    
    
    public void makeUpdatingElements(ReadCSV csvReader, String task, JFrame frame, JLabel status) {
        IntervalMarker restMarker = new IntervalMarker(0, 0); 

        csvReader.StartWaitingForCSVIfOptedIn();

        csvReader.getCsvPath(false);

        List<String> csvData = csvReader.getAllCSVLines(true, task);

        GraphData grapher = new GraphData(task);

        XYSeriesCollection dataset = grapher.makeGraphDataset(csvData);

        // make two graphs (1 line per graph) for nfb
        ArrayList<XYPlot> plotList = new ArrayList<>();
        if ("Neurofeedback".equals(task)) {
            ArrayList<JFreeChart> charts = new ArrayList<>();
            ArrayList<Object> chartObjects;
            for (int i = 0; i < dataset.getSeriesCount(); i++) {

                XYSeriesCollection nfbDataset = new XYSeriesCollection();
                XYSeries series = dataset.getSeries(i);
                nfbDataset.addSeries(series);

                chartObjects = grapher.makeChart(nfbDataset, new Color[] {Constants.colorList[i]});
                charts.add((JFreeChart) chartObjects.get(0));
                plotList.add((XYPlot) chartObjects.get(1));

                List<List<Integer>> restBlocks = grapher.getRestBlocks(csvData);
                for (List<Integer> restBlock : restBlocks) {
                   restMarker = grapher.addRestMarkers((XYPlot) chartObjects.get(1), restBlock.get(0), restBlock.get(restBlock.size() - 1));
                   System.out.println(restMarker);
                }


            }
            JPanel chartPanel = grapher.makeGraphChartPanel(charts);
            

            frame.add(chartPanel);

        } else {
            // make one graph (2 lines on graph)
            ArrayList<Object> chartObjects = grapher.makeChart(dataset, Constants.colorList);

            JPanel chartPanel = grapher.makeGraphChartPanel(new ArrayList<>(Collections.singletonList((JFreeChart) chartObjects.get(0))));

            plotList.add((XYPlot) chartObjects.get(1));
            frame.add(chartPanel);
        }

        // update font
        String csvPath = csvReader.getCsvPath(true);
        Path path = Paths.get(csvPath);
        Path fileName = path.getFileName();
        status.setText("CSV File: " + fileName.toString());
        status.setFont(Constants.nonTitleFont);
        
        JPanel bottomPanel = new JPanel();
        bottomPanel.setBackground(Constants.blueColor);

        // add mri panel 
        StatisticsPanel statPanelInstance = new StatisticsPanel(task);
        JPanel[] statisticsPanels = statPanelInstance.makeStatisticsPanel();
        for (JPanel panel : statisticsPanels) {
            bottomPanel.add(panel);
        }

        // add to lefthand stat panel 
        // addExitButton(statisticsPanels[0]);

        frame.add(bottomPanel);

        frame.setVisible(true);
                
        String lastCsvLine = "";
        while (true) { 
            csvReader.waitForNewCsvData();

            String csvLine = csvReader.getCSVLine();

            if (csvLine != null && !csvLine.equals(lastCsvLine)) {
                System.out.println("CSV Line: " + csvLine);
                
                grapher.updateDataset(csvLine, dataset, plotList);

                if ("Neurofeedback".equals(task)) {
                    System.out.println("HERE 1");
                    List<Object> restData = grapher.ifRestTrial(csvLine);
                    
                    if ((boolean) restData.get(0)) {
                        System.out.println("HERE 2");
                        System.out.println(restMarker);
                        restMarker = grapher.updateRestMarkers(plotList, (int) restData.get(1), restMarker);
                    }
                }
                    
                lastCsvLine = csvLine;
            }

            
        }
            
    }        

    public void addExitButton(Container container) {
        // make action buttons 
        JButton exitButton = new JButton("Exit"); 
        exitButton.setAlignmentX(JPanel.CENTER_ALIGNMENT);
        exitButton.setFont(Constants.mainWindowButtonFont);
        exitButton.setPreferredSize(new Dimension(
            Constants.mainWindowButtonWidth, 
            Constants.mainWindowButtonHeight));

         // Wrap the button in a panel to further control placement if needed
        JPanel buttonPanel = new JPanel();
        buttonPanel.setBackground(Constants.blueColor);
        buttonPanel.setLayout(new FlowLayout(FlowLayout.CENTER));
        buttonPanel.setBorder(new EmptyBorder(10, 10, 10, 10)); // Additional padding around the panel
        buttonPanel.add(exitButton);

        container.add(buttonPanel);

        exitButton.addActionListener((ActionEvent e) -> {
            System.out.println("Exiting");
            App.newGuiSession();
        });
    }
}