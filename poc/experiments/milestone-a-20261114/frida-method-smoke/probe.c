#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
__attribute__((noinline,optimize("O0"),visibility("default"))) unsigned probe(unsigned x) {
  __asm__ volatile("" : "+r"(x));
  return x+1;
}
int main(void) {
  unsigned sum=0;
  struct timespec delay={0,10000000};
  for(unsigned i=0;i<300;i++){sum+=probe(i);nanosleep(&delay,0);}
  printf("%u\n",sum);
  return sum==45150?0:1;
}
