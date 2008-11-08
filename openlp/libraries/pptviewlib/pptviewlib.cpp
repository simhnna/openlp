/*
 *   PPTVIEWLIB - Control PowerPoint Viewer 2003/2007 (for openlp.org)
 *   Copyright (C) 2008 Jonathan Corwin
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */


#define WIN32_LEAN_AND_MEAN  
#include <windows.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include "pptviewlib.h"

// Because of the callbacks used by SetWindowsHookEx, the memory used needs to be
// sharable across processes (the callbacks are done from a different process)
// Therefore use data_seg with RWS memory.
//
// See http://msdn.microsoft.com/en-us/library/aa366551(VS.85).aspx for alternative
// method of holding memory, removing fixed limits which would allow dynamic number
// of items, rather than a fixed number. Use a Local\ mapping, since global has UAC 
// issues in Vista.
#pragma data_seg(".PPTVIEWLIB")
PPTVIEWOBJ pptviewobj[MAX_PPTOBJS] = {NULL};
HHOOK globalhook = NULL;
BOOL debug = FALSE;
#pragma data_seg()
#pragma comment(linker, "/SECTION:.PPTVIEWLIB,RWS")

#define DEBUG(...)  if(debug) printf(__VA_ARGS__)


HINSTANCE hInstance = NULL;

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
					 )
{
    hInstance = (HINSTANCE)hModule;
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
	case DLL_THREAD_ATTACH:
	case DLL_THREAD_DETACH:
		break;
	case DLL_PROCESS_DETACH:
		// Clean up... hopefully there is only the one process attached? 
		// We'll find out soon enough during tests!
		for(int i = 0; i<MAX_PPTOBJS; i++)
			ClosePPT(i);
		break;
	}
	return TRUE;
}
DllExport void SetDebug(BOOL onoff)
{
	printf("SetDebug");
	debug = onoff;
	DEBUG("enabled");
}

