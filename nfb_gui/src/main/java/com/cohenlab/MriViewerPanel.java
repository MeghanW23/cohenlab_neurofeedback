package com.cohenlab;

import java.awt.Dimension;

import javax.swing.BorderFactory;
import javax.swing.JPanel;

public class MriViewerPanel {
    public static JPanel makeMriPanel(String task, JPanel outerPanel) {
        JPanel panel = new JPanel();
        panel.setPreferredSize(new Dimension(Constants.mriPanelWidth, Constants.mriPanelHeight));
        panel.setBackground(Constants.greyColor);
        panel.setBorder(BorderFactory.createEtchedBorder());
                
        return panel;
    }
}