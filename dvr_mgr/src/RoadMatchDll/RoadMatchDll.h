// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the ROADMATCHDLL_EXPORTS
// symbol defined on the command line. this symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// ROADMATCHDLL_API functions as being imported from a DLL, whereas this DLL sees symbols
// defined with this macro as being exported.
#ifdef ROADMATCHDLL_EXPORTS
#define ROADMATCHDLL_API __declspec(dllexport)
#else
#define ROADMATCHDLL_API __declspec(dllimport)
#endif

// This class is exported from the RoadMatchDll.dll
class ROADMATCHDLL_API CRoadMatchDll {
public:
	CRoadMatchDll(void);
	// TODO: add your methods here.
};

extern ROADMATCHDLL_API int nRoadMatchDll;

ROADMATCHDLL_API int fnRoadMatchDll(void);
