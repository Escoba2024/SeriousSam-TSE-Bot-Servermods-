#include "bot_reconnect.h"
#include <cstdio>
#include <cstdlib>

static void check(bool value, const char *message) {
  if (!value) { std::fprintf(stderr, "FAIL: %s\n", message); std::exit(1); }
}

int main() {
  botcore::Reconnect retry;
  // The real JoinGame failure calls StopGame and leaves gameOn false.
  check(!retry.Poll(0, true, true, false, true, true, true), "wait for server restart");
  check(!retry.Poll(1, true, true, false, true, true, true), "no busy retry");
  check(retry.Poll(2, true, true, false, true, true, true), "first reconnect");
  retry.OnStop(); // JoinGame's internal StopGame must preserve the pending join.
  retry.OnResult(17, false);
  check(!retry.Poll(18, true, false, false, false, false, true), "backoff after failed join");
  check(retry.Poll(21, true, false, false, false, false, true), "retry survives gameOn false");
  retry.OnStop();
  retry.OnResult(22, true);
  check(!retry.Poll(40, true, true, false, false, false, true), "success does not reconnect healthy game");

  // A second map change must arm a fresh recovery, and manual stop cancels it.
  check(!retry.Poll(50, true, true, false, true, true, true), "second map arms recovery");
  retry.OnStop();
  check(!retry.Poll(100, true, false, false, false, false, true), "manual stop cancels recovery");

  // A disabled bot, server, missing target or ordinary disconnection must not join.
  check(!retry.Poll(110, false, true, false, true, true, true), "disabled bot unchanged");
  check(!retry.Poll(120, true, true, true, true, true, true), "server never joins itself");
  check(!retry.Poll(130, true, true, false, true, true, false), "no join address");
  check(!retry.Poll(140, true, true, false, false, true, true), "only finished-map disconnect arms recovery");

  // Several failures use capped delays, not a frame-by-frame storm.
  check(!retry.Poll(150, true, true, false, true, true, true), "arm repeated failure");
  check(retry.Poll(152, true, true, false, true, true, true), "attempt one");
  retry.OnResult(160, false);
  check(!retry.Poll(163, true, false, false, false, false, true), "four-second delay");
  check(retry.Poll(164, true, false, false, false, false, true), "attempt two");
  retry.OnResult(170, false);
  check(!retry.Poll(177, true, false, false, false, false, true), "eight-second delay");
  check(retry.Poll(178, true, false, false, false, false, true), "attempt three");
  retry.OnResult(180, false);
  check(!retry.Poll(189, true, false, false, false, false, true), "capped ten-second delay");
  check(retry.Poll(190, true, false, false, false, false, true), "attempt four");
  retry.OnResult(191, false);
  check(!retry.Poll(192, false, false, false, false, false, true), "disable clears pending retry");
  check(!retry.Poll(220, true, false, false, false, false, true), "reenable does not resurrect retry");
  check(!retry.Poll(230, true, true, false, true, true, true), "arm user-abort case");
  check(retry.Poll(232, true, true, false, true, true, true), "start user-abort attempt");
  retry.OnStop(); // internal StopGame
  retry.OnStop(); // subsequent explicit stop during the attempt
  retry.OnResult(240, false);
  check(!retry.Poll(260, true, false, false, false, false, true), "user-aborted join must not be retried");
  std::puts("BOT RECONNECT POLICY PASS");
}
