#include "manager.h"

/* Write your code here */
// const int MAX_DEVICES = 100;  // Maximum number of devices

// // Exception class for duplicate devices
// class DuplicateDevice : public std::exception {
//     const Device* device;  // Pointer to the device that caused the exception

// public:
//     // Constructor to initialize with the duplicate device
//     explicit DuplicateDevice(const Device* device)
//         : device(device) {}

//     // Override the what() method to return the error message
//     const char* what() const noexcept {
//         return "Duplicate device detected:";
//     }

//     // Additional method to print the device info
//     void print_device_info() const {
//         if (device) {
//             device->print_device();  // Directly call print_device() on the device
//         }
//     }
// };

// class Manager {
// private:
//     Device* devices[MAX_DEVICES];  // Fixed-size array to store pointers to devices
//     int device_count;              // Current count of devices

Manager:: Manager() {
        device_count = 0;
    }
void Manager::add_device(Device* device) {
    for (int i = 0; i<device_count; i++) {
        if(*devices[i] == *device) {
            throw DuplicateDevice(device);
        }
    }
    if (device_count < MAX_DEVICES){
        devices[device_count] = device;
        device_count++;
    }
}

bool Manager::compare_device(int index, const Device& other) const {
    return (*devices[index] == other);
}

Device* Manager::find_device(const Device& search_device) const {
    for (int i =0; i < device_count; i++) {
        if (*devices[i] == search_device) {
            return devices[i];
        }
    }
    return nullptr;
}

void Manager::delete_device(const Device& device) {
    int i;
    for (i =0; i<device_count; i++) {
        if (*devices[i] == device) {
            break;
        }
    }
    if (i<device_count) {
        delete devices[i];
        for (int j = i; j< device_count-1; j++) {
            devices[j] = devices[j+1];
        }
    }
    device_count--;
    devices[device_count] = nullptr;
}

void Manager::print_all_devices() const {
    for (int i = 0; i < device_count; i++) {
        if (devices[i] != nullptr) {
            devices[i] -> print_device();
        }
    }
}
Manager::~Manager() {
    for (int i = 0; i < device_count; i++) {
        delete devices[i];
        devices[i] = nullptr;
    }
}
