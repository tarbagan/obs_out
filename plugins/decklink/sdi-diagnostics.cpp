#include "sdi-diagnostics.hpp"
#include <sstream>

std::string GetSDIDiagnostics(DeckLinkDevice *device)
{
	if (!device) {
		return "Device unavailable. Check Desktop Video driver and refresh the device list.";
	}
	std::ostringstream report;
	report << "Device: " << device->GetDisplayName() << "\nModel: " << device->GetName()
	       << "\nPersistent identity: " << device->GetHash()
	       << "\nSubdevice index/count: " << device->GetSubDeviceIndex() << "/" << device->GetSubDeviceCount();
	ComPtr<IDeckLinkInput> input;
	ComPtr<IDeckLinkOutput> output;
	report << "\nCapture interface: " << (device->GetInput(&input) ? "available" : "unavailable")
	       << "\nPlayback interface: " << (device->GetOutput(&output) ? "available" : "unavailable")
	       << "\nSDI input: " << ((device->GetVideoInputConnections() & bmdVideoConnectionSDI) ? "yes" : "no")
	       << "\nSDI output: " << ((device->GetVideoOutputConnections() & bmdVideoConnectionSDI) ? "yes" : "no");
	ComPtr<IDeckLinkStatus> status;
	if (!device->GetStatus(&status)) {
		report << "\nSignal status: unavailable in this driver/device.";
		return report.str();
	}
	decklink_bool_t locked = false;
	report << "\nInput signal locked: ";
	if (status->GetFlag(bmdDeckLinkStatusVideoInputSignalLocked, &locked) == S_OK) {
		report << (locked ? "yes" : "no");
	} else {
		report << "unknown (not reported)";
	}
	int64_t value = 0;
	for (auto item : {bmdDeckLinkStatusDetectedVideoInputMode, bmdDeckLinkStatusCurrentVideoOutputMode}) {
		report << (item == bmdDeckLinkStatusDetectedVideoInputMode ? "\nDetected input mode: "
									   : "\nCurrent output mode: ");
		if (status->GetInt(item, &value) != S_OK) {
			report << "unknown (not reported)";
			continue;
		}
		ComPtr<IDeckLinkDisplayMode> mode;
		if (item == bmdDeckLinkStatusDetectedVideoInputMode && input) {
			input->GetDisplayMode(static_cast<BMDDisplayMode>(value), &mode);
		} else if (output) {
			output->GetDisplayMode(static_cast<BMDDisplayMode>(value), &mode);
		}
		if (mode) {
			decklink_string_t name;
			if (mode->GetName(&name) == S_OK) {
				std::string text;
				DeckLinkStringToStdString(name, text);
				report << text;
			} else {
				report << "ID 0x" << std::hex << value << std::dec;
			}
		} else {
			report << "ID 0x" << std::hex << value << std::dec;
		}
	}
	report << "\nReference locked: ";
	if (status->GetFlag(bmdDeckLinkStatusReferenceSignalLocked, &locked) == S_OK) {
		report << (locked ? "yes" : "no");
	} else {
		report << "unknown (not reported)";
	}
	report << "\nOutput status does not confirm cable continuity or receiver lock."
	       << "\nConnector masks describe connection types, not numbered physical BNC ports.";
	return report.str();
}
