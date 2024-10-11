package edu.uc.cs3003.medava;
public class Ibuprofen extends Medicine {

    //constructor
    public Ibuprofen() {
        super("Ibuprofen");
    }
    //getter
    @Override
    public MedicineSchedule getSchedule() {
        return MedicineSchedule.Uncontrolled;
    }

    //allows us to override the default temperature range
    @Override
    public double minimumTemperature() {
        return 30.0;
    }
    //allows us to override the default temperature range
    @Override
    public double maximumTemperature() {
        return 90.0;
    }
}
