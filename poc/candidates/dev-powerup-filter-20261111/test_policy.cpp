#include <cassert>
#include "DevPowerupPolicy.h"
int main() {
  for(int type=-2;type<=8;++type) {
    assert(DevRemovePowerup(true,true,false,true,type)==(type==0||type==2));
    assert(!DevRemovePowerup(false,true,false,true,type));
    assert(!DevRemovePowerup(true,false,false,true,type));
    assert(!DevRemovePowerup(true,true,true,true,type));
    assert(!DevRemovePowerup(true,true,false,false,type));
  }
}
