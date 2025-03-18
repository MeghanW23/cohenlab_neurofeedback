package com.cohenlab;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.geom.Ellipse2D;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import javax.swing.BorderFactory;
import javax.swing.BoxLayout;
import javax.swing.JPanel;
import javax.swing.border.CompoundBorder;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.axis.ValueAxis;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYLineAndShapeRenderer;
import org.jfree.chart.title.TextTitle;
import org.jfree.chart.ui.RectangleEdge;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

public class GraphData {
    final private String task;

    public GraphData(String task) {
        this.task = task; 
    }
    
    public String[] parseCSVData(String csvLine) {
        String[] values = csvLine.split(",");

        for (int i = 0; i < values.length; i++) {
            if ("nan".equals(values[i])) {
                System.out.println("Changing Nan to 0.");
                values[i] = "0";
            }
        }

        return values;
    }

    public String[] getGraphInfo() {
        
         String xAxisName = "Trial"; 

        if ("RIFG".equals(this.task) || "MSIT".equals(this.task)) {
            String yAxisName = "Percent Correct";
            String[] singleGraphInfo = {"", xAxisName, yAxisName}; 
            return singleGraphInfo;
            

        } else if ("Neurofeedback".equals(this.task)) {
            String yAxisName = "";
            String[] singleGraphInfo = {"", xAxisName, yAxisName}; 
            return singleGraphInfo;
        }

        return null;
    }

    public XYSeriesCollection makeGraphDataset(List<String> startingCsvLines) {

        double condition1Trials = 0;
        double condition1Correct = 0;

        double condition2Trials = 0;
        double condition2Correct = 0;

        // get data from csv and HashMap index dictionary 
        XYSeriesCollection dataset = new XYSeriesCollection();
        Map<String, Map<String, Integer>> csvDataIndices = Constants.getColumnIndices();

        for (String seriesName : Constants.getSeriesNames().get(this.task)) {

            System.out.println("Iterating Through CSV Lines to Plot: " + seriesName);
            
            XYSeries dataSeries = new XYSeries(seriesName);
            
            if (startingCsvLines == null || startingCsvLines.isEmpty()) {
                System.out.println("No data to process.");
            } else {
                for (String csvString : startingCsvLines ) {
                
                
                    String[] csvDataList = parseCSVData(csvString);
    
                    // get trial number 
                    int trialIndex = csvDataIndices.get(this.task).get("totalTr");
                    int trialNumber = Integer.parseInt(csvDataList[trialIndex]);
                    
                    if (null != this.task) switch (this.task.trim()) {
                    case "Neurofeedback":
                        
                        if ("Brain Activation (AIU)".trim().equals(seriesName)) {
                           
                            int activatationResultIndex = csvDataIndices.get(this.task).get("result");
                            
                            double nfbResult = Double.parseDouble(csvDataList[activatationResultIndex]);
    
                            // number of columns (+1 to account for this new column )
                            dataSeries.add(trialNumber, nfbResult);
    
                        } else if ("Neurofeedback Score".trim().equals(seriesName)){
    
                            int scoreResultIndex = csvDataIndices.get(this.task).get("score");
    
                            double nfbScore = Double.parseDouble(csvDataList[scoreResultIndex]);
    
                            // number of columns (+1 to account for this new column )
                            dataSeries.add(trialNumber, nfbScore);
                        }
    
                        // break so it doesnt fall through
                        break;
    
                    case "MSIT":
                        int msitResultIndex = csvDataIndices.get(this.task).get("result");
                        String msitResult = csvDataList[msitResultIndex];
    
                        int msitConditionIndex = csvDataIndices.get(this.task).get("condition");
                        String msitCondition = csvDataList[msitConditionIndex];
    
                        if (("Control Trial").equals(seriesName)) {
                            
                            if ("333".trim().equals(msitCondition)) {
                                condition1Trials += 1;
    
                                if ("correct".trim().equals(msitResult)){
                                    condition1Correct += 1;
                                }
        
                                // get all control trials that are correct over all interference trials
                                double msitCondition1PercentCorrect = ((double) condition1Correct / condition1Trials) * 100;
                                
                                // number of columns (+1 to account for this new column )
                                dataSeries.add(trialNumber, msitCondition1PercentCorrect);
    
                            } 
                        } else if (("Interference Trial").equals(seriesName)) {
                            
                            if ("444".trim().equals(msitCondition)) {
                                condition2Trials += 1;
    
                                if ("correct".trim().equals(msitResult)){
                                    condition2Correct += 1;
                                }
    
                                // get all interference trials that are correct over all interference trials
                                double msitCondition2PercentCorrect = ((double) condition2Correct / condition2Trials) * 100;
    
                                // number of columns (+1 to account for this new column )
                                dataSeries.add(trialNumber, msitCondition2PercentCorrect);
                            }
                        } 
    
                        // break so it doesnt fall through
                        break;
                    
                    case "RIFG": 
                        int rifgResultIndex = csvDataIndices.get(this.task).get("result");
                        String rifgResult = csvDataList[rifgResultIndex];
    
                        int rifgConditionIndex = csvDataIndices.get(this.task).get("condition");
                        String rifgCondition = csvDataList[rifgConditionIndex];
    
                        if (("Bear Trial").equals(seriesName)) {
                            
                            if ("bear".equals(rifgCondition)) {
                                condition1Trials += 1;
    
                                if ("correct_rejection".equals(rifgResult)) {
                                    condition1Correct += 1;
                                }
                                // get all control trials that are correct over all interference trials
                                double rifgCondition1PercentCorrect = ((double) condition1Correct / condition1Trials) * 100;
                                
                                // number of columns (+1 to account for this new column )
                                dataSeries.add(trialNumber, rifgCondition1PercentCorrect);
    
                            }
    
                        } else if (("Buzz Trial").equals(seriesName)) {
                            
                            if ("buzz".equals(rifgCondition)) {
                                condition2Trials += 1;
    
                                if ("hit".equals(rifgResult)) { 
                                    condition2Correct += 1;
                                }
        
                                // get all control trials that are correct over all interference trials
                                double rifgCondition2PercentCorrect = ((double) condition2Correct / condition2Trials) * 100;
                                
                                // number of columns (+1 to account for this new column )
                                dataSeries.add(trialNumber, rifgCondition2PercentCorrect);
                            }
                        }
    
                        // break so it doesnt fall through
                        break;
    
                    default:
                        System.out.println("Unexpected task: " + this.task);
                        break;
                    }
                }

            }
            // add this iterations xyseries to the dataset 
            dataset.addSeries(dataSeries);            
            
        }
        
        return dataset;
    } 

