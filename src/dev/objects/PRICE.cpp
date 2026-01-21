#include "PRICE.h"
#include <iostream>

PRICE::PRICE(): date(0), open(0), high(0), low(0), close(0), vol(0), avg(0), barCount(0){}
PRICE::PRICE(int date, double open, double high, double low, double close, double vol, double avg, int barCount): date(date), open(open), high(high), low(low), close(close), vol(vol), avg(avg), barCount(barCount){}

int PRICE::getDate() const { return date; }
double PRICE::getOpen() const { return open; }
double PRICE::getHigh() const { return high; }
double PRICE::getLow() const { return low; }
double PRICE::getClose() const { return close; }
double PRICE::getVol() const { return vol; }
int PRICE::getBarCount() const { return barCount; }
double PRICE::getAvg() const { return avg; }

void PRICE::printPrice() const {
	std::cout << "Date: " << date 
			  << ", Open: " << open 
			  << ", High: " << high 
			  << ", Low: " << low 
			  << ", Close: " << close 
			  << '\n';
}

