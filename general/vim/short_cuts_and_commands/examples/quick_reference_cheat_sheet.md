# Vim Quick Reference Cheat Sheet

## Essential Commands for Daily Use

### Modes (The Foundation)
```
Esc           Return to Normal mode (your home base)
i             Enter Insert mode (before cursor)
a             Enter Insert mode (after cursor)
v             Enter Visual mode (character selection)
V             Enter Visual mode (line selection)
:             Enter Command-line mode
```

### Navigation (Normal Mode)
```
BASIC MOVEMENT
h j k l       ← ↓ ↑ → (Use these instead of arrow keys!)
w             Word forward
b             Word backward
0             Start of line
$             End of line
gg            Top of file
G             Bottom of file

ADVANCED MOVEMENT
f{char}       Find character forward in line
F{char}       Find character backward in line
*             Find word under cursor
{number}G     Go to line number (e.g., 15G)
```

### Essential Editing
```
ENTERING TEXT
i             Insert before cursor
a             Insert after cursor
o             Open new line below
O             Open new line above

DELETING
x             Delete character
dd            Delete line
dw            Delete word
d$            Delete to end of line

COPY & PASTE
yy            Copy line
yw            Copy word
p             Paste after
P             Paste before

UNDO/REDO
u             Undo
Ctrl+r        Redo
.             Repeat last command
```

### File Operations
```
:w            Save file
:q            Quit
:wq           Save and quit
:q!           Quit without saving
:e filename   Open file
```

### Search & Replace
```
/pattern      Search forward
?pattern      Search backward
n             Next search result
N             Previous search result
:s/old/new/g  Replace all in line
:%s/old/new/g Replace all in file
```

---

## Quick Command Combinations

### Efficient Editing Patterns
```
ci"           Change inside quotes
di(           Delete inside parentheses
yi{           Yank inside braces
va"           Visual select around quotes (including quotes)
vi"           Visual select inside quotes (excluding quotes)
```

### Multipliers (Power User Moves)
```
5j            Move down 5 lines
3dd           Delete 3 lines
2yy           Copy 2 lines
4w            Move forward 4 words
10x           Delete 10 characters
```

### Line Operations
```
>>            Indent line right
<<            Indent line left
J             Join line with next line
~             Change case of character
```

---

## Most Common Workflows

### 1. Quick Text Insertion
```
1. Navigate to position (hjkl, w, b, f)
2. Choose insert mode: i (before) or a (after)
3. Type your text
4. Press Esc to return to Normal mode
```

### 2. Delete and Replace Text
```
1. Navigate to target text
2. Delete: x (char), dw (word), dd (line)
3. Enter insert mode: i, a, o
4. Type replacement text
5. Press Esc
```

### 3. Copy Text Elsewhere
```
1. Navigate to text to copy
2. Copy: yy (line), yw (word), or use visual mode
3. Navigate to destination
4. Paste: p (after) or P (before)
```

### 4. Find and Replace
```
1. Search for text: /pattern
2. Navigate through results: n, N
3. Replace globally: :%s/old/new/g
   Or replace with confirmation: :%s/old/new/gc
```

---

## Emergency Commands

### "Help, I'm Stuck!"
```
Esc Esc Esc   Get back to Normal mode (press multiple times)
:q!           Quit without saving (when all else fails)
u             Undo last change
:help         Access Vim's built-in help
```

### "I Made a Mistake!"
```
u             Undo last change
Ctrl+r        Redo (undo the undo)
:e!           Reload file from disk (lose all changes)
```

---

## Settings Quick Setup

### Essential .vimrc Settings
```vim
set number          " Show line numbers
syntax on           " Enable syntax highlighting
set hlsearch        " Highlight search results
set incsearch       " Incremental search
set tabstop=4       " Tab width
set expandtab       " Use spaces instead of tabs
set mouse=a         " Enable mouse support
```

### Temporary Settings (During Session)
```
:set number     " Show line numbers
:set nonumber   " Hide line numbers
:syntax on      " Enable syntax highlighting
:noh            " Turn off search highlighting
```

---

## Memory Aids

### Movement Mnemonics
- **h** = left (h is on the left of jkl)
- **j** = down (j looks like a down arrow)
- **k** = up (k points up)
- **l** = right (l is on the right of hjk)
- **w** = word forward
- **b** = back word
- **f** = find character
- **$** = end (like end of command in shell)

### Command Patterns
- **d** = delete (dd = delete line, dw = delete word)
- **y** = yank/copy (yy = yank line, yw = yank word)
- **c** = change (cc = change line, cw = change word)
- **i** = inside (di" = delete inside quotes)
- **a** = around (da" = delete around quotes, including quotes)

---

## Learning Path Priority

### Week 1: Master These First
```
hjkl movement
i, a for insert mode
Esc to get back to Normal
dd, yy, p for delete/copy/paste
:w, :q, :wq for file operations
```

### Week 2: Add These
```
0, $ for line movement
w, b for word movement
x for character deletion
dw for word deletion
/search and n, N
```

### Week 3: Power User Moves
```
f{char} for quick navigation
Visual mode with v, V
. for repeat command
Basic multipliers like 3dd, 5w
:s///g for search and replace
```

---

## Pro Tips

1. **Stay in Normal Mode**: Think of Normal mode as your home base
2. **Use hjkl**: Train yourself away from arrow keys
3. **Master the Dot**: The `.` command is incredibly powerful for repetitive tasks
4. **Learn Gradually**: Focus on one new command per day
5. **Practice Daily**: Even 10 minutes daily builds muscle memory
6. **Customize Later**: Get comfortable with defaults before customizing

---

## Common Beginner Mistakes to Avoid

❌ **Don't**: Stay in Insert mode when not typing
✅ **Do**: Return to Normal mode immediately after typing

❌ **Don't**: Use the mouse for navigation
✅ **Do**: Force yourself to use keyboard commands

❌ **Don't**: Try to learn everything at once
✅ **Do**: Master basics before moving to advanced features

❌ **Don't**: Give up after the first day
✅ **Do**: Practice consistently for at least a week

---

*Print this cheat sheet and keep it nearby while learning Vim!*
