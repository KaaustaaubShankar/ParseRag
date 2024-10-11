package edu.uc.cs3003.medava;

import java.util.ArrayList;

public class Transporter {
    private ArrayList<Shippable > goods;
    { goods = new ArrayList<Shippable >() {
        
    };}
    public Transporter(String transporterName, double lowTemp, double highTemp) {
        mTransporterName = transporterName;
        mLowTemperature = lowTemp;
        mHighTemperature = highTemp;
    }
    private String mTransporterName;

    public String getTransporterName() {
        return mTransporterName;
    }


    public void ship() {
        // Do some shipping!
    }

    private double mLowTemperature, mHighTemperature;
    
    
    public boolean load(Shippable itemToLoad) {
        if (itemToLoad.isTemperatureRangeAcceptable(mLowTemperature, mHighTemperature)) {
            return goods.add(itemToLoad);
        }
        return false;

    }
    public Shippable unload() {
        return goods.remove(0);
    }
    public boolean isEmpty() {
        return goods.isEmpty();
    }
}