    public ArrayList<Object> makeChart(XYSeriesCollection dataset,  Color[] lineColors) {
        ArrayList<Object> returnList = new ArrayList<>();

        // get title and axis info 
        String[] graphInfo =  getGraphInfo();
        String chartTitle = graphInfo[0];
        String xAxisLabel = graphInfo[1];
        String yAxisLabel = graphInfo[2];

        // make chart w/ axis info and dataset 
        JFreeChart chart = ChartFactory.createXYLineChart(
            chartTitle, 
            xAxisLabel, 
            yAxisLabel, 
            dataset,
            PlotOrientation.VERTICAL,
            true,  
            true,  
            false
            );


        returnList.add(chart);

        chart.getLegend().setBackgroundPaint(Constants.greyColor);
        chart.getLegend().setItemFont(Constants.chartLegendFont);
        chart.getLegend().setPosition(RectangleEdge.TOP);
        
        XYPlot plot = (XYPlot) chart.getPlot();

        XYSeries[] seriesArray = new XYSeries[dataset.getSeriesCount()];
        for (int i = 0; i < dataset.getSeriesCount(); i++) {
            seriesArray[i] = dataset.getSeries(i);
        }
        setAxesRanges(seriesArray, plot);
        returnList.add(plot);
        
        TextTitle title = chart.getTitle();
        title.setFont(Constants.chartTitleFont);
        
        // chart styling 
        XYLineAndShapeRenderer renderer = new XYLineAndShapeRenderer();
        for (int i = 0; i < dataset.getSeriesCount(); i++) {
            renderer.setSeriesPaint(i, lineColors[i]);
            renderer.setSeriesLinesVisible(i, true);
            renderer.setSeriesShapesVisible(i, !"Neurofeedback".equals(this.task));
            renderer.setSeriesShape(i, new Ellipse2D.Double(-2.5, -2.5, 5, 5)); // Custom shape size
            renderer.setSeriesOutlinePaint(i, Color.RED);
        }
        chart.setBackgroundPaint(Constants.greyColor);

        plot.setDomainPannable(true);
        plot.setRangePannable(true);
        plot.setRenderer(renderer);

        
        return returnList;
    }

