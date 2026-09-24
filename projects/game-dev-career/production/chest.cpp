#include <cassert>
#include <iostream>
#include <vector>

struct Chest {
    bool opened = false;
    int keys = 1;
    std::vector<int> inventory;
    const char* open() {
        if (opened) return "already_open";
        if (keys == 0) return "no_key";
        if (inventory.size() >= 4) return "bag_full";
        inventory.push_back(100);
        --keys;
        opened = true;
        return "reward_added";
    }
};
void record(const char* name, Chest chest) {
    const auto first = chest.open();
    const auto count = chest.inventory.size();
    const auto second = chest.open();
    assert(chest.inventory.size() == count); // Repeat input must not duplicate rewards.
    std::cout << "{\"case\":\"" << name << "\",\"first\":\"" << first
              << "\",\"second\":\"" << second << "\",\"opened\":" << (chest.opened?"true":"false")
              << ",\"keys\":" << chest.keys << ",\"items\":" << chest.inventory.size() << "}";
}
int main() {
    std::cout << "[";
    record("normal", Chest{});
    std::cout << ",";
    Chest no_key; no_key.keys=0; record("no_key", no_key);
    std::cout << ",";
    Chest full; full.inventory={1,2,3,4}; record("bag_full", full);
    std::cout << "]\n";
}
