* A Cloud Orchestration Layer: Creating/Deleting/Quering and Scheduling Virtual Machines(VMs) in a given Network.

* Write the information of
    * the physical machines in: pm_file
    * the location of the VM image file in: image_file
    * flavors which can be evaluated in: flavor_file


* Run using the following command:
    *  ./bin/script.sh <pm_file><image_file><flavor_file>

* Scheduler Algorithm:
    * The scheduler looks for the next machine in line and if its ram and cpu limit satisfies the ram and cpu limit of the virtual machine to be created, it creates the VM in that machine.

* Technology Used : Flask, Libvirt
