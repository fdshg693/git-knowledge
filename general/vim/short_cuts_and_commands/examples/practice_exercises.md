# Vim Practice Exercises for Beginners

## Exercise 1: Basic Navigation and Movement

### Setup
Create a simple text file with the following content:

```
The quick brown fox jumps over the lazy dog.
This line contains several words for practice.
Here we have another line with different content.
Line four has some numbers: 123, 456, 789.
Final line of our practice text file.
```

### Navigation Challenges
1. **Basic Movement**: Starting at the beginning, use only `h`, `j`, `k`, `l` to move to the word "fox"
2. **Word Movement**: From "fox", use `w` to move forward word by word to "lazy"
3. **Line Movement**: Use `0` to go to the beginning of the line, then `$` to go to the end
4. **File Movement**: Use `gg` to go to the first line, then `G` to go to the last line
5. **Line Numbers**: Go to line 3 using `3G`

### Expected Results
- You should be comfortable moving around without using arrow keys
- Practice until you can navigate to any word without thinking about the commands

---

## Exercise 2: Basic Editing Operations

### Text Editing Practice
Using the same text file:

1. **Insert Text**: 
   - Position cursor at the beginning of line 1
   - Press `i` and add "INTRO: " before "The quick brown fox"
   - Press `Esc` to return to Normal mode

2. **Append Text**:
   - Move to the end of line 1
   - Press `a` and add " END"
   - Press `Esc`

3. **New Lines**:
   - Position cursor on line 2
   - Press `o` to create a new line below and add "This is a new line below."
   - Press `Esc`
   - Press `O` to create a new line above and add "This is a new line above."
   - Press `Esc`

### Expected Results
Your file should now look like:
```
INTRO: The quick brown fox jumps over the lazy dog. END
This is a new line above.
This line contains several words for practice.
This is a new line below.
Here we have another line with different content.
Line four has some numbers: 123, 456, 789.
Final line of our practice text file.
```

---

## Exercise 3: Delete, Copy, and Paste Operations

### Setup Text
```
apple banana cherry
dog elephant fox giraffe
red green blue yellow
123 456 789 012
```

### Deletion Practice
1. **Delete Characters**: Position cursor on 'a' in "apple", press `x` to delete it
2. **Delete Words**: Position cursor on "banana", press `dw` to delete the word
3. **Delete Lines**: Position cursor anywhere on line 2, press `dd` to delete entire line
4. **Delete to End**: Position cursor on 'g' in "green", press `d$` to delete to end of line

### Copy and Paste Practice
1. **Copy Word**: Position cursor on "red", press `yw` to copy the word
2. **Paste**: Move to end of line 4, press `p` to paste "red"
3. **Copy Line**: Position cursor on line with numbers, press `yy` to copy entire line
4. **Paste Line**: Move to end of file, press `p` to paste the line

### Undo Practice
1. Press `u` several times to undo your changes
2. Press `Ctrl+r` to redo some changes
3. Practice until comfortable with undo/redo flow

---

## Exercise 4: Search and Replace Workflow

### Practice Text
```
The cat sat on the mat.
A cat is a wonderful pet.
Cats are independent animals.
My cat likes to sleep in the sun.
Some people prefer dogs to cats.
```

### Search Practice
1. **Basic Search**: Press `/cat` and press Enter to search for "cat"
2. **Navigate Results**: Use `n` to go to next occurrence, `N` to go to previous
3. **Word Search**: Position cursor on any "cat" and press `*` to search for that word

### Replace Practice
1. **Single Line Replace**: On line 1, type `:s/cat/dog/` to replace first "cat" with "dog"
2. **Global Line Replace**: Type `:s/cat/dog/g` to replace all "cat" with "dog" on current line
3. **File-wide Replace**: Type `:%s/cat/dog/g` to replace all "cat" with "dog" in entire file
4. **Confirm Replace**: Type `:%s/dog/cat/gc` to replace with confirmation

---

## Exercise 5: Visual Mode Selection

### Practice Text
```
Programming languages:
- Python
- JavaScript  
- Java
- C++
- Ruby
- Go
```