// Open the PointPoint, count the slides and take a snapshot of each slide
// for use in previews
// previewpath is a prefix for the location to put preview images of each slide.
// "<n>.bmp" will be appended to complete the path. E.g. "c:\temp\slide" would 
// create "c:\temp\slide1.bmp" slide2.bmp, slide3.bmp etc.
// It will also create a *info.txt containing information about the ppt
DllExport int OpenPPT(char *filename, HWND hParentWnd, RECT rect, char *previewpath)
{
	STARTUPINFO si;
	PROCESS_INFORMATION pi;
	char cmdline[MAX_PATH * 2];
	int id;

	DEBUG("OpenPPT start: %s\n", filename);
	if(GetPPTViewerPath(cmdline, sizeof(cmdline))==FALSE)
	{
		DEBUG("OpenPPT: GetPPTViewerPath failed\n");
		return -1;
	}
	id = -1;
	for(int i = 0; i<MAX_PPTOBJS; i++)
	{
		if(pptviewobj[id].state==PPT_CLOSED)
		{
			id=i;
			break;
		}
	}
	if(id<0)
	{
		DEBUG("OpenPPT: Too many PPTs\n");
		return -1;
	}
	memset(&pptviewobj[id], 0, sizeof(PPTVIEWOBJ));
	strcpy_s(pptviewobj[id].filename, MAX_PATH, filename);
	strcpy_s(pptviewobj[id].previewpath, MAX_PATH, previewpath);
	pptviewobj[id].state = PPT_CLOSED;
	pptviewobj[id].slideCount = 0;
	pptviewobj[id].currentSlide = 0;
	pptviewobj[id].firstSlideSteps = 0;
	pptviewobj[id].hParentWnd = hParentWnd;
	pptviewobj[id].hWnd = NULL;
	pptviewobj[id].hWnd2 = NULL;
	if(hParentWnd!=NULL&&rect.top==0&&rect.bottom==0&&rect.left==0&&rect.right==0)
	{
		LPRECT wndrect = NULL;
		GetWindowRect(hParentWnd, wndrect);
		pptviewobj[id].rect.top = 0;
		pptviewobj[id].rect.left = 0;
		pptviewobj[id].rect.bottom = wndrect->bottom-wndrect->top;
		pptviewobj[id].rect.right = wndrect->right-wndrect->left;
	}
	else
	{
		pptviewobj[id].rect.top = rect.top;
		pptviewobj[id].rect.left = rect.left;
		pptviewobj[id].rect.bottom = rect.bottom;
		pptviewobj[id].rect.right = rect.right;
	}
	strcat_s(cmdline, MAX_PATH * 2, "/S \"");
	strcat_s(cmdline, MAX_PATH * 2, filename);
	strcat_s(cmdline, MAX_PATH * 2, "\"");
	memset(&si, 0, sizeof(si));
	memset(&pi, 0, sizeof(pi));
	BOOL gotinfo = GetPPTInfo(id);
	if(!CreateProcess(NULL, cmdline, NULL, NULL, FALSE, 0, 0, NULL, &si, &pi))
	{
		DEBUG("OpenPPT: CreateProcess failed\n");
		ClosePPT(id);
		return -1;
	}

	pptviewobj[id].state = PPT_STARTED;
	pptviewobj[id].dwProcessId = pi.dwProcessId;
	pptviewobj[id].dwThreadId = pi.dwThreadId;
	pptviewobj[id].hThread = pi.hThread;
	pptviewobj[id].hProcess = pi.hProcess;
	/* 
	 * I'd really like to just hook on the new threadid. However this always gives
	 * error 87. Perhaps I'm hooking to soon? No idea... however can't wait
	 * since I need to ensure I pick up the WM_CREATE as this is the only
	 * time the window can be resized in such away the content scales correctly
	 *
	 * hook = SetWindowsHookEx(WH_CBT,CbtProc,hInstance,pi.dwThreadId);
	 */
	if(globalhook!=NULL)
		UnhookWindowsHookEx(globalhook);
	globalhook = SetWindowsHookEx(WH_CBT,CbtProc,hInstance,NULL);
	if(globalhook==0)
	{
		DEBUG("OpenPPT: SetWindowsHookEx failed\n");
		ClosePPT(id);
		return -1;
	}
	if(gotinfo)
		pptviewobj[id].state = PPT_LOADED;
	else
	{
		while(pptviewobj[id].state!=PPT_LOADED&&pptviewobj[id].state!=PPT_CLOSED)
		{
			NextStep(id);
			Sleep(100); // need to be careful not to be too quick, otherwise step to far and close show
		}
		SavePPTInfo(id);
		RestartShow(id);
	}
	//InvalidateRect(pptviewobj[id].hWnd, NULL, TRUE);
	DEBUG("OpenPPT: Exit: id=%i\n", id);
	return id;
}
// Load information about the ppt from an info.txt file.
// Format:
// filedate
// filesize
// slidecount
BOOL GetPPTInfo(int id)
{
	struct _stat filestats;
	char info[MAX_PATH];
	FILE* pFile;
	char buf[100];

	DEBUG("GetPPTInfo: start\n");
	if(_stat(pptviewobj[id].filename, &filestats)!=0)
		return FALSE;
	sprintf_s(info, MAX_PATH, "%sinfo.txt", pptviewobj[id].previewpath);
	int err = fopen_s(&pFile, info, "r");
	if(err!=0)
		return FALSE;
	fgets(buf, 100, pFile); 
	if(filestats.st_mtime!=atoi(buf))
	{
		fclose (pFile);
		return FALSE;
	}
	fgets(buf, 100, pFile);	
	if(filestats.st_size!=atoi(buf))
	{
		fclose (pFile);
		return FALSE;
	}
	fgets(buf, 100, pFile); // slidecount
	int slidecount = atoi(buf);
	// check all the preview images still exist
	for(int i = 1; i<=slidecount; i++)
	{
		sprintf_s(info, MAX_PATH, "%s%i.bmp", pptviewobj[id].previewpath, i);
		if(GetFileAttributes(info)==INVALID_FILE_ATTRIBUTES)
			return FALSE;
	}
	pptviewobj[id].slideCount = slidecount;
	DEBUG("GetPPTInfo: exit ok\n");
	return TRUE;
}

