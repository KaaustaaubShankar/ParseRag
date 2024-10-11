package edu.uc.cs3003.medava;

public class Jarvik implements Shippable {

    //attributes
    private String serialNumber;
    //constructor
    Jarvik(String deviceSerialNumber) {
        serialNumber = deviceSerialNumber;
    }

    //getter
    public String getMedicineName() {
        return "Jarvik Artificial Heart";
    }

    //getter
    public MedicineSchedule getSchedule() {
        return MedicineSchedule.Uncontrolled;
    }

    //getter
    public String getSerialNumber() {
        return serialNumber;
    }
    //method to check temperature range
    public boolean isTemperatureRangeAcceptable(Double lowTemperature, Double highTemperature) {
        if (30.0 <= lowTemperature && highTemperature <= 90.0) {
            return true;
        }
        return false;
    }

    
}