    public JPanel makeGraphChartPanel(ArrayList<JFreeChart> charts) {
        
        // put chart on panel
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBackground(Constants.blueColor);
        
        for (JFreeChart chart : charts) {
            ChartPanel chartPanel = new ChartPanel(chart);
            chartPanel.setPreferredSize(new Dimension(
                Constants.getChartDimensions().get(this.task)[0], 
                Constants.getChartDimensions().get(this.task)[1]));
            chartPanel.setBackground(Constants.blueColor);
            chartPanel.setBorder(new CompoundBorder(
                BorderFactory.createEmptyBorder(5, 0, 5, 0),
                BorderFactory.createEtchedBorder()));
            panel.add(chartPanel);

        }
    
        return panel;

    }
    public void setAxesRanges(XYSeries[] seriesList, XYPlot plot) {
        // set axes ranges (+10 to make look better) and fonts 
        double[] axisRanges = getMinAndMaxOfXYSeriesCollection(seriesList);

        ValueAxis domainAxis = plot.getDomainAxis();
        domainAxis.setLabelFont(Constants.chartAxisFont);

        NumberAxis xAxis = (NumberAxis) domainAxis;
        xAxis.setRange(axisRanges[0] - 5, axisRanges[1] + 5);
        
        ValueAxis rangeAxis = plot.getRangeAxis();
        rangeAxis.setLabelFont(Constants.chartAxisFont);
        NumberAxis yAxis = (NumberAxis) rangeAxis;

        if ("Neurofeedback".equals(this.task)) {
            yAxis.setRange(axisRanges[2] - 0.1, axisRanges[3] + 0.1);

        } else {
            yAxis.setRange(axisRanges[2] - 5, axisRanges[3] + 5);

        }        
    }

    public double[] getMinAndMaxOfXYSeriesCollection(XYSeries[] seriesList) {
        double minX = Double.MAX_VALUE;
        double minY = Double.MAX_VALUE;

        double maxX = Double.MIN_VALUE;
        double maxY = Double.MIN_VALUE;

        boolean allEmptySeries = true;

        for (XYSeries series : seriesList) {
            
            if (series.isEmpty()) {
                continue;
            } 
            allEmptySeries = false;

            for (int j = 0; j < series.getItemCount(); j++) {
                double xValue = series.getX(j).doubleValue();
                double yValue = series.getY(j).doubleValue();
                    
                if (xValue < minX) {
                    minX = xValue;
                } 
                if (xValue > maxX) {
                    maxX = xValue;
                }
    
                if (yValue < minY) {
                    minY = yValue;
                } 
                
                if (yValue > maxY) {
                    maxY = yValue;
                }
    
            }

        }
        if (allEmptySeries) {
            System.out.println("All Empty Series - Getting Fake Axis Range");
            return new double[]{0, 10, 0, 100};
        } else {
            return new double[]{minX, maxX, minY, maxY};
        }
        
    }