BOOL SavePPTInfo(int id)
{
	struct _stat filestats;
	char info[MAX_PATH];
	FILE* pFile;

	DEBUG("SavePPTInfo: start\n");
	if(_stat(pptviewobj[id].filename, &filestats)!=0)
	{
		DEBUG("SavePPTInfo: stat of %s failed\n", pptviewobj[id].filename);
		return FALSE;
	}
	sprintf_s(info, MAX_PATH, "%sinfo.txt", pptviewobj[id].previewpath);
	int err = fopen_s(&pFile, info, "w");
	if(err!=0)
	{
		DEBUG("SavePPTInfo: fopen of %s failed%i\n", info, err);
		return FALSE;
	}
	DEBUG("%u\n%u\n%u\n", filestats.st_mtime, filestats.st_size, pptviewobj[id].slideCount);
	fprintf(pFile, "%u\n%u\n%u\n", filestats.st_mtime, filestats.st_size, pptviewobj[id].slideCount);
	fclose (pFile);
	DEBUG("SavePPTInfo: exit ok\n");
	return TRUE;
}

// Get the path of the PowerPoint viewer from the registry
BOOL GetPPTViewerPath(char *pptviewerpath, int strsize)
{
	HKEY hkey;
	DWORD dwtype, dwsize;
	LRESULT lresult;

	DEBUG("GetPPTViewerPath: start\n");
	if(RegOpenKeyEx(HKEY_CLASSES_ROOT, "Applications\\PPTVIEW.EXE\\shell\\open\\command", 0, KEY_READ, &hkey)!=ERROR_SUCCESS)
		return FALSE;	
	dwtype = REG_SZ;
	dwsize = (DWORD)strsize;
	lresult = RegQueryValueEx(hkey, NULL, NULL, &dwtype, (LPBYTE)pptviewerpath, &dwsize );
	RegCloseKey(hkey);
	if(lresult!=ERROR_SUCCESS)
		return FALSE;
	pptviewerpath[strlen(pptviewerpath)-4] = '\0';	// remove "%1" from end of key value
	DEBUG("GetPPTViewerPath: exit ok\n");
	return TRUE;
}

// Unhook the Windows hook 
void Unhook(int id)
{
	DEBUG("Unhook: start\n");
	if(pptviewobj[id].hook!=NULL)	
		UnhookWindowsHookEx(pptviewobj[id].hook);
	pptviewobj[id].hook = NULL;
	DEBUG("Unhook: exit ok\n");
}

// Close the PowerPoint viewer, release resources
DllExport void ClosePPT(int id)
{
	DEBUG("ClosePPT: start\n");
	pptviewobj[id].state = PPT_CLOSED;
	Unhook(id);
	if(pptviewobj[id].hWnd==0)
		TerminateThread(pptviewobj[id].hWnd, 0);
	else
		PostMessage(pptviewobj[id].hWnd, WM_CLOSE, 0, 0);
	CloseHandle(pptviewobj[id].hThread);
	CloseHandle(pptviewobj[id].hProcess);
	memset(&pptviewobj[id], 0, sizeof(PPTVIEWOBJ));
	DEBUG("ClosePPT: exit ok\n");
	return;
}
// Moves the show back onto the display
DllExport void Resume(int id)
{
	DEBUG("Resume:\n");
	MoveWindow(pptviewobj[id].hWnd, pptviewobj[id].rect.left, pptviewobj[id].rect.top, 
			pptviewobj[id].rect.right - pptviewobj[id].rect.left, 
			pptviewobj[id].rect.bottom - pptviewobj[id].rect.top, TRUE);
	Unblank(id);								
}
// Moves the show off the screen so it can't be seen
DllExport void Stop(int id)
{
	DEBUG("Stop:\n");
	MoveWindow(pptviewobj[id].hWnd, -32000, -32000, 
			pptviewobj[id].rect.right - pptviewobj[id].rect.left, 
			pptviewobj[id].rect.bottom - pptviewobj[id].rect.top, TRUE);
}

// Return the total number of slides
DllExport int GetSlideCount(int id)
{
	DEBUG("GetSlideCount:\n");
	if(pptviewobj[id].state==0)
		return -1;
	else
		return pptviewobj[id].slideCount;
}

// Return the number of the slide currently viewing
DllExport int GetCurrentSlide(int id)
{
	DEBUG("GetCurrentSlide:\n");
	if(pptviewobj[id].state==0)
		return -1;
	else
		return pptviewobj[id].currentSlide;
}

// Take a step forwards through the show 
DllExport void NextStep(int id)
{
	DEBUG("NextStep:\n");
	PostMessage(pptviewobj[id].hWnd, WM_MOUSEWHEEL, MAKEWPARAM(0, -WHEEL_DELTA), 0);
}

// Take a step backwards through the show 
DllExport void PrevStep(int id)
{
	DEBUG("PrevStep:\n");
	PostMessage(pptviewobj[id].hWnd, WM_MOUSEWHEEL, MAKEWPARAM(0, WHEEL_DELTA), 0);
}