### Visual Selection Practice
1. **Character Selection**: 
   - Position cursor at start of "Python"
   - Press `v` to enter visual mode
   - Use arrow keys or `l` to select "Python"
   - Press `d` to delete selection

2. **Line Selection**:
   - Position cursor on "- JavaScript" line
   - Press `V` to select entire line
   - Press `y` to copy the line
   - Move to end of list and press `p` to paste

3. **Block Selection**:
   - Position cursor at the start of first dash (-)
   - Press `Ctrl+v` to enter block visual mode
   - Move down to select all dashes in a column
   - Type `>` to indent all selected lines

---

## Exercise 6: File Operations Practice

### Multi-File Workflow
1. **Create New File**: Type `:e practice2.txt` to create/edit a new file
2. **Switch Between Files**: 
   - Type `:e practice1.txt` to switch back
   - Use `:ls` to see all open buffers
3. **Save Work**: 
   - Type `:w` to save current file
   - Type `:w newname.txt` to save with new name
4. **Exit Workflow**:
   - Type `:q` to quit current file
   - Type `:qall` to quit all files
   - Type `:wq` to save and quit

---

## Exercise 7: Efficiency Commands Practice

### Speed Challenge Text
```
function calculateSum(a, b) {
    return a + b;
}

function calculateProduct(a, b) {
    return a * b;
}

function calculateDifference(a, b) {
    return a - b;
}
```

### Efficiency Practice
1. **Multipliers**: 
   - Use `3dd` to delete 3 lines at once
   - Use `5w` to move forward 5 words
   - Use `2yy` to copy 2 lines

2. **Repeat Command**:
   - Delete a word with `dw`
   - Move to another word and press `.` to repeat deletion
   - Practice until comfortable with the `.` command

3. **Quick Changes**:
   - Use `cw` to change a word (try changing "calculateSum" to "addNumbers")
   - Use `cc` to change an entire line
   - Use `r` to replace a single character

---

## Exercise 8: Real-World Scenario

### Editing a Configuration File
Create a file with this content:
```
# Configuration Settings
debug_mode = false
max_connections = 100
timeout = 30
server_name = "localhost"
port = 8080
ssl_enabled = false
```

### Tasks to Complete
1. **Enable Debug Mode**: Find "debug_mode" and change "false" to "true"
2. **Update Server Settings**: 
   - Change max_connections to 200
   - Change timeout to 60
   - Change server_name to "production-server"
3. **Add New Settings**: Add these lines at the end:
   ```
   log_level = "info"
   backup_enabled = true
   ```
4. **Clean Up**: Remove any trailing whitespace and ensure consistent formatting

### Suggested Vim Commands Sequence
1. `/debug_mode` → `n` → `f=` → `w` → `cw` → type "true" → `Esc`
2. `/max_connections` → navigate and change value
3. `G` → `o` → add new configuration lines
4. `:w` to save your work

---

## Progress Tracking

### Beginner Milestones
- [ ] Can navigate using h/j/k/l comfortably
- [ ] Can enter and exit insert mode smoothly
- [ ] Can delete, copy, and paste text accurately
- [ ] Can search for text and navigate results
- [ ] Can save and quit files confidently
- [ ] Can undo/redo changes without hesitation

### Intermediate Goals
- [ ] Uses multipliers with commands (e.g., 5dd, 3w)
- [ ] Comfortable with visual mode for selections
- [ ] Can perform basic search and replace operations
- [ ] Uses efficient movement commands (f, t, *, #)
- [ ] Begins using the . (repeat) command regularly

### Practice Schedule Suggestion
- **Week 1**: Focus on navigation and basic editing (Exercises 1-2)
- **Week 2**: Master delete, copy, paste operations (Exercise 3)
- **Week 3**: Learn search and replace workflows (Exercise 4)
- **Week 4**: Practice visual mode and file operations (Exercises 5-6)
- **Week 5+**: Build efficiency with advanced commands (Exercises 7-8)

Remember: Consistency is more important than speed. Practice these exercises regularly, and you'll develop muscle memory for Vim commands!
