#pragma once

#include "decklink-device.hpp"

// Snapshot only: status availability is driver/device dependent.
std::string GetSDIDiagnostics(DeckLinkDevice *device);
