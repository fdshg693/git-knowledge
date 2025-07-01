# Vim Shortcuts and Commands: Complete Beginner's Guide

## Overview
Vim (Vi Improved) is a powerful text editor that operates through keyboard commands rather than mouse interactions. While initially challenging, mastering Vim's modal editing approach can dramatically increase your text editing efficiency. This guide covers essential shortcuts, commands, and concepts for beginners.

## Table of Contents
1. [Understanding Vim Modes](#understanding-vim-modes)
2. [Essential Navigation Commands](#essential-navigation-commands)
3. [Basic Text Editing](#basic-text-editing)
4. [Intermediate Commands](#intermediate-commands)
5. [File Operations](#file-operations)
6. [Search and Replace](#search-and-replace)
7. [Visual Mode Operations](#visual-mode-operations)
8. [Customization Basics](#customization-basics)
9. [Common Workflows](#common-workflows)
10. [Best Practices](#best-practices)

## Understanding Vim Modes

Vim operates in different modes, each serving specific purposes:

### 1. Normal Mode (Command Mode)
- **Default mode** when you open Vim
- Used for navigation and executing commands
- Press `Esc` to return to Normal mode from any other mode
- **Key insight**: Think of this as your "home base" - you'll spend most time here

### 2. Insert Mode
- For typing and editing text
- Enter with: `i` (insert), `a` (append), `o` (open new line)
- **Visual cue**: Look for `-- INSERT --` at the bottom

### 3. Visual Mode
- For selecting text
- Enter with: `v` (character), `V` (line), `Ctrl+v` (block)
- **Purpose**: Select text before performing operations

### 4. Command-Line Mode
- For executing complex commands
- Enter with: `:` (ex commands), `/` (search), `?` (reverse search)
- **Usage**: File operations, settings, advanced editing

## Essential Navigation Commands

### Basic Movement (Normal Mode)
```
h, j, k, l    ← ↓ ↑ →     (Arrow keys also work, but h/j/k/l is faster)
w             Move forward by word
b             Move backward by word
e             Move to end of current word
0             Move to beginning of line
$             Move to end of line
gg            Go to first line of file
G             Go to last line of file
```

### Advanced Navigation
```
f{char}       Find character forward in line
F{char}       Find character backward in line
t{char}       Move to just before character forward
T{char}       Move to just after character backward
;             Repeat last f, F, t, or T command
,             Repeat last f, F, t, or T command in reverse
```

### Line and Page Navigation
```
Ctrl+f        Page down (forward)
Ctrl+b        Page up (backward)
Ctrl+d        Half page down
Ctrl+u        Half page up
{number}G     Go to specific line number (e.g., 15G goes to line 15)
H             Move to top of screen
M             Move to middle of screen
L             Move to bottom of screen
```

## Basic Text Editing

### Entering Insert Mode
```
i             Insert before cursor
a             Insert after cursor
I             Insert at beginning of line
A             Insert at end of line
o             Open new line below current line
O             Open new line above current line
```

### Basic Deletion
```
x             Delete character under cursor
X             Delete character before cursor
dd            Delete entire line
dw            Delete word from cursor position
d$            Delete from cursor to end of line
d0            Delete from cursor to beginning of line
```

### Copy (Yank) and Paste
```
yy            Copy (yank) entire line
yw            Copy word from cursor position
y$            Copy from cursor to end of line
p             Paste after cursor/line
P             Paste before cursor/line
```

### Undo and Redo
```
u             Undo last change
Ctrl+r        Redo last undone change
.             Repeat last command
```

## Intermediate Commands

### Text Manipulation
```
r{char}       Replace single character under cursor
R             Enter replace mode (overwrite text)
~             Change case of character under cursor
>>            Indent line right
<<            Indent line left
J             Join current line with next line
```

### Advanced Deletion and Editing
```
cw            Change word (delete word and enter insert mode)
cc            Change entire line
c$            Change from cursor to end of line
s             Substitute character (delete char and enter insert mode)
S             Substitute entire line
```

### Working with Numbers (Multipliers)
```
5j            Move down 5 lines
3dd           Delete 3 lines
2yy           Copy 2 lines
4w            Move forward 4 words
10x           Delete 10 characters
```

## File Operations

### Opening and Saving Files
```
:w            Save (write) file
:q            Quit Vim
:wq           Save and quit
:q!           Quit without saving (force quit)
:w filename   Save as new filename
:e filename   Edit (open) another file
```

### File Information
```
:pwd          Show current directory
:ls           List open buffers
:set nu       Show line numbers
:set nonu     Hide line numbers
```

## Search and Replace

### Basic Search
```
/pattern      Search forward for pattern
?pattern      Search backward for pattern
n             Go to next search result
N             Go to previous search result
*             Search for word under cursor (forward)
#             Search for word under cursor (backward)
```

### Find and Replace
```
:s/old/new/           Replace first occurrence in current line
:s/old/new/g          Replace all occurrences in current line
:%s/old/new/g         Replace all occurrences in entire file
:%s/old/new/gc        Replace all with confirmation
:10,20s/old/new/g     Replace in lines 10-20
```

## Visual Mode Operations

### Selecting Text
```
v             Start character-wise visual selection
V             Start line-wise visual selection
Ctrl+v        Start block-wise visual selection
```

### Operations in Visual Mode
```
d             Delete selected text
y             Copy (yank) selected text
c             Change selected text (delete and enter insert mode)
>             Indent selected lines
<             Unindent selected lines
:             Execute command on selection
```

## Customization Basics

### .vimrc Configuration
Create a `.vimrc` file in your home directory for persistent settings:

```vim
" Enable line numbers
set number

" Enable syntax highlighting
syntax on

" Set tab width to 4 spaces
set tabstop=4
set shiftwidth=4
set expandtab

" Enable incremental search
set incsearch

" Highlight search results
set hlsearch

" Enable mouse support
set mouse=a

" Show matching brackets
set showmatch
```

### Common Settings Commands
```
:set number       Show line numbers
:set nonumber     Hide line numbers
:set hlsearch     Highlight search results
:set nohlsearch   Turn off search highlighting
:syntax on        Enable syntax highlighting
:syntax off       Disable syntax highlighting
```

## Common Workflows

### Efficient Text Navigation Workflow
1. Use `f{char}` to quickly jump to characters in a line
2. Use `w` and `b` for word-by-word movement
3. Use `0` and `$` for line boundaries
4. Use `gg` and `G` for file boundaries

### Quick Editing Workflow
1. Navigate to target location (Normal mode)
2. Enter appropriate editing mode (`i`, `a`, `o`, etc.)
3. Make changes
4. Press `Esc` to return to Normal mode
5. Use `.` to repeat last change if needed

### Search and Replace Workflow
1. Use `/pattern` to find target text
2. Navigate through results with `n` and `N`
3. Use `:%s/old/new/gc` for global replace with confirmation
4. Review each replacement before accepting

## Best Practices

### For Beginners
1. **Stay in Normal Mode**: Return to Normal mode frequently - it's your command center
2. **Use hjkl**: Train yourself to use hjkl instead of arrow keys for faster navigation
3. **Master Basic Commands First**: Focus on i, a, o, dd, yy, p, u before advanced features
4. **Practice Daily**: Even 10-15 minutes daily will build muscle memory
5. **Don't Use Mouse**: Force yourself to use keyboard commands only

### Efficiency Tips
1. **Use Multipliers**: Commands like `5dd` or `3w` are more efficient than repeating single commands
2. **Learn Text Objects**: Commands like `diw` (delete in word) or `ci"` (change in quotes)
3. **Use . Command**: The dot command repeats your last change - very powerful for repetitive tasks
4. **Customize Your .vimrc**: Set up your environment to match your workflow
5. **Learn One New Command Per Day**: Gradually expand your command vocabulary

### Common Mistakes to Avoid
1. **Don't Stay in Insert Mode**: Only enter Insert mode when actively typing
2. **Don't Ignore Visual Mode**: It's excellent for precise text selection
3. **Don't Fear the Command Line**: `:` commands are powerful for file operations
4. **Don't Skip the Help**: `:help command` provides detailed information
5. **Don't Give Up Early**: The learning curve is steep but the payoff is enormous

## Next Steps
Once comfortable with these basics, explore:
- Advanced text objects and motions
- Macros and recording commands
- Window and tab management
- Plugin systems (Vim-Plug, Pathogen)
- Advanced customization and scripting

Remember: Vim mastery comes through practice. Start with basic commands and gradually incorporate more advanced features into your workflow.
