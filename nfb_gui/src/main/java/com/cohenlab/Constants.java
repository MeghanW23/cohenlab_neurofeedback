package com.cohenlab;

import java.awt.Color;
import java.awt.Font;
import java.util.HashMap;
import java.util.Map;

public class Constants {

    // starting frame settings 
    static int startingFrameWidth = 800;
    static int startingFrameHeight = 850;
    static Color blueColor = new Color(173, 216, 230); // Light Blue 

    // starting panel 
    static int startingPanelWidth = 775;
    static int startingPanelHeight = 775;
    static Color greyColor = new Color(211, 211, 211); // Light Grey 

    // starting title 
    static Font startingTitleFont = new Font("Serif", Font.BOLD, 35);

    // starting logo 
    static String logoPath = System.getenv("GUI_NFB_LOGO");
    static int logoWidth = 650;
    static int logoHeight = 400;

    // starting action buttons 
    static Font startingActionButtonFont = new Font("Serif", Font.BOLD, 25);
    static int actionButtonWidth = 500;
    static int actionButtonHeight = 75; 

    // csv constants 
    static int[] nfbColumnsToPlot = {0, 1}; 

    static int[] rifgColumnsToPlot = {0, 1, 2};

    static int[] msitColumnsToPlot = {0, 1, 2, 3, 4}; // mean activation only

    // options panel 
    static int optionsPanelWidth = 775;
    static int optionsPanelHeight = 300;

    static Font optionLabelButtonFont = new Font("Serif", Font.BOLD, 25);
    static Font optionButtonFont = new Font("Serif", Font.PLAIN, 25);

    // options action buttons
    static int actionOptionsButtonWidth = 400; 
    static int actionOptionsButtonHeight = 60; 
    
    // sambashare Dir Path 
    static String sambashareDirPath = System.getenv("SAMBASHARE_DIR_PATH");

    // csv Dir Path
    static String csvNfbDirScorePath = System.getenv("NFB_SCORE_LOG_DIR");
    static String csvRifgDirScorePath = System.getenv("RIFG_SCORE_LOG_DIR");
    static String csvMsitDirScorePath = System.getenv("MSIT_SCORE_LOG_DIR");

    // mask dir path 
    static String maskDir = System.getenv("MASK_DIR");

    // log dir paths
    static String csvNfbDirLogPath = System.getenv("NFB_LOG_DIR");
    static String csvRifgDirLogPath = System.getenv("RIFG_LOG_DIR");
    static String csvMsitDirLogPath = System.getenv("MSIT_LOG_DIR");

    // main window
    static Font titleFont = new Font("Serif", Font.BOLD, 25);
    static Font nonTitleFont = new Font("Serif", Font.PLAIN, 15);
    static Font waitingStatusFont = new Font("Serif", Font.PLAIN, 35);

    static Font chartTitleFont = new Font("Serif", Font.BOLD, 20);
    static Font chartAxisFont = new Font("Serif", Font.PLAIN, 15);
    static Font chartLegendFont = new Font("Serif", Font.BOLD, 15);

    static Color[] colorList = {Color.DARK_GRAY, Color.BLUE};

    // main window button size
    static int mainWindowButtonWidth = 250; 
    static int mainWindowButtonHeight= 40; 
    static Font mainWindowButtonFont = new Font("Serif", Font.PLAIN, 20);

    // statistics panel 
    static int statPanelWidth = 400;
    static int statPanelHeight = 355;
    static Font statPanelTitleFont = new Font("Serif", Font.BOLD, 15);
    static Font statPanelNonTitleFont = new Font("Serif", Font.PLAIN, 13);

    // mri panel 
    static int mriPanelWidth = 365;
    static int mriPanelHeight = 355;

    static double mriMonitorWidth = Double.parseDouble(System.getenv("MRI_MONITOR_WIDTH"));
    static double mriMonitorHeight = Double.parseDouble(System.getenv("MRI_MONITOR_HEIGHT"));
    static double mriMonitorYOffset = Double.parseDouble(System.getenv("MRI_MONITOR_Y_OFFSET"));


    public static Map<String, int[]> getChartDimensions() { 
        Map<String, int[]> chartDimensions = new HashMap<>();
        chartDimensions.put("RIFG", new int[] {775, 350}); // width, height
        chartDimensions.put("MSIT", new int[] {775, 350});
        chartDimensions.put("Neurofeedback", new int[] {775, 175});

        return chartDimensions;
    }

    public static Map<String, String[]> getSeriesNames() {
        Map<String, String[]> seriesNames = new HashMap<>();
        seriesNames.put("Neurofeedback", new String[] { "Neurofeedback Score", "Brain Activation (AIU)"});
        seriesNames.put("RIFG", new String[] {"Bear Trial", "Buzz Trial"});
        seriesNames.put("MSIT", new String[] { "Control Trial", "Interference Trial"});

        return seriesNames;
    }
    
    public static Map<String, Map<String, Integer>> getColumnIndices() {
        Map<String, Map<String, Integer>> csvColumnIndices = new HashMap<>();

        Map<String, Integer> rifgCsvColumnIndices = new HashMap<>();
        rifgCsvColumnIndices.put("totalTr", 0);
        rifgCsvColumnIndices.put("result", 1);
        rifgCsvColumnIndices.put("condition", 2);
        csvColumnIndices.put("RIFG", rifgCsvColumnIndices);

        Map<String, Integer> msitCsvColumnIndices = new HashMap<>();
        msitCsvColumnIndices.put("totalTr", 0);
        msitCsvColumnIndices.put("result", 1);
        msitCsvColumnIndices.put("condition", 2);
        msitCsvColumnIndices.put("blockNum", 3);
        msitCsvColumnIndices.put("blockTrial", 3);
        csvColumnIndices.put("MSIT", msitCsvColumnIndices);

        Map<String, Integer> nfbCsvColumnIndices = new HashMap<>();
        nfbCsvColumnIndices.put("totalTr", 2);
        nfbCsvColumnIndices.put("score", 1);
        nfbCsvColumnIndices.put("blockNum", 3);
        nfbCsvColumnIndices.put("blockTrial", 0);
        nfbCsvColumnIndices.put("result", 4);
        csvColumnIndices.put("Neurofeedback", nfbCsvColumnIndices);

        return csvColumnIndices;
    }

}
