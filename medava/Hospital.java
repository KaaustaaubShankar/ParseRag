package edu.uc.cs3003.medava;

public class Hospital {
    //attribute
    private String name;

    //constructor
    public Hospital(String hospitalName) {
        name = hospitalName;
    }

    //method to recieve shipment
    void receive(Transporter t) {
        while (!t.isEmpty()) {
            Shippable unloaded = t.unload();
            System.out.println(String.format("Checking whether Hospital can receive %s.", unloaded.getMedicineName()));
            if (unloaded.getSchedule() != MedicineSchedule.Uncontrolled) {
                System.out.println(String.format("Hospital cannot receive controlled substances and %s is a %s.",
                        unloaded.getMedicineName(), unloaded.getSchedule().asString()));
            } else {
                System.out.println(String.format("Accepted a shipment of %s.", unloaded.getMedicineName()));
            }
        }
    }

    //getter
    public String name() {
        return name;
    }

    
}
