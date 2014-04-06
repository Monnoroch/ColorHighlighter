#define WINVER 0x0500
#define _WIN32_WINNT 0x0500

#include <Windows.h>
#include <stdio.h>

CHOOSECOLOR cc;                 // common dialog box structure 
static COLORREF acrCustClr[16]; // array of custom colors 
HWND hwnd;                      // owner window
HBRUSH hbrush;                  // brush handle
static DWORD rgbCurrent;        // initial color selection

int main() {
	HWND consoleHwnd = GetConsoleWindow();
	ShowWindow( consoleHwnd, SW_HIDE );

	// Initialize CHOOSECOLOR 
	ZeroMemory(&cc, sizeof(cc));
	cc.lStructSize = sizeof(cc);
	cc.hwndOwner = consoleHwnd;
	cc.lpCustColors = (LPDWORD) acrCustClr;
	cc.rgbResult = rgbCurrent;
	cc.Flags = CC_FULLOPEN | CC_RGBINIT | CC_ANYCOLOR;
 
	if (ChooseColor(&cc)==TRUE) {
		hbrush = CreateSolidBrush(cc.rgbResult);
		rgbCurrent = cc.rgbResult;
		printf("#%06X", cc.rgbResult);
	} else {
		printf("CANCEL");
	}

	ShowWindow( consoleHwnd, SW_SHOW );
	return 0;
}