// Blank the show (black screen)
DllExport void Blank(int id)
{	
	// B just toggles blank on/off. However pressing any key unblanks.
	// So send random unmapped letter first (say 'A'), then we can 
	// better guarantee B will blank instead of trying to guess 
	// whether it was already blank or not.
	DEBUG("Blank:\n");
	HWND h1 = GetForegroundWindow();
	HWND h2 = GetFocus();
	SetForegroundWindow(pptviewobj[id].hWnd2);
	SetFocus(pptviewobj[id].hWnd2);
	keybd_event((int)'A', 0, 0, 0);
	keybd_event((int)'B', 0, 0, 0);
	SetForegroundWindow(h1);
	SetFocus(h2);
	//SendMessage(pptviewobj[id].hWnd2, WM_KEYDOWN, 'A', 0);
	//SendMessage(pptviewobj[id].hWnd2, WM_CHAR, 'A', 0);
	//SendMessage(pptviewobj[id].hWnd2, WM_KEYUP, 'A', 0);
	//SendMessage(pptviewobj[id].hWnd2, WM_KEYDOWN, 'B', 0);
	//SendMessage(pptviewobj[id].hWnd2, WM_CHAR, 'B', 0);
	//SendMessage(pptviewobj[id].hWnd2, WM_KEYUP, 'B', 0);
}
// Unblank the show 
DllExport void Unblank(int id)
{	
	DEBUG("Unblank:\n");
	// Pressing any key resumes.
	SendMessage(pptviewobj[id].hWnd2, WM_KEYDOWN, 'A', 0);
	SendMessage(pptviewobj[id].hWnd2, WM_CHAR, 'A', 0);
	SendMessage(pptviewobj[id].hWnd2, WM_KEYUP, 'A', 0);
//	HWND h1 = GetForegroundWindow();
//	HWND h2 = GetFocus();
//	SetForegroundWindow(pptviewobj[id].hWnd);
//	SetFocus(pptviewobj[id].hWnd);
//	keybd_event((int)'A', 0, 0, 0);
//	SetForegroundWindow(h1);
//	SetFocus(h2);
}

// Go directly to a slide
DllExport void GotoSlide(int id, int slideno)
{	
	DEBUG("GotoSlide %i:\n", slideno);
	// Did try WM_KEYDOWN/WM_CHAR/WM_KEYUP with SendMessage but didn't work
	// perhaps I was sending to the wrong window? No idea. 
	// Anyway fall back to keybd_event, which is OK as long we makesure
	// the slideshow has focus first
	char ch[10];

	if(slideno<0) return;
	_itoa_s(slideno, ch, 10, 10);
	HWND h1 = GetForegroundWindow();
	HWND h2 = GetFocus();
	SetForegroundWindow(pptviewobj[id].hWnd);
	SetFocus(pptviewobj[id].hWnd);
	for(int i=0;i<10;i++)
	{
		if(ch[i]=='\0') break;
		keybd_event((BYTE)ch[i], 0, 0, 0);
	}
	keybd_event(VK_RETURN, 0, 0, 0);
	SetForegroundWindow(h1);
	SetFocus(h2);

	//for(int i=0;i<10;i++)
	//{
	//	if(ch[i]=='\0') break;
	//	SendMessage(pptviewobj[id].hWnd2, WM_KEYDOWN, ch[i], 0);
	//	SendMessage(pptviewobj[id].hWnd2, WM_CHAR, ch[i], 0);
	//	SendMessage(pptviewobj[id].hWnd2, WM_KEYUP, ch[i], 0);
	//}
	//SendMessage(pptviewobj[id].hWnd2, WM_KEYDOWN, VK_RETURN, 0);
	//SendMessage(pptviewobj[id].hWnd2, WM_CHAR, VK_RETURN, 0);
	//SendMessage(pptviewobj[id].hWnd2, WM_KEYUP, VK_RETURN, 0);
	//keybd_event(VK_RETURN, 0, 0, 0);
}

