#define WINVER 0x0500
#define _WIN32_WINNT 0x0500

#include <Windows.h>
#include <stdio.h>


int main(int argc, char* argv[]) {
	HWND consoleHwnd = GetConsoleWindow();
	ShowWindow(consoleHwnd, SW_HIDE);

	DWORD rgbCurrent; // initial color selection
	if(argc < 2) {
		rgbCurrent = RGB(0, 0, 0);
	}
	else {
		int r, g, b, a;
		char * text;
		char tmp;

		text = argv[1] + 1;
		tmp = text[2];
		text[2] = '\0';
		sscanf_s(text, "%X", &r);
		text[2] = tmp;

		text = argv[1] + 3;
		tmp = text[2];
		text[2] = '\0';
		sscanf_s(text, "%X", &g);
		text[2] = tmp;

		text = argv[1] + 5;
		tmp = text[2];
		text[2] = '\0';
		sscanf_s(text, "%X", &b);
		text[2] = tmp;

		text = argv[1] + 7;
		tmp = text[2];
		sscanf_s(text, "%X", &a);

		rgbCurrent = RGB(r, g, b);
	}

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
		printf("#%02X%02X%02XFF", GetRValue(cc.rgbResult), GetGValue(cc.rgbResult), GetBValue(cc.rgbResult));
	else
		printf("CANCEL");

	ShowWindow( consoleHwnd, SW_SHOW );
	return 0;
}
