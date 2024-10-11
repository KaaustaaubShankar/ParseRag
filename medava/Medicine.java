package edu.uc.cs3003.medava;

public abstract class Medicine implements Shippable {
    private String mMedicineName;

    //constructor
    public  Medicine(String medicineName) {
        mMedicineName = medicineName;
    }

    //getter
    public String getMedicineName() {
        return mMedicineName;
    }

    //method to check temperature range
    public boolean isTemperatureRangeAcceptable(Double lowTemperature, Double highTemperature) {
        if (this.minimumTemperature() <= lowTemperature && highTemperature <= this.maximumTemperature()) {
            return true;
        }
        return false;
    }

    
    public double minimumTemperature() {
        return 0.0;
    }

    public double maximumTemperature() {
        return 100.0;
    }    
    
    //abstract method that is implemented by child classes
    public abstract MedicineSchedule getSchedule();
}
