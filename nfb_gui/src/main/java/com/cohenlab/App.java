package com.cohenlab;

import javax.swing.UIManager;

public class App 
{
    @SuppressWarnings("UseSpecificCatch")
    public static void main( String[] args )
    {
        System.out.println( "Starting App" );  

        try {
            UIManager.setLookAndFeel(UIManager.getCrossPlatformLookAndFeelClassName());
        } catch (Exception e) {
            System.exit(1);
        }

        GUI gui = new GUI();
        gui.StartingWindow();
    
    }
}
