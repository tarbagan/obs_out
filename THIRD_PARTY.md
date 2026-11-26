# Third-party notices

The DeckLink source/output modules, frontend UI and translations are derived from
OBS Studio 32.2.2, commit fc546137470c0f4a5f1493b6e7815545ee1b170b.
Copyright OBS Project contributors. OBS code is GPL version 2 or later; see COPYING.
Local modifications add SDI validation, diagnostics and error handling.

The bundled Blackmagic DeckLink SDK interface files retain the Blackmagic Design
copyright and license notices in their file headers. Their terms apply independently.
FrameQueue retains Dmitry Vyukov's redistribution notice in decklink-device-instance.hpp.
Build-time OBS, Qt and multimedia dependencies retain their respective upstream licenses.
The package script ships plugin DLLs and plugin data only, not these runtime dependencies.
