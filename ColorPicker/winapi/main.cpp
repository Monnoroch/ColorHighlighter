#define WINVER 0x0500
#define _WIN32_WINNT 0x0500

#include <Windows.h>
#include <stdio.h>


int main(int argc, char* argv[]) {
	HWND consoleHwnd = GetConsoleWindow();
	ShowWindow(consoleHwnd, SW_HIDE);

	unsigned r = 0, g = 0, b = 0, a = 0;
	if(argc > 1)
		sscanf_s(argv[1], "%02X%02X%02X%02X", &r, &g, &b, &a);

	COLORREF rgbCurrent = RGB((BYTE) r, (BYTE) g, (BYTE) b);

	// Initialize CHOOSECOLOR
	COLORREF acrCustClr[16] = {}; // array of custom colors 
	CHOOSECOLOR cc;
	ZeroMemory(&cc, sizeof(cc));
	cc.lStructSize = sizeof(cc);
	cc.hwndOwner = consoleHwnd;
	cc.lpCustColors = (LPDWORD) acrCustClr;
	cc.rgbResult = rgbCurrent;
	cc.Flags = CC_FULLOPEN | CC_RGBINIT | CC_ANYCOLOR;
 
	if(ChooseColor(&cc) == TRUE)
		printf("#%02X%02X%02X%s", GetRValue(cc.rgbResult), GetGValue(cc.rgbResult), GetBValue(cc.rgbResult), argc < 2 ? "FF" : argv[1] + 6);
	else
		printf("CANCEL");

	ShowWindow(consoleHwnd, SW_SHOW);
	return 0;
}
