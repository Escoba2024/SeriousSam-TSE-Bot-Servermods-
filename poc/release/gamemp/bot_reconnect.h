/* SeriousSam TSE Bot Project: GameMP-only bot-client integration.
 * Modified 2026-10-08 through 2026-10-11; publication notice 2026-10-12.
 * Original captured source and published hashes: docs/reports/2026-10-12-source-verification.json.
 * GPL-2.0-only; existing upstream copyright notices are retained. */
#ifndef BOTCORE_RECONNECT_H
#define BOTCORE_RECONNECT_H

namespace botcore {

// Main-thread policy. Clock values are monotonic seconds, independent of the
// session tick that resets during JoinGame. Only a finished-map disconnect
// arms recovery; a failed join may subsequently leave gameOn false.
class Reconnect {
  bool pending_ = false;
  bool joining_ = false;
  bool internalStop_ = false;
  double due_ = 0;
  double delay_ = 2;
public:
  bool HasPending() const { return pending_; }
  void Reset() { pending_ = joining_ = internalStop_ = false; due_ = 0; delay_ = 2; }
  void OnStop() {
    if (joining_ && internalStop_) { internalStop_ = false; return; }
    Reset();
  }

  bool Poll(double now, bool enabled, bool gameOn, bool server,
            bool finished, bool disconnected, bool hasTarget) {
    if (!enabled || server || !hasTarget) { Reset(); return false; }
    if (joining_) return false;
    if (gameOn && !finished && !disconnected) { Reset(); return false; }
    if (!pending_ && gameOn && finished && disconnected) {
      pending_ = true;
      due_ = now + 2;
      delay_ = 2;
    }
    if (!pending_ || now < due_) return false;
    joining_ = true;
    internalStop_ = true;
    return true;
  }

  void OnResult(double now, bool success) {
    if (!joining_) return; // an explicit stop/user break canceled this attempt
    if (success) { Reset(); return; }
    joining_ = false;
    pending_ = true;
    delay_ = delay_ < 5 ? delay_ * 2 : 10;
    due_ = now + delay_;
  }
};

} // namespace botcore
#endif
