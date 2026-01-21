#ifndef PRICE_H
#define PRICE_H
// Pricing object data recieved from IBKR api
class PRICE{
	public:
		int date, barCount;
		double open, high,low, close,vol,avg;

		PRICE();
		PRICE(int date, double open, double high, double low, double close, double vol , double avg, int barCount);

		int getDate() const;
		int getBarCount() const;
		double getOpen() const;
		double getHigh() const;
		double getLow() const;
		double getClose() const;
		double getVol() const;
		double getAvg() const;


};



#endif
