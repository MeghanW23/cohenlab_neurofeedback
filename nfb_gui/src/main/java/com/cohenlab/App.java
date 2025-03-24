package com.cohenlab;

import javax.swing.UIManager;
import javax.swing.UnsupportedLookAndFeelException;

public class App 
{
    public static void main( String[] args )
    {
        System.out.println( "Starting App" );  

        try {
            UIManager.setLookAndFeel(UIManager.getCrossPlatformLookAndFeelClassName());
        } catch (ClassNotFoundException | IllegalAccessException | InstantiationException | UnsupportedLookAndFeelException e) {
            System.out.println(e);
            System.exit(1);
        }

        App.newGuiSession();
    }

    public static void newGuiSession() {
        GUI gui = new GUI();
        gui.StartingWindow();
    }
}
