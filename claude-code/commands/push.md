# /push - Intelligent Git Push Workflow

## Usage
- `/push` - Auto-generate commit message and push to current branch (or push existing commits if working directory is clean)
- `/push [branch]` - Push to specific branch with auto-generated commit message  
- `/push [commit_message]` - Push to current branch with custom commit message
- `/push [branch] [commit_message]` - Push to specific branch with custom commit message
- `/push all` - Comprehensive workflow: save, stage ALL changes, commit, and push to current branch
- `/push all [branch]` - Same as above but push to specific branch
- `/push all [commit_message]` - Same as above with custom commit message
- `/push all [branch] [commit_message]` - Full control with all argument

**Smart Push Detection**: The command automatically detects when your working directory is clean but you have local commits ready to push, and switches to push-only mode.

## Special "all" Workflow

When the `all` argument is detected, execute this comprehensive workflow:

### All Changes Capture Process
1. **Save All Open Files**: Notify user to save any unsaved files in editors, or check common editor auto-save locations
2. **Stage ALL Changes**: Use `git add -A` to stage:
   - Modified files
   - New/untracked files  
   - Deleted files
   - Renamed/moved files
3. **Include Ignored Files Check**: Ask user if they want to review and potentially include any currently ignored files that might be relevant
4. **Comprehensive Status**: Run `git status --porcelain` and `git diff --cached --name-status` to show exactly what will be committed

Display enhanced summary with proper line breaks and terminal formatting:

**Terminal Formatting with Fallback:**
- Primary: Use terminal color codes and Unicode emoji for rich display
- Fallback: If terminal doesn't support formatting, use plain text equivalents
- Auto-detect terminal capabilities with `tput colors` or environment variables

Format and display the summary as follows:
📋 COMPREHENSIVE PUSH SUMMARY (ALL Changes)
==================================================
📁 Repository: [repo-name] ([platform])
🌿 Current Branch: [current-branch]
🎯 Target Branch: [target-branch]
🚀 Pipeline: [pipeline-info]

📝 ALL Changes to commit:
   ✏️ Modified: [list]
   ➕ New/Added: [list]
   ❌ Deleted: [list]
   📦 Renamed/Moved: [list]

💬 Commit Message: [generated/provided message]

⚠️  Pipeline Warning: [if applicable]

⚠️  ALL CHANGES MODE: This will commit EVERYTHING in your working directory
==================================================

Then proceed with the standard approval process.

## Standard Workflow Instructions

### 1. Pre-Push Analysis
**Git Repository Validation:**
- First, verify this is a git repository: `git rev-parse --git-dir`
- If not a git repository: Display "❌ Error: Not a git repository. Run 'git init' to initialize." and stop
- If git command fails: Display "❌ Error: Git not available or repository corrupted." and stop

**Merge Conflict Detection:**
- Check for unresolved merge conflicts: `git diff --name-only --diff-filter=U`
- If conflicts found: Display "❌ Error: Unresolved merge conflicts detected in: [files]. Resolve conflicts before pushing." and stop
- Check merge status: `git status --porcelain | grep '^UU\|^AA\|^DD'`
- If merge in progress: Display "❌ Error: Merge in progress. Complete merge or abort with 'git merge --abort'." and stop

Run these commands in parallel to gather repository information:
- `git status --porcelain` - Check for uncommitted changes
- `git branch --show-current` - Get current branch  
- `git remote -v` - Get repository information
- `git diff --name-only HEAD` - Get list of changed files

**Handle Clean Working Directory:**
If no uncommitted changes exist (`git status --porcelain` is empty):
1. Check for commits ahead of remote: `git log origin/[branch]..HEAD --oneline`
2. If commits exist to push:
   - Skip to step 1.5 (configure git credentials)
   - Skip to step 4 (show push summary) with commits to push
   - Continue with approval and push workflow
3. If no commits to push: display "❌ No changes to commit or push. Everything is up to date." and stop.

### 1.5. Repository-Specific Git Configuration
**Verify git user settings are configured for the repository:**