// Restart the show from the beginning
DllExport void RestartShow(int id)
{
	// If we just go direct to slide one, then it remembers that all other slides have
	// been animated, so ends up just showing the completed slides of those slides that
	// have been animated next time we advance. 
	// Only way I've found to get around this is to step backwards all the way through. 
	// Lets move the window out of the way first so the audience doesn't see this.
	DEBUG("RestartShow:\n");
	Stop(id);
	GotoSlide(id, pptviewobj[id].slideCount);
	while(pptviewobj[id].currentSlide>1)
	{
		PrevStep(id);
		Sleep(10);
	}
	for(int i=0;i<=pptviewobj[id].firstSlideSteps;i++)
	{
		PrevStep(id);
	}
	Resume(id);
}

// This hook is started with the PPTVIEW.EXE process and waits for the
// WM_CREATEWND message. At this point (and only this point) can the
// window be resized to the correct size.
// Release the hook as soon as we're complete to free up resources
LRESULT CALLBACK CbtProc(int nCode, WPARAM wParam, LPARAM lParam)
{
	HHOOK hook = globalhook;
    if(nCode==HCBT_CREATEWND)
    {
	    char csClassName[16];
        HWND hCurrWnd = (HWND)wParam;
		DWORD retProcId = NULL;
		GetClassName(hCurrWnd, csClassName, sizeof(csClassName));
		if((strcmp(csClassName, "paneClassDC")==0)
		  ||(strcmp(csClassName, "screenClass")==0))
		{
			int id=-1;
			DWORD windowthread = GetWindowThreadProcessId(hCurrWnd,NULL);
			for(int i=0; i<MAX_PPTOBJS; i++)
			{
				if(pptviewobj[i].dwThreadId==windowthread)
				{
					id=i;
					break;
				}
			}
			if(id>=0)
			{
				if(strcmp(csClassName, "paneClassDC")==0)
					pptviewobj[id].hWnd2=hCurrWnd;
				else		
				{
					pptviewobj[id].hWnd=hCurrWnd;
					CBT_CREATEWND* cw = (CBT_CREATEWND*)lParam;
					if(pptviewobj[id].hParentWnd!=NULL) 
						cw->lpcs->hwndParent = pptviewobj[id].hParentWnd;
					cw->lpcs->cy=(pptviewobj[id].rect.bottom-pptviewobj[id].rect.top);
					cw->lpcs->cx=(pptviewobj[id].rect.right-pptviewobj[id].rect.left);
					cw->lpcs->y=-32000; 
					cw->lpcs->x=-32000; 
				}
				if((pptviewobj[id].hWnd!=NULL)&&(pptviewobj[id].hWnd2!=NULL))
				{
					UnhookWindowsHookEx(globalhook);
					globalhook=NULL;
					pptviewobj[id].state = PPT_OPENED;
					pptviewobj[id].hook = SetWindowsHookEx(WH_CALLWNDPROC,CwpProc,hInstance,pptviewobj[id].dwThreadId);
				}
			}
		}
    }
	return CallNextHookEx(hook,nCode,wParam,lParam); 
}

// This hook exists whilst the slideshow is running but only listens on the
// slideshows thread. It listens out for slide changes, message WM_USER+22.
LRESULT CALLBACK CwpProc(int nCode, WPARAM wParam, LPARAM lParam){
	CWPSTRUCT *cwp;
	cwp = (CWPSTRUCT *)lParam;
	HHOOK hook = NULL;
	char filename[MAX_PATH];

	DWORD windowthread = GetWindowThreadProcessId(cwp->hwnd,NULL);
	int id=-1;
	for(int i=0; i<MAX_PPTOBJS; i++)
	{
		if(pptviewobj[i].dwThreadId==windowthread)
		{
			id=i;
			hook = pptviewobj[id].hook;
			break;
		}
	}
	if((id>=0)&&(nCode==HC_ACTION))
	{
		if(cwp->message==WM_USER+22)
		{
			if((pptviewobj[id].state != PPT_LOADED)
				&& (pptviewobj[id].currentSlide>0)
				&& (pptviewobj[id].previewpath!=NULL&&strlen(pptviewobj[id].previewpath)>0))
			{
				sprintf_s(filename, MAX_PATH, "%s%i.bmp", pptviewobj[id].previewpath, pptviewobj[id].currentSlide);
				CaptureAndSaveWindow(cwp->hwnd, filename);
			}
			if(cwp->wParam==0)
			{
				if(pptviewobj[id].currentSlide>0) 
				{
					pptviewobj[id].state = PPT_LOADED;
					pptviewobj[id].currentSlide = pptviewobj[id].slideCount+1;
				}
			} 
			else
			{
				if((pptviewobj[id].state != PPT_LOADED)&&cwp->wParam==256)
					pptviewobj[id].firstSlideSteps++;
				pptviewobj[id].currentSlide = cwp->wParam - 255;
				if(pptviewobj[id].currentSlide>pptviewobj[id].slideCount)
					pptviewobj[id].slideCount = pptviewobj[id].currentSlide;
			}
		}
		if((pptviewobj[id].state != PPT_CLOSED)&&(cwp->message==WM_CLOSE||cwp->message==WM_QUIT))
			ClosePPT(id);
	}
	return CallNextHookEx(hook,nCode,wParam,lParam); 
}

