#include <mlpack.hpp>
#include <mlpack/core/util/version.hpp>

using namespace std;
int main(){
 // printing version of mlpack and returing it as a string
 
	cout << "mlpack version: " << mlpack::util::GetVersion() << "\n";
	return 0;

}
	