- Check current config: `git config user.email` and `git config user.name`
- If not configured, prompt user to set them:
  - `git config user.email "your-email@example.com"`
  - `git config user.name "Your Name"`
- Note: Users with multiple git identities can configure per-repository settings using `git config` (without `--global`)

### 2. Pipeline Detection
Check for deployment pipeline configurations:
- **Bitbucket**: Look for `bitbucket-pipelines.yml` in project root
- **GitHub Actions**: Check for `.github/workflows/*.yml` files
- Display appropriate pipeline warning if found

### 3. Intelligent Commit Message Generation
If no commit message provided by user:

**For single file changes:**
- Analyze the actual file content changes using `git diff` 
- Generate descriptive commit message based on the nature of changes
- Examples: "Add user authentication endpoint", "Fix memory leak in parser", "Update API documentation"

**For multiple files:**
- Categorize changes (new features, bug fixes, refactoring, documentation)
- Generate comprehensive message describing the overall change
- Examples: "Implement user dashboard with authentication", "Refactor database layer and update tests"

**Commit Message Quality Standards:**
- Use imperative mood ("Add", "Fix", "Update", not "Added", "Fixed", "Updated")
- Be specific about what changed and why
- Limit first line to 50 characters when possible
- Add detailed explanation if changes are complex
- **NEVER include references to Claude, AI, or automated generation** - commit messages should appear natural and human-written

### 4. Pre-Push Summary Display
Show formatted summary for user approval with proper line breaks and terminal formatting:

**For uncommitted changes (commit + push workflow):**
📋 PUSH SUMMARY
==================================================
📁 Repository: [repo-name] ([platform])
🌿 Current Branch: [current-branch]
🎯 Target Branch: [target-branch]
🚀 Pipeline: [pipeline-info]

📝 Changes to commit:
   [list of files with change types]

💬 Commit Message: [generated/provided message]

⚠️  Pipeline Warning: [if applicable]
==================================================

**For clean working directory (push-only workflow):**
📋 PUSH SUMMARY
==================================================
📁 Repository: [repo-name] ([platform])
🌿 Current Branch: [current-branch]
🎯 Target Branch: [target-branch]
🚀 Pipeline: [pipeline-info]

📝 Commits to push:
   [list of commits with commit messages]

💬 Ready to push [X] commit(s) to origin/[branch]

⚡ Auto-configured git credentials for [platform]

⚠️  Pipeline Warning: [if applicable]
==================================================

### 5. User Approval Process
**Enhanced User Approval with Clear Options:**

Present the summary and ask: **"Do you want to proceed with this push?"**

**Response Options:**
- **"yes"**, **"y"**, **"proceed"**, **"go"** - Execute as shown
- **"no"**, **"n"**, **"cancel"**, **"abort"** - Cancel the push
- **"edit message [new message]"** - Change commit message only
- **"change branch [branch-name]"** - Change target branch only  
- **"show diff"** - Display detailed changes before deciding
- **"yes, but [modification]"** - Approve with changes (e.g., "yes, but change message to 'Fix parser'")

**Input Validation:**
- Case-insensitive response matching
- Trim whitespace from responses
- Handle partial matches ("ye" → "yes", "ca" → "cancel")
- Clear error for unrecognized responses: "❌ Please respond with 'yes', 'no', or specify modifications."
- Timeout after 60 seconds of no response: "⏰ No response received. Push cancelled for safety."

### 6. Handle User Response
- **If approved with no modifications**: Proceed to step 7
- **If approved with modifications**: Update the plan according to user specifications, show updated summary, then proceed
- **If declined**: Display "❌ Push cancelled." and stop

### 7. Git Operations Execution  
Execute in sequence with status updates and comprehensive error handling:

**For push-only mode (clean working directory with commits to push):**
1. **Push**: `git push origin [final-target-branch]`
   - **Error handling**: If push fails:
     - Check for rejected push: "Updates were rejected" → Display "❌ Push rejected. Pull latest changes first: 'git pull origin [branch]'"
     - Check for no upstream: "fatal: The current branch" → Display "❌ No upstream branch set. Use: 'git push -u origin [branch]'"
     - Check for authentication: "Authentication failed" → Display "❌ Authentication failed. Check git credentials."
     - Check for network: "Could not resolve host" → Display "❌ Network error. Check internet connection."
     - Generic error: Display "❌ Push failed: [error message]. Please check repository status."