    public void updateDataset(String csvLine, XYSeriesCollection dataset,  ArrayList<XYPlot> plotList) {
        if (csvLine.trim().isEmpty()){
            System.out.println("Skipping empty new line");
            return;
        }
        
        String[] csvList = parseCSVData(csvLine);

        // get trial number 
        Map<String, Map<String, Integer>> csvDataIndices = Constants.getColumnIndices();

        int trialIndex = csvDataIndices.get(this.task).get("totalTr");
        int trialNumber = Integer.parseInt(csvList[trialIndex]);
        

        if (null != this.task) {
            switch (this.task.trim()) {
                case "Neurofeedback":
                    int nfbScoreIndex = csvDataIndices.get(this.task).get("score");
                    Double nfbScore = Double.valueOf(csvList[nfbScoreIndex]);

                    int nfbActivationIndex = csvDataIndices.get(this.task).get("result");
                    Double nfbActivation =  Double.valueOf(csvList[nfbActivationIndex]);
                    
                    for (int i = 0; i < dataset.getSeriesCount(); i++) {
                        if (i == 0) {
                            dataset.getSeries(i).add(trialNumber, nfbScore);

                            NumberAxis yAxis = (NumberAxis) plotList.get(i).getRangeAxis();
                            yAxis.setRange(-1.1, 1.1);

                            NumberAxis xAxis = (NumberAxis) plotList.get(i).getDomainAxis();
                            xAxis.setRange(0, trialNumber + 5);

                        } else if (i == 1) {
                            dataset.getSeries(i).add(trialNumber, nfbActivation);

                            setAxesRanges(new XYSeries[] {dataset.getSeries(i)},  plotList.get(i));
                        }
                    }
                    
                    break;

                case "RIFG":
                case "MSIT":

                    int resultIndex = csvDataIndices.get(this.task).get("result");
                    String result = csvList[resultIndex];

                    // if it fits any of the msit or rifg correct results, add the current series
                    if (result.trim().equals("rest")){
                        System.out.println("Skipping rest");
                        break;
                    }
                    if (result.trim().isEmpty()){
                        System.out.println("Skipping empty result");
                        break;
                    }

                    int conditionIndex = csvDataIndices.get(this.task).get("condition");
                    String condition = csvList[conditionIndex];
                    
                    XYSeries currentSeries = getSeriesFromDataset(condition, dataset);

                    if (result.trim().equals("correct") || result.trim().equals("hit") ||  result.trim().equals("correct_rejection")) {
                        double currentPercentCorrect;
                        if (trialNumber == 1) {
                            currentPercentCorrect = 100;

                        } else {
                            currentPercentCorrect = getLastSeriesCoordinate(currentSeries)[1];

                            double totalCorrect = (currentPercentCorrect / 100) * (trialNumber - 1);
                            totalCorrect += 1;
                            
                            currentPercentCorrect = (totalCorrect / trialNumber) * 100;
                            
                        }
                        
                        currentSeries.add(trialNumber, currentPercentCorrect);
                        printEachElementInSeries(currentSeries);
                        
                    }  else {
                        double currentPercentCorrect;
                        if (trialNumber == 1) {
                            currentPercentCorrect = 0;
                        } else {
                            currentPercentCorrect = getLastSeriesCoordinate(currentSeries)[1];
                            double totalCorrect = (currentPercentCorrect / 100) * (trialNumber - 1);
                            currentPercentCorrect = (totalCorrect / trialNumber) * 100;
                        }
                        
                        printEachElementInSeries(currentSeries);
                        currentSeries.add(trialNumber, currentPercentCorrect);
                    }
                    setAxesRanges(new XYSeries[] {dataset.getSeries(0), dataset.getSeries(1)}, plotList.get(0));
                    break;

                default:
                    System.out.println("Task unrecognized: " + this.task);
                    break;
            }
           
        }
    }
    
    public XYSeries getSeriesFromDataset(String condition, XYSeriesCollection dataset) {
        
        if ("MSIT".equals(this.task)) {
            if ("444".equals(condition)) {
                condition = "interference";
            } 
            if ("333".equals(condition)) {
                condition = "control";
            }
        }

        for (int index = 0; index < Constants.getSeriesNames().get(this.task).length; index++) {
            if (Constants.getSeriesNames().get(this.task)[index].toLowerCase().contains(condition)) {
                XYSeries seriesToUse = dataset.getSeries(index);
                return seriesToUse;
            }
        }
        System.out.println("Could not find matching series");
        return null;
    }

    public void printEachElementInSeries(XYSeries series) {
        System.out.println("-------------");
        for (int i = 0; i < series.getItemCount(); i++) {
            double xValue = series.getX(i).doubleValue();
            double yValue = series.getY(i).doubleValue();
            System.out.println("Coordinate: (" + xValue + ", " + yValue + ")");
        }
    }

    public double[] getLastSeriesCoordinate(XYSeries series) {
        if (series.isEmpty()) {
            System.out.println("Series is empty, returning (0,0) as most recent coordinate");
            return new double[]{0, 0};
        }

        double xValue = series.getX(series.getItemCount() - 1).doubleValue();
        double yValue = series.getY(series.getItemCount() - 1).doubleValue();

        return new double[]{xValue, yValue};
    }
}

