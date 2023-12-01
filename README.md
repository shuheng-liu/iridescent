# Viris – Vim meets IRIS

## Supported Vim Modes

Currently, there are 3 modes supported

- Insert
- Normal
- Replace

## Supported Vim Commands in *Normal* Mode

In *Normal* mode, viris supports a variety of canonical vim commands.
These key bindings should feel natural to experienced vim users.
If you haven't used vim before, learn about [`vimtutor`](https://vimschool.netlify.app/introduction/vimtutor/) first.

- Navigation
    - `h`, `l`, `<LEFT>`, `<RIGHT>`: Move cursor left and right.
    - `j`, `k`, `<UP>`, `<DOWN>`: Navigate through history. This is because we only support one-line editing currently.
    - `G`: Go to the line that was recently edited but not sent. This happens because the user navigated into history
      before hitting enter.
    - `w`, `W`: Navigate to the next beginning-of-word. Capital `W` treats consecutive non-whitespace characters as a
      single word.
    - `e`, `E`: Navigate to the next end-of-word. Capital `E` treats consecutive non-whitespace characters as a single
      word.
    - `b`, `B`: Navigate to the previous beginning-of-word. Capital `B` treats consecutive non-whitespace characters as
      a single word.
    - `0`: Navigate to the beginning of line.
    - `$`: Navigate to the end of line.
    - `f<char>`: Navigate to the next occurrence of `<char>` (TODO)
    - `F<char>`: Navigate to the previous occurrence of `<char>` (TODO)
- Deletion:
    - `dw`/`dW`: Delete until the next beginning-of-word (to be fixed).
    - `de`/`dE`: Delete until the next end-of-word (to be fixed).
    - `db`/`dB`: Delete until the previous beginning-of-word (to be fixed).
    - `dd`: Delete all characters on the current line.
    - `d0`: Delete until beginning of the line.
    - `d$`: Delete until end of the line.
    - `dt<char>`: Delete until the next occurrence of `<char>`.
    - `di<char>`: Delete everything within the enclosing pair of
        - parentheses `(...)`: if `<char>` is either `(` or `)`
        - square brackets `[...]`: if `<char>` is either `[` or `]`
        - curly braces `{...}`: if `<char>` is either `[` or `]`
        - angle brackets `<...>`: if `<char>` is either `<` or `>`
        - backticks <code>&#96;...&#96;</code>: if `<char>` is backtick <code>`</code>
        - single quotes `'...'`: if `<char>` is single quote `'`
        - double quotes `"..."`: if `<char>` is double quote `"`
        - commas `,...,` if `<char>` is comma `,` (standard Vim doesn't support this)
        - spaces ` ... ` if `<char>` is space ` ` (standard Vim doesn't support this)
    - `x`: Delete the character under cursor
- Change:
    - The change commands are almost identical to the delete commands listed above.
      The difference is that a change command will exit *Normal* mode and enter *Insert* mode after deleting characters.
    - The keystrokes for a change command is obtained by changing the leading `d` to `c`.
        - `cw`, `cW`, `ce`, `cE`, `cb`, `cB`, `c0`, `c$`, `ct<char>`, `ci<char>`
    - Special cases are:
        - `cc`: Delete the current line and set to insert mode.
        - `s`: Delete the character under cursor and set to insert mode.
- Copy/Paste:
    - A text segment is automatically copied to the internal clipboard once it's deleted by a *Delete* or *Change*
      command.
    - You can optionally copy something without deleting them with the yank commands: (to be implemented)
      `yw`, `yW`, `ye`, `yE`, `yb`, `yB`, `yy`, `y0`, `y$`, `yt<yhar>`, `yi<yhar>`
    - To paste the content of the clipboard use `p` (paste to the right of the current block-shaped cursor) or `P` (
      paste to the left of the current block-shaped cursor)
- Switch between modes:
    - `i`: Exit *Normal* mode and enter *Insert* mode, moving the cursor (vertical bar) to the left the original
      cursor (block-shaped).
    - `a`: Exit *Normal* mode and enter *Insert* mode, moving the cursor (vertical bar) to the right the original
      cursor (block-shaped).
    - `I`: Exit *Normal* mode and enter *Insert* mode, moving the cursor (vertical bar) to beginning of the line.
    - `A`: Exit *Normal* mode and enter *Insert* mode, moving the cursor (vertical bar) to end of the line.
    - `R`: Exit *Normal* mode and enter *Replace* mode, preserving the cursor (underscore) position.
- Search through history: (To be implemented)
    - `?<search-string><Enter>`: search the history from latest to oldest, where <search-string> is any regex string.
      Notice the leading `?`.
    - `/<search-string><Enter>`: search the history from oldest to latest. Notice the leading `/`.
    - Once search is started, use `n`/`N` to find the next/previous match.
    - Unlike in vim, the `<search-string>` does not appear when typed. The use must be responsible for inputting correct
      string blindly.
- Miscellaneous
    - `Enter`: Sends the current line. Notice that the next prompt will still be in *Normal* mode.
    - `~`: Switch casing of the current character. I.e., change `a` to 'A` and `A` to `a` (To be implemented)
    - `%`: Navigate between matching pairs of parentheses, square brackets, angle brackets, or curly braces. (To be
      implemented)

## Unsupported Vim Features

Currently, there is no plan to implement

- Any commands with repetitions, e.g., `2w`, `f3a`, `10x`.
- The undo/repo commands `u`, `<CTRL>r`.
- The repeat command `.`.
- Visual mode and commands in visual mode
- Command-line mode.
