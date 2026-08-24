# Verification lanes

## Build integrity

- Tests and type checks pass.
- Production build succeeds.
- Required assets load.
- The browser console has no unexplained errors.
- The artifact does not rely on an undocumented network service.

## Interaction integrity

- Every control performs its stated action.
- Expected, incorrect, empty, boundary, and repeated-action paths behave safely.
- Reset and replay clear visible and hidden state.
- Random examples can be reproduced when debugging requires it.
- The learner cannot enter an impossible or misleading state.

## Visual and accessibility integrity

- Check wide and narrow viewports.
- Confirm text, controls, labels, and important state are not clipped.
- Test keyboard navigation and visible focus.
- Do not use color as the only state signal.
- Respect reduced motion.
- Keep contrast and text size readable.

## Instructional integrity

- Displayed facts, calculations, transitions, and feedback are correct.
- The learner performs the action named in the brief.
- Answers are not revealed before the intended attempt.
- Feedback distinguishes the targeted misconception.
- Decorative detail does not compete with the explanation.
- Completion means something connected to the learning objective.
- The artifact labels important simplifications and sources.

