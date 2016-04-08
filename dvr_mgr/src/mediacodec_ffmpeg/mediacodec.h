// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the MEDIACODEC_EXPORTS
// symbol defined on the command line. this symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// MEDIACODEC_API functions as being imported from a DLL, whereas this DLL sees symbols
// defined with this macro as being exported.
/*
#ifdef MEDIACODEC_EXPORTS
#define MEDIACODEC_API extern "C" __declspec(dllexport)
#else
#define MEDIACODEC_API __declspec(dllimport)
#endif
*/
/*
// This class is exported from the mediacodec.dll
class MEDIACODEC_API Cmediacodec {
public:
	Cmediacodec(void);
	// TODO: add your methods here.
};

extern MEDIACODEC_API int nmediacodec;

MEDIACODEC_API int fnmediacodec(void);
*/