VOID CaptureAndSaveWindow(HWND hWnd, CHAR* filename)
{
	HBITMAP hBmp;
	if ((hBmp = CaptureWindow(hWnd)) == NULL) 
		return;

	RECT client;
	GetClientRect (hWnd, &client);
	UINT uiBytesPerRow = 3 * client.right; // RGB takes 24 bits
	UINT uiRemainderForPadding;

	if ((uiRemainderForPadding = uiBytesPerRow % sizeof (DWORD)) > 0) 
		uiBytesPerRow += (sizeof (DWORD) - uiRemainderForPadding);

	UINT uiBytesPerAllRows = uiBytesPerRow * client.bottom;
	PBYTE pDataBits;

	if ((pDataBits = new BYTE [uiBytesPerAllRows]) != NULL) 
	{
		BITMAPINFOHEADER bmi = {0};
		BITMAPFILEHEADER bmf = {0};

		// Prepare to get the data out of HBITMAP:
		bmi.biSize = sizeof (bmi);
		bmi.biPlanes = 1;
		bmi.biBitCount = 24;
		bmi.biHeight = client.bottom;
		bmi.biWidth = client.right;

		// Get it:
		HDC hDC = GetDC (hWnd);
		GetDIBits (hDC, hBmp, 0, client.bottom, pDataBits, 
					(BITMAPINFO*) &bmi, DIB_RGB_COLORS);
		ReleaseDC (hWnd, hDC);

		// Fill the file header:
		bmf.bfOffBits = sizeof (bmf) + sizeof (bmi);
		bmf.bfSize = bmf.bfOffBits + uiBytesPerAllRows;
		bmf.bfType = 0x4D42;

		// Writing:
		FILE* pFile;
		int err = fopen_s(&pFile, filename, "wb");
		if (err == 0) 
		{
			fwrite (&bmf, sizeof (bmf), 1, pFile);
			fwrite (&bmi, sizeof (bmi), 1, pFile);
			fwrite (pDataBits, sizeof (BYTE), uiBytesPerAllRows, pFile);
			fclose (pFile);
		} 
		delete [] pDataBits;
	}
	DeleteObject (hBmp);
}
HBITMAP CaptureWindow (HWND hWnd) {
	HDC hDC;
	BOOL bOk = FALSE;
	HBITMAP hImage = NULL;

	hDC = GetDC (hWnd);
	RECT rcClient;
	GetClientRect (hWnd, &rcClient);
	if ((hImage = CreateCompatibleBitmap (hDC, rcClient.right, rcClient.bottom)) != NULL) 
	{
		HDC hMemDC;
		HBITMAP hDCBmp;

		if ((hMemDC = CreateCompatibleDC (hDC)) != NULL) 
		{
			hDCBmp = (HBITMAP) SelectObject (hMemDC, hImage);
			HMODULE hLib = LoadLibrary("User32");
			if(GetProcAddress(hLib, "PrintWindow")==NULL)
			{
				SetWindowPos(hWnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOSIZE); 
				BitBlt (hMemDC, 0, 0, rcClient.right, rcClient.bottom, hDC, 0, 0, SRCCOPY);
				SetWindowPos(hWnd, HWND_NOTOPMOST, -32000, -32000, 0, 0, SWP_NOSIZE); 
			}
			else
			{
				PrintWindow(hWnd, hMemDC, 0);
			}
			SelectObject (hMemDC, hDCBmp);
			DeleteDC (hMemDC);
			bOk = TRUE;
		}
	}
	ReleaseDC (hWnd, hDC);
	if (! bOk) 
	{
		if (hImage) 
		{
			DeleteObject (hImage);
			hImage = NULL;
		}
	}
	return hImage;
}
