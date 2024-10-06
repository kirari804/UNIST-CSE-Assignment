#include "device.h"
using namespace std;
#include <iostream>



/* Write your code here */
// class Device {
// protected:
//     int device_id;
//     std::string device_type;
//     std::string brand;

// public:
Device::Device(int id, const std::string& type, const std::string& brand):
    device_id(id), device_type(type), brand(brand) { }

Device:: ~Device() {
    // cout << device_type << " [ID: " << device_id << ", " << "Brand: " << brand;
}
void Device::print_device() const {
    cout << device_type << " [ID: " << device_id << ", " << "Brand: " << brand;

}
bool Device::operator==(const Device& other) const {
    return device_id == other.device_id 
    && device_type == other.device_type
        && brand == other.brand;
}
bool Device::operator<(const Device& other) const {
    return device_id < other.device_id;
}
bool Device::operator>(const Device& other) const {
    return device_id > other.device_id;
}
bool Device::operator<=(const Device& other) const {
    return device_id <= other.device_id;
}
bool Device::operator>=(const Device& other) const {
    return device_id >= other.device_id;
}  


// class Phone : public Device {
// private:
//     int data_usage; // Mobile data usage in GB

// public:
Phone::Phone(int id, const std::string& brand, int data_usage):
    Device(id, "Phone", brand), data_usage(data_usage) {}
Phone::~Phone() {
    // Device::print_device();
    // cout << ", " << "Data Usage: " << data_usage << "]"<<endl;
}
void Phone::print_device() const {
    Device::print_device();
    cout << ", " << "Data Usage: " << data_usage << "]"<<endl;
}
bool Phone::operator<(const Phone& other) const {
    return device_id < other.device_id
        && data_usage < other.data_usage;
}
bool Phone::operator>(const Phone& other) const {
    return device_id > other.device_id
        && data_usage > other.data_usage;
}
bool Phone::operator<=(const Phone& other) const {
    return device_id <= other.device_id
        &&  data_usage <= other.data_usage;
}
bool Phone::operator>=(const Phone& other) const {
    return device_id >= other.device_id
        && data_usage >= other.data_usage;
}

// class Watch : public Device {
// private:
//     int step_count; // Step counter function

// public:
Watch::Watch(int id, const std::string& brand, int step_count): 
    Device(id, "Watch",  brand), step_count(step_count) {}
Watch::~Watch() {
    // Device::print_device();
    // cout << ", " << "Step Count: " << step_count << "]"<<endl;
}
void Watch::print_device() const {
    Device::print_device();
    cout << ", " << "Step Count: " << step_count << "]"<<endl;
}
bool Watch::operator<(const Watch& other) const {
    return device_id < other.device_id
        && step_count < other.step_count;
}
bool Watch::operator>(const Watch& other) const {
    return device_id > other.device_id
        && step_count > other.step_count;
}
bool Watch::operator<=(const Watch& other) const {
    return device_id <= other.device_id
        && step_count <= other.step_count;
}
bool Watch::operator>=(const Watch& other) const {
    return device_id >= other.device_id
        && step_count >= other.step_count;
}


// class Ring : public Device {
// private:
//     bool sleep_tracking ;  // Sleep quality measurement

// public:
Ring::Ring(int id, const std::string& brand, bool sleep_tracking):
    Device(id, "Ring", brand), sleep_tracking(sleep_tracking) {}
Ring::~Ring() {
    // cout << device_type << " [ID: " << device_id << "Brand: " << brand;
    // if (sleep_tracking) {
    //     cout << " Sleep Tracking: Enabled]" << endl;
    //     }
    // else {
    //     cout << " Sleep Tracking: Disabled]" << endl;
    //     }
    }
void Ring::print_device() const {
    Device::print_device();
    if (sleep_tracking) {
        cout << ", " <<"Sleep Tracking: Enabled] "<< endl;
    }
    else {
        cout << ", " <<"Sleep Tracking: Disabled] "<< endl;
    }
}
bool Ring::operator<(const Ring& other) const {
    return device_id < other.device_id;
}
bool Ring::operator>(const Ring& other) const {
    return device_id > other.device_id;
}
bool Ring::operator<=(const Ring& other) const {
    return device_id <= other.device_id;
}
bool Ring::operator>=(const Ring& other) const {
    return device_id >= other.device_id;
}  

// class Earbud : public Device {
// private:
//     bool noise_cancellation;  // Whether the earbuds have noise cancellation

// public:
Earbud::Earbud(int id, const std::string& brand, bool noise_cancel):
    Device(id, "Earbud", brand), noise_cancellation(noise_cancel) {}
Earbud::~Earbud() {
    // cout << device_type << " [ID: " << device_id << "Brand: " << brand ;
    // if (noise_cancellation) {
    //     cout << " Noise Cancellation: Enabled]" << endl;
    // }
    // else {
    //     cout << " Noise Cancellation: Disabled]" << endl;
    // }        
}
void Earbud::print_device() const {
    Device::print_device();
    if (noise_cancellation) {
        cout << ", " << "Noise Cancellation:  Enabled]" << endl;
    }
    else {
        cout << ", " << "Noise Cancellation:  Disabled]" << endl;
    }        
}
bool Earbud::operator<(const Earbud& other) const {
    return device_id < other.device_id;
}
bool Earbud::operator>(const Earbud& other) const {
    return device_id > other.device_id;
}
bool Earbud::operator<=(const Earbud& other) const {
    return device_id <= other.device_id;
}
bool Earbud::operator>=(const Earbud& other) const {
    return device_id >= other.device_id;
}




