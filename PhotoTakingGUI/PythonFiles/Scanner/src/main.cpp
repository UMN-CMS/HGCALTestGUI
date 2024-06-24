#include "../include/EventListener.h"
#include "../include/main.h"

#include <iostream>
#include <unistd.h>

int main(void)
{
	
	EventListener el;
	el.Open();

	//el.GetScanners();

	//std::cout << "Checking if you have a scanner plugged in..." << std::endl;

	//std::cout << "Please scan barcode or type 'q' to quit: " << std::endl;

	//std::cout << "<datalabel>33 32 30 35 39 39 39 39 39 39 30 30 30 30 31</datalabel>" << std::endl;

	while(!el.GetToClose())
	{
		//std::cout << "Still running..." << std::endl;
		//usleep(1000000);
	}

	return 0;
}
