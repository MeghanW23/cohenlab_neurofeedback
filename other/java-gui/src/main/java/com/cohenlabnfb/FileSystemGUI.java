package com.cohenlabnfb;

import java.io.File;
import javax.swing.*;
import java.awt.Container;

public class FileSystemGUI {
    
    public static void createFileButton(String task, JButton openButton, Container container, FilePathCallback callback) {
        openButton.addActionListener(e -> {
            JFileChooser fileChooser = new JFileChooser();
            fileChooser.setDialogTitle("Please Choose a File");
            if (task == "neurofeedback") {
                fileChooser.setCurrentDirectory(NFBGraph.GetCsvPath());
            } else if (task == "rifg") {
                fileChooser.setCurrentDirectory(RIFGGraph.GetCsvPath());
            } else if (task == "msit") {
                fileChooser.setCurrentDirectory(MSITGraph.GetCsvPath());

            }
            
            int result = fileChooser.showOpenDialog(container);

            // If a file is selected
            if (result == JFileChooser.APPROVE_OPTION) {
                File selectedFile = fileChooser.getSelectedFile();
                if (!selectedFile.getName().contains(".csv") || !selectedFile.getName().contains("score")) {
                    JOptionPane.showMessageDialog(container, "Selected file" + selectedFile.getName() + " must to be a .csv file with the word 'score' in it");
                    callback.onFileSelected(null);
                    
                } else {
                    String filePath = selectedFile.getAbsolutePath();
                    JOptionPane.showMessageDialog(container, "You selected file: " + filePath);
                    callback.onFileSelected(filePath);  // Pass the selected file path to the callback
                }

            } else {
                JOptionPane.showMessageDialog(container, "No file selected.");
                callback.onFileSelected(null);  // Notify that no file was selected
            }
        });
    }

    // Interface for the callback
    public interface FilePathCallback {
        void onFileSelected(String filePath);
    }
}
