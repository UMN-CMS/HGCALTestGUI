#include "../include/EventListener.h"
#include <stdlib.h>

using namespace std;

EventListener::EventListener()
{
	this->toClose_ = false;
}

EventListener::~EventListener()
{
	Close();
}

void EventListener::Open()
{
	StatusID status;

	::Open(this, SCANNER_TYPE_ALL, &status);

	std::string inXML = 
		"<inArgs><cmdArgs><arg-int>1</arg-int><arg-int>1</arg-int></cmdArgs></inArgs>";
	std::string outXML = "";

	::ExecCommand(CMD_REGISTER_FOR_EVENTS, inXML, outXML, &status);

}

void EventListener::Close()
{
	StatusID status;
	::Close(0, &status);
}

void EventListener::GetScanners()
{
	unsigned short number;
	std::vector<unsigned int> scannerIDs;
	std::string outXML;
	StatusID status;

	std::cout << "Getting total number of scanners connected..." << std::endl;

	::GetScanners(&number, &scannerIDs, outXML, &status);

	std::cout << "Total number of scanners connected: " << number << std::endl;
       	std::cout << outXML << std::endl;	
}

void EventListener::OnBarcodeEvent( short eventType, std::string& pscanData )
{
	//std::cout << "Barcode Detected" << std::endl;
	//std::cout << "Out XML:" << std::endl;
	std::cout << pscanData << std::endl;
	toClose_ = true;
	std::cout << toClose_ << std::endl;
}

bool EventListener::GetToClose()
{
	return toClose_;
}

void EventListener::OnDisconnect()
{
	cout << "OnDisconnect" << endl;
}

void EventListener::OnImageEvent( short eventType, int size, short imageFormat,
		char* sfimageData, int dataLength, std::string& pScannerData )
{
	cout << "OnImageEvent" << endl;
}
void EventListener::OnVideoEvent( short eventType, int size, char* sfvideoData, int
		dataLength, std::string& pScannerData )
{
	cout << "OnVideoEvent" << endl;
}
void EventListener::OnPNPEvent( short eventType, std::string ppnpData )
{
}
void EventListener::OnCommandResponseEvent( short status, std::string& prspData )
{
	cout << endl << "Scanner data: " << prspData << endl;
	cout << "OnCommandResponseEvent" << endl;
	cout << prspData << endl;
}
void EventListener::OnScannerNotification( short notificationType, std::string&
		pScannerData )
{
	cout << endl << "Scanner event data: " << pScannerData << endl;
	cout << "OnScannerNotification" << endl;
}
void EventListener::OnIOEvent( short type, unsigned char data )
{
	cout << "OnIOEvent" << endl;
}
void EventListener::OnScanRMDEvent( short eventType, std::string& prmdData )
{
	cout << "OnScanRMDEvent" << endl;
	cout << "Out XML " << endl;
	cout << prmdData << endl;
}
void EventListener::OnBinaryDataEvent( short eventType, int size, short dataFormat, unsigned char* sfBinaryData, std::string& pScannerData)
{
}
