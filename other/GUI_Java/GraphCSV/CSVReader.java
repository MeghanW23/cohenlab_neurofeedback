package GraphCSV;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.axis.ValueAxis;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import javax.swing.*;
import org.jfree.chart.plot.PlotOrientation;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;


public class CSVReader {
    private File filePath;
    private JFrame frame;
    private ChartPanel chartPanel;
    private XYSeries series1;

    public CSVReader(File filePath) {
        this.filePath = filePath;
        
        // Create a frame and chart panel initially
        series1 = new XYSeries("Block 1");        
        XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(series1);

        JFreeChart chart = ChartFactory.createXYLineChart(
            "Neurofeedback Score", // Title
            "X Axis",               // X Axis Label
            "Y Axis",               // Y Axis Label
            dataset,                // Dataset
            PlotOrientation.VERTICAL,
            true,                    // Show legend
            true,                    // Tooltips
            false                    // URLs
        );

        chartPanel = new ChartPanel(chart);
        chartPanel.setPreferredSize(new java.awt.Dimension(1000, 600));

        JButton end_button = new JButton("Exit");
        end_button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                System.out.println("Exit button clicked. Closing application.");
                System.exit(0);
            }
        });

        
        frame = new JFrame();
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        frame.setLayout(new GridBagLayout());
        GridBagConstraints gbcnfb = new GridBagConstraints();


        gbcnfb.gridx = 1; // Column 1
        gbcnfb.gridy = 1; // Row 1
        frame.add(chartPanel, gbcnfb);
        
        gbcnfb.gridx = 1; 
        gbcnfb.gridy = 2;
        frame.add(end_button, gbcnfb);
        frame.pack();
        frame.setVisible(true);


        System.out.println("Reading from CSV:" + filePath);
        Path path = Paths.get(filePath.getAbsolutePath());

        System.out.println("Checking for CSV File Existence ...");
        if (Files.exists(path)) {
            System.out.println("CSV File Exists.");
        } else {
            System.out.println("CSV File Does Not Exist.");
            System.exit(1);
        }


    }

    public Object[] ReadData() {
        String line;
        int line_count = 0;
        String x_axis_header = "No X Axis Header Found";
        String y_axis_header = "No Y Axis Header Found";
        ArrayList<String> coordinates = new ArrayList<>();        
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            while ((line = br.readLine()) != null) {
                // Skip empty lines
                if (line.trim().isEmpty() || line.trim().equals(",")) {
                    continue;
                }
                line_count = line_count + 1; /// Check if the line is a header via a line counter
                
                if (line_count == 1) {
                    String[] values = line.split(",");
                    if ( values.length != 2) {
                        continue; 
                    }
                    x_axis_header = values[0];
                    y_axis_header = values[1];
                } else {
                    if (line.contains("nan")) {
                        // Handle the "nan" case, e.g., log it or skip this coordinate
                        String[] values = line.split(",");
                        coordinates.add(values[0] + "," + "0");
                    } else {
                        coordinates.add(line); // Add valid data to the list
                    }
                   
                }
            }
        } catch (IOException e) {
            System.err.println("Error Reading CSV File: " + e.getMessage());
        }
        return new Object[] { x_axis_header, y_axis_header, coordinates};
    }

    public void GraphData(Object[] information_to_graph) {
        // Extracting data from the object array with proper casting
        String x_axis_header = (String) information_to_graph[0];
        String y_axis_header = (String) information_to_graph[1];

        ArrayList<String> coordinates = (ArrayList<String>) information_to_graph[2];
        String[] split_coords;
        XYSeries series1 = new XYSeries("Block 1");

        for (String coordinate : coordinates) {
            split_coords = coordinate.split(",");

            if (split_coords.length != 2) {
                System.err.println("Invalid coordinate format: " + coordinate);
                continue; // Skip invalid entries
            }

            double x = Double.parseDouble(split_coords[0].trim());
            double y = Double.parseDouble(split_coords[1].trim());
            series1.add(x, y); // create an XYSeries point to series1
        }
        
        XYSeriesCollection dataset = new XYSeriesCollection(); // add all series to the dataset 
        dataset.addSeries(series1);

        // Update chart title and axis labels
        JFreeChart chart = chartPanel.getChart();
        chart.setTitle("Neurofeedback Score");
        XYPlot plot = chart.getXYPlot();
        plot.getDomainAxis().setLabel(x_axis_header); // Update X-axis label
        plot.getRangeAxis().setLabel(y_axis_header); // Update Y-axis label
        plot.setDataset(dataset);

        // Ensure that the updated chart is refreshed
        chartPanel.repaint();

    }
}