**For "all" mode (commit + push):**
1. **Stage ALL changes**: `git add -A` (includes deletions, renames, and new files)
   - **Error handling**: If staging fails → Display "❌ Staging failed: [error]. Check file permissions and disk space."
2. **Commit**: `git commit -m "[final-commit-message]"`
   - **Error handling**: If commit fails:
     - Check for empty commit: "nothing to commit" → Display "❌ No changes to commit after staging."
     - Check for commit message: "Aborting commit due to empty commit message" → Display "❌ Empty commit message. Please provide a message."
     - Generic error: Display "❌ Commit failed: [error]. Check repository status."
3. **Push**: `git push origin [final-target-branch]`
   - **Error handling**: Same as push-only mode above

**For standard mode (commit + push):**
1. **Stage changes**: `git add .` (current directory and subdirectories)
   - **Error handling**: Same as "all" mode staging
2. **Commit**: `git commit -m "[final-commit-message]"`
   - **Error handling**: Same as "all" mode commit
3. **Push**: `git push origin [final-target-branch]`
   - **Error handling**: Same as push-only mode above

**General Error Recovery:**
- After any error, run `git status` to show current repository state
- Suggest specific recovery actions based on error type
- Preserve user's work and avoid destructive operations

### 8. Success Confirmation
Display completion message:
```
✅ Push completed successfully!
🎉 Changes pushed to [repo-name] on branch '[branch]'
🚀 [Pipeline trigger message if applicable]
```

## Argument Parsing Logic

### Special Directory Shortcuts
- If arguments match `dotfiles` → Execute dotfiles workflow:
  1. Change to `~/.config` or specified dotfiles directory
  2. Execute standard push workflow from that directory
  3. Use "Update dotfiles" as default commit message if none provided
  4. Return to original directory after completion

### "all" Argument Detection
- If first argument is `all` → Enable comprehensive "all changes" mode
- `/push all` → All changes to current branch
- `/push all [branch]` → All changes to specified branch  
- `/push all [commit_message]` → All changes with custom message to current branch
- `/push all [branch] [commit_message]` → All changes with full control

### Standard Argument Parsing
**Improved Edge Case Handling:**
- Empty arguments → Use current branch and generate commit message
- Single argument parsing:
  - Contains spaces → Always treat as commit message (e.g., "fix user login")
  - Matches commit keywords ('add', 'update', 'fix', 'remove', 'refactor', 'implement', 'create', 'delete', 'modify') → Treat as commit message
  - Valid git branch name pattern (alphanumeric, hyphens, underscores, slashes) → Treat as target branch
  - Ambiguous single word → Ask user: "Is '[argument]' a branch name or commit message?"
- Multiple arguments → first is branch, rest combined as commit message
- Branch validation → Check if specified branch exists locally or remotely before proceeding
- Special characters handling → Properly escape commit messages with quotes, apostrophes, and special characters

## Error Handling
- Validate git repository exists
- Check for merge conflicts before pushing
- Provide clear error messages for common issues
- Suggest solutions when possible

## Special Considerations
- Always use current branch as default target
- Generate meaningful commit messages by analyzing actual code changes
- Warn about deployment pipelines before pushing
- Support both GitHub and Bitbucket repository detection
- Maintain consistent emoji-based status indicators
- Wait for explicit user approval before executing any git operations
- **"all" mode captures EVERYTHING**: deletions, renames, new files, and modifications
- **"all" mode safety**: Always show comprehensive summary before execution
- **File saving reminder**: Prompt user to save unsaved work when using "all" mode
- **Smart push detection**: Automatically detects when working directory is clean but local commits exist, switches to push-only mode
- **Push-only workflow**: When no uncommitted changes exist but commits are ahead of remote, skips commit steps and goes straight to push
