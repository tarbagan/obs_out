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

## FrameQueue redistribution notice

```text
Copyright (c) 2010-2011 Dmitry Vyukov. All rights reserved.
Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
   1. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
   2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY DMITRY VYUKOV "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
SHALL DMITRY VYUKOV OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of Dmitry Vyukov.
```
