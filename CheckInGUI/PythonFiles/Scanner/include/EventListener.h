#ifndef EVENTLISTENER_H_
#define EVENTLISTENER_H_

#include "zebra-scanner/CsIEventListenerXml.h"
#include "zebra-scanner/CsUserDefs.h"
#include "zebra-scanner/CsBarcodeTypes.h"
#include "zebra-scanner/Cslibcorescanner_xml.h"
#include <iostream>

class EventListener : public IEventListenerXml
{
	public:
		explicit EventListener();
		virtual ~EventListener();

		virtual void OnVideoEvent( short eventType,
			int size, char* sfvideoData,
			int dataLength,
			std::string& pScannerData
			);

		virtual void OnImageEvent( short eventType,
			int size, short imageFormat,
			char* sfimageData,
			int dataLength,
			std::string& pScannerData
			);

		virtual void OnBinaryDataEvent( short eventType, int size, short dataFormat,
				unsigned char* sfBinaryData, std::string& pScannerData);
		virtual void OnBarcodeEvent( short eventType, std::string& pscanData );
		virtual void OnPNPEvent( short eventType, std::string ppnpData );
		virtual void OnCommandResponseEvent( short status, std::string& prspData );
		virtual void OnScannerNotification( short notificationType, std::string& pScannerData);
		virtual void OnIOEvent( short type, unsigned char data );
		virtual void OnScanRMDEvent( short eventType, std::string& prmdData );
		virtual void OnDisconnect();

		void Open();
		void GetScanners();
		void Close();
		bool GetToClose();

	private:
		bool toClose_;
};

#endif 
