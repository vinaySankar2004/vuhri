# Browsers

Which browser the agent uses for websites, and when it switches. How to behave on a
logged-in site is a personal preference and lives in `local/preferences/`.

## Built-in browser first

In the Claude desktop app, the Browser pane in a Code session is the default. It is
separate from the person's own browsers, so each site needs signing in there once. Use it
for reading, research, previews, and any signed-in site that works there.

## Claude in Chrome when the pane fails

Switch to [Claude in Chrome](https://claude.com/chrome) only when the built-in browser
cannot finish the task. Say which failure caused the switch, and go back to the pane for
the next task. Failures seen so far:

- **A passkey kept in the person's own browser or Apple Passwords.** The pane cannot reach
  it, and the sign-in ends with a message saying the passkey prompt was cancelled. Seen on an
  AWS root sign-in, 2026-10-08.

Add a failure to this list only when it has been seen, with its date.

Claude in Chrome is Anthropic's extension. It works in new tabs of the person's real Chrome,
with the sign-ins they already have there. Recent Chrome on macOS can use passkeys saved in
[iCloud Keychain](https://developer.chrome.com/blog/passkeys-on-icloud-keychain), now Apple
Passwords. The person sets it up once per computer: install it from the Chrome Web Store,
sign in with the same Claude account the app uses, and follow Anthropic's
[setup guide](https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome).
If no browser is connected, tell the person and ask them to check that Chrome is open with
the extension signed in. Do not retry in a loop.

## Either way

- Passwords, passkeys, and one-time codes are the person's to enter.
- Computer use can see a browser window but not click or type in it, so it is no substitute
  for either browser.
- Do not drive the person's browser through AppleScript or similar scripting. The reason is
  in `DECISIONS.md`.

Agents other than Claude Code follow the same order with their host's tools: an isolated
browser first, the person's own browser only when the isolated one fails.
