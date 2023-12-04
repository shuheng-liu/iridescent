# Viris – Vim meets IRIS

## Usage

```bash
viris [-h] [--input-path INPUT_PATH] [--output-path OUTPUT_PATH] [--debug-path DEBUG_PATH] [--history-path HISTORY_PATH] [instance]
```

Positional arguments

```
  instance (defaults to $IRIS_INSTANCE environment variable)
```

Optional arguments

```
  -h, --help            show the help message and exit
  --input-path INPUT_PATH, -i INPUT_PATH
                        location of input logs
  --output-path OUTPUT_PATH, -o OUTPUT_PATH
                        location of output logs
  --debug-path DEBUG_PATH, -d DEBUG_PATH
                        Location of debugging logs
  --history-path HISTORY_PATH, -H HISTORY_PATH
                        Location of history file
```

Environment variables

- `$IRIS_USERNAME` and `$IRIS_PASSWORD`: If both are set, will be used for authentication.
- `$IRIS_INSTANCE`: If present, will be the default instance.

## How it works

The project is based on the [`pexpect`](https://pexpect.readthedocs.io/en/stable/) library.

Once `viris` starts, it spins up another process
of [InterSystems IRIS](https://docs.intersystems.com/iris20233/csp/docbook/Doc.View.cls?KEY=TOS_Terminal) terminal
that runs in the background.
`viris` intercepts user keystrokes, parses them, and passes along to the background `IRIS terminal` process, and renders
the output of `IRIS terminal` back to the user.
To parse keystrokes, `viris` maintains an inner state of the current prompt line, position of the cursor, and shape of
the cursor (vertical bar for *Insert* mode, rectangular block for *Normal* mode, underscore for *Replace* mode).
For example, in *Insert* mode, hitting `<OPTION> + <DELETE>` or `<ALT> + <DELETE>` when the current prompt and cursor
positions is

```
USER>set obj = ##class(%Dynam|icObject).%New()     // vertical bar "|" is cursor position
```

will send 5 `<DELETE>`s to the backend `IRIS terminal` process and the resulting prompt will be

```
USER>set obj = ##class(%|icObject).%New()          // vertical bar "|" is cursor position
```

.

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
    - `f<char>`: Navigate to the next occurrence of `<char>`
    - `F<char>`: Navigate to the previous occurrence of `<char>`
    - `t<char>`: Navigate to the character before the next occurrence of `<char>`
    - `T<char>`: Navigate to the character after the previous occurrence of `<char>`
    - `%`: Navigate between matching pairs of parentheses, square brackets, angle brackets, or curly braces.
- Deletion:
    - `dw`/`dW`: Delete until the next beginning-of-word.
    - `de`/`dE`: Delete until the next end-of-word.
    - `db`/`dB`: Delete until the previous beginning-of-word.
    - `dd`: Delete all characters on the current line.
    - `d0`: Delete until beginning of the line.
    - `d$`: Delete until end of the line.
    - `dt<char>`: Delete until the next occurrence of `<char>` (exclusive).
    - `dT<char>`: Delete backwards until the next occurrence of `<char>` (exclusive).
    - `df<char>`: Delete until the next occurrence of `<char>` (inclusive).
    - `dF<char>`: Delete backwards until the next occurrence of `<char>` (inclusive).
    - `di<char>`: Delete everything within the enclosing pair of
        - parentheses `(...)`: if `<char>` is either `(` or `)`
        - square brackets `[...]`: if `<char>` is either `[` or `]`
        - curly braces `{...}`: if `<char>` is either `[` or `]`
        - angle brackets `<...>`: if `<char>` is either `<` or `>`
        - backticks <code>&#96;...&#96;</code>: if `<char>` is backtick <code>`</code>
        - single quotes `'...'`: if `<char>` is single quote `'`
        - double quotes `"..."`: if `<char>` is double quote `"`
        - commas `,...,` if `<char>` is comma `,` (standard Vim doesn't support this)
        - spaces <code>&nbsp;...&nbsp;</code> if `<char>` is space ` ` (standard Vim doesn't support this)
    - `diw` and `diW`: As a special case to the above, `diw` deletes the word under cursor.
      Capital `w` treats consecutive non-whitespace characters as a word.
      If the current character under cursor is a whitespace, consecutive whitespaces are considered a word.
    - `x`: Delete the character under cursor
- Change:
    - The change commands are almost identical to the delete commands listed above.
      The difference is that a change command will exit *Normal* mode and enter *Insert* mode after deleting characters.
    - The keystrokes for a change command is obtained by changing the leading `d` to `c`.
        - `cw`, `cW`, `ce`, `cE`, `cb`, `cB`, `c0`, `c$`, `ct<char>`, `cT<char>`, `cf<char>`, `cF<char>`, `ci<char>`
    - Special cases are:
        - `cc`: Delete the current line and set to insert mode.
        - `s`: Delete the character under cursor and set to insert mode.
- Copy/Paste:
    - A text segment is automatically copied to the internal clipboard once it's deleted by a *Delete* or *Change*
      command.
    - You can optionally copy something without deleting them with the yank commands: (TODO)
      `yw`, `yW`, `ye`, `yE`, `yb`, `yB`, `yy`, `y0`, `y$`, `yt<char>`, `yT<char>`, `yf<char>`, `yF<char>`, `yi<char>`
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
- Search through history: (TODO)
    - `?<search-string><Enter>`: search the history from latest to oldest, where <search-string> is any regex string.
      Notice the leading `?`.
    - `/<search-string><Enter>`: search the history from oldest to latest. Notice the leading `/`.
    - Once search is started, use `n`/`N` to find the next/previous match.
    - Unlike in vim, the `<search-string>` does not appear when typed. The use must be responsible for inputting correct
      string blindly.
- Miscellaneous
    - `Enter`: Sends the current line. Notice that the next prompt will still be in *Normal* mode.
    - `~`: Switch casing of the current character. I.e., change `a` to 'A` and `A` to `a`

## Unsupported Vim Features

Currently, there is no plan to implement

- Any commands with repetitions, e.g., `2w`, `f3a`, `10x`.
- The undo/repo commands `u`, `<CTRL>r`.
- The repeat command `.`.
- Visual mode and commands in visual mode
- Command-line mode.
