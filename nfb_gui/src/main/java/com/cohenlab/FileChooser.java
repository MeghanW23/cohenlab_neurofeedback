package com.cohenlab;

import java.io.File;

import javax.swing.JFileChooser;

public class FileChooser {
    public static String getFile(String csvParentDir) {
        JFileChooser fileChooser = new JFileChooser();

        File csvParentDirFile = new File(csvParentDir);
        
        if (csvParentDir != null) {
            if ( !csvParentDirFile.exists()) {
                throw new IllegalArgumentException("Inputted csvParentDir does not exist");
            } else {
                fileChooser.setCurrentDirectory(csvParentDirFile);
            
            }
        }


        String selectedFileString = null; 
        int returnVal = fileChooser.showOpenDialog(null);
        if (returnVal == JFileChooser.APPROVE_OPTION) { 
            File selectedFile = fileChooser.getSelectedFile();
            selectedFileString = selectedFile.toString();
            System.out.println("Selected file from Gui: " + selectedFile.getAbsolutePath());

        } else {
            System.out.println("File selection cancelled.");
        }
        
        return selectedFileString;

    }
}
