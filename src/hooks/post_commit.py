import os
import sys
import argparse
import fnmatch
from pathlib import Path
from difflib import unified_diff
import re
import subprocess

script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.insert(0, src_dir)
 
from utils.translation import translate_text, translate_incremental, detect_language

TARGET_LANGUAGES = ["en", "ja"]
TRANSLATION_IGNORE_FILE = ".md_ignore"

# Incremental translation thresholds
DIFF_THRESHOLD_PERCENT = 50  # If diff > 30%, use full translation
LINE_COUNT_THRESHOLD = 100   # If lines <= 100, use full translation

DEFAULT_IGNORE_PATTERNS = []

def load_ignore_patterns(repo_root='.'):
    """Load .ignore_md_translation patterns from client repo"""
    ignore_file = Path(repo_root) / TRANSLATION_IGNORE_FILE
    patterns = []
    
    if ignore_file.exists():
        print(f"Loading ignore patterns from: {ignore_file}")
        try:
            with open(ignore_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
            print(f"Loaded {len(patterns)} custom ignore patterns")
        except Exception as e:
            print(f"Error reading {ignore_file}: {e}")
            patterns = DEFAULT_IGNORE_PATTERNS.copy()
    else:
        print(f"No {TRANSLATION_IGNORE_FILE} file found, using default patterns")
        patterns = DEFAULT_IGNORE_PATTERNS.copy()
    
    return patterns

def should_ignore_file(file_path, ignore_patterns):
    """Check if file should be ignored based on patterns"""
    file_path_str = str(file_path).replace('\\', '/')  # Normalize path separators
    
    for pattern in ignore_patterns:
        # Normalize pattern separators
        pattern = pattern.replace('\\', '/')
        
        # Direct match
        if fnmatch.fnmatch(file_path_str, pattern):
            print(f"Ignoring {file_path_str} (matches pattern: {pattern})")
            return True
        
        # Handle directory patterns ending with /**
        if pattern.endswith('/**'):
            dir_pattern = pattern[:-3]  # Remove /**
            if file_path_str.startswith(dir_pattern + '/') or file_path_str == dir_pattern:
                print(f"Ignoring {file_path_str} (in directory: {dir_pattern})")
                return True
        
        # Handle patterns with path separators
        if '/' in pattern and fnmatch.fnmatch(file_path_str, pattern):
            print(f"Ignoring {file_path_str} (matches path pattern: {pattern})")
            return True
    
    return False

def apply_formatting_fixes(file_path):
    """Apply formatting fixes to a markdown file (preserves markdown two-space line breaks)"""
    if not os.path.exists(file_path):
        return False
    
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Remove trailing whitespace from lines (preserve markdown two-space line breaks)
        lines = content.splitlines()
        fixed_lines = []
        for line in lines:
            # Preserve markdown two-space line breaks: exactly 2 spaces at end of non-blank line
            if line.endswith('  ') and not line.endswith('   ') and line.strip():
                # Line ends with exactly 2 spaces - preserve them
                fixed_lines.append(line[:-2].rstrip() + '  ')
            else:
                # Remove all trailing whitespace
                fixed_lines.append(line.rstrip())
        
        content = '\n'.join(fixed_lines)
        
        # Fix 2: Ensure single newline at end of file
        if content and not content.endswith('\n'):
            content += '\n'
        elif content.endswith('\n\n'):
            # Remove extra newlines, keep only one
            content = content.rstrip('\n') + '\n'
        
        # Fix 3: Remove excessive blank lines (more than 2 consecutive)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✨ Applied formatting fixes to: {file_path}")
            return True
        else:
            print(f"✓ No formatting needed for: {file_path}")
            return False
        
    except Exception as e:
        print(f"Error formatting {file_path}: {e}")
        return False

def calculate_diff_percentage(file_path, current_commit_hash):
    """
    Calculate the percentage of lines changed in a file.
    """
    try:
        # Get base version using git
        result = subprocess.run(
            ['git', 'show', f'HEAD^:{file_path}'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            return None, None, None, None
        
        base_content = result.stdout
        current_content = read_file(file_path)
        
        # Calculate diff
        base_lines = base_content.splitlines()
        current_lines = current_content.splitlines()
        
        diff = list(unified_diff(base_lines, current_lines, lineterm=''))
        
        # Count added and removed lines
        added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        removed = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        
        total_lines = max(len(base_lines), len(current_lines))
        changed_lines = added + removed
        
        if total_lines == 0:
            return 0, 0, 0, base_content
        
        diff_percentage = ((added + removed) / total_lines) * 100
        
        return diff_percentage, len(current_lines), changed_lines, base_content
        
    except Exception as e:
        print(f"Error calculating diff: {e}")
        return None, None, None, None

def get_file_language(file_path):
    """Determine language based on file extension convention"""
    path = Path(file_path)
    
    # Special case for README.md - detect language from content
    if path.name == "README.md":
        if path.exists():
            content = read_file(file_path)
            return detect_language(content)
        return "en"  # Default README to English
    
    # Check for explicit language extensions
    if path.name.endswith('.ja.md'):
        return "ja"
    elif path.name.endswith('.en.md'):
        return "en"
    elif path.name.endswith('.md'):
        # For other .md files, detect language and rename
        if path.exists():
            content = read_file(file_path)
            detected_lang = detect_language(content)
            return detected_lang
        return "en"  # Default to English
    else:
        return None

def get_translated_path(original_path, target_lang):
    """Generate translated file path maintaining directory structure"""
    path = Path(original_path)
    
    # Special case for README.md
    if path.name == "README.md":
        if target_lang == "ja":
            return path.parent / "README.ja.md"
        else:
            return path.parent / "README.en.md"
    
    # Handle other files
    if target_lang == "ja":
        if path.name.endswith('.en.md'):
            # Convert filename.en.md to filename.ja.md
            stem = path.name[:-6]  # Remove .en.md
            return path.parent / f"{stem}.ja.md"
        elif path.name.endswith('.md'):
            # Convert filename.md to filename.ja.md
            stem = path.stem
            return path.parent / f"{stem}.ja.md"
    else:  # target_lang == "en"
        if path.name.endswith('.ja.md'):
            # Convert filename.ja.md to filename.en.md
            stem = path.name[:-6]  # Remove .ja.md
            return path.parent / f"{stem}.en.md"
        elif path.name.endswith('.md'):
            # Convert filename.md to filename.en.md
            stem = path.stem
            return path.parent / f"{stem}.en.md"
    
    return path

def rename_ambiguous_md_file(file_path):
    """Rename .md file to .en.md or .ja.md based on detected language"""
    path = Path(file_path)
    
    # Skip README.md and already explicit files
    if (path.name.upper() == "README.MD" or path.name.endswith('.en.md') or path.name.endswith('.ja.md')):
        return file_path
    
    if path.name.endswith('.md'):
        content = read_file(file_path)
        detected_lang = detect_language(content)
        
        # Create new name with explicit language
        stem = path.stem
        new_name = f"{stem}.{detected_lang}.md"
        new_path = path.parent / new_name
        
        # Rename the file
        print(f"Renaming {file_path} to {new_path} (detected: {detected_lang})")
        os.rename(file_path, new_path)
        return str(new_path)
    
    return file_path

def check_simultaneous_edits(changed_files):
    """Check if both language pairs were edited in the same changeset"""
    files_set = set(changed_files)
    skip_files = set()
    
    for file_path in changed_files:
        if file_path in skip_files:
            continue
            
        path = Path(file_path)
        
        # Special case for README.md
        if path.name == "README.md":
            readme_ja = path.parent / "README.ja.md"
            if str(readme_ja) in files_set:
                print(f"Simultaneous edit detected: {file_path} and {readme_ja}")
                skip_files.add(file_path)
                skip_files.add(str(readme_ja))
            continue
        
        # Check for paired files
        if path.name.endswith('.en.md'):
            stem = path.name[:-6]  # Remove .en.md
            pair_path = path.parent / f"{stem}.ja.md"
        elif path.name.endswith('.ja.md'):
            stem = path.name[:-6]  # Remove .ja.md
            pair_path = path.parent / f"{stem}.en.md"
        else:
            continue
            
        if str(pair_path) in files_set:
            print(f"Simultaneous edit detected: {file_path} and {pair_path}")
            skip_files.add(file_path)
            skip_files.add(str(pair_path))
    
    return skip_files





def read_file(file_path):
    """Read file with encoding fallback"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            return file.read()

def sync_translations(original_file, ignore_patterns):
    """Sync translations for PR events"""
    if not os.path.exists(original_file):
        print(f"File {original_file} not found, skipping")
        return False
    
    # Check if file should be ignored
    if should_ignore_file(original_file, ignore_patterns):
        print(f"⏭️  Skipping translation for {original_file} (matched ignore pattern)")
        return False
    
    # First, handle .md file renaming if needed
    processed_file = rename_ambiguous_md_file(original_file)
    
    source_lang = get_file_language(processed_file)
    if not source_lang:
        print(f"Cannot determine language for {processed_file}, skipping")
        return False
    
    content = read_file(processed_file)
    target_langs = [lang for lang in TARGET_LANGUAGES if lang != source_lang]
    
    # Calculate diff percentage for incremental translation decision
    diff_pct, line_count, changed_lines, base_content = calculate_diff_percentage(processed_file, 'HEAD')
    
    
    translated = False
    for lang in target_langs:
        translated_file = get_translated_path(original_file, lang)
        translated_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine if incremental mode should be used
        use_incremental = False
        
        
        if (diff_pct is not None and 
            diff_pct < DIFF_THRESHOLD_PERCENT and
            changed_lines is not None and
            line_count < LINE_COUNT_THRESHOLD and
            translated_file.exists()):
            use_incremental = True
            print(f"  ✓ Decision: USE INCREMENTAL MODE")
        else:
            print(f"  ✗ Decision: USE FULL TRANSLATION MODE")
            if diff_pct is None:
                print(f"    Reason: diff_pct is None (git diff failed or first commit)")
            elif diff_pct >= DIFF_THRESHOLD_PERCENT:
                print(f"    Reason: diff_pct ({diff_pct:.1f}%) >= threshold ({DIFF_THRESHOLD_PERCENT}%)")
            elif line_count >= LINE_COUNT_THRESHOLD:
                print(f"    Reason: line_count ({line_count}) >= threshold ({LINE_COUNT_THRESHOLD})")
            elif not translated_file.exists():
                print(f"    Reason: translated file does not exist")
        
        # Translate based on mode
        if use_incremental:
            print(f"Using incremental translation for {original_file} (diff: {diff_pct:.1f}%, changed: {changed_lines} lines)")
            existing_translation = read_file(str(translated_file))     
            translated_content = translate_incremental(base_content, content, existing_translation, lang)
            
            # Fall back to full translation if incremental fails
            if not translated_content:
                print(f"Incremental translation failed, falling back to full translation")
                translated_content = translate_text(content, lang)
        else:
            print(f"Using full translation for {original_file}")
            translated_content = translate_text(content, lang)
        
        if translated_content:
            # Write translated content first
            translated_file.write_text(translated_content, encoding='utf-8')
            
            # Apply formatting fixes to the newly written file
            apply_formatting_fixes(str(translated_file))
            
            translated = True
    
    return translated

def find_markdown_files(ignore_patterns):
    """Find all markdown files in project, respecting ignore patterns"""
    markdown_files = []
    
    # Recursively find all .md, .en.md, and .ja.md files from project root
    for root, dirs, files in os.walk('.'):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if not should_ignore_file(os.path.join(root, d), ignore_patterns)]
        
        for file in files:
            if file.endswith('.md'):  # Includes .en.md and .ja.md files
                file_path = os.path.relpath(os.path.join(root, file), '.')
                # Skip hidden directories (.git, .github, etc.) and ignored files
                if (not any(part.startswith('.') for part in Path(file_path).parts) and
                    not should_ignore_file(file_path, ignore_patterns)):
                    markdown_files.append(file_path)
    
    return markdown_files

def process_specific_files(file_list, ignore_patterns):
    """Process specific files with simultaneous edit detection"""
    if not file_list:
        return []
    
    files = [f.strip() for f in file_list.split(',') if f.strip().endswith('.md')]
    
    # Check for simultaneous edits
    skip_files = check_simultaneous_edits(files)
    
    if skip_files:
        print(f"Skipping translation for simultaneously edited files: {skip_files}")
    
    # Process files that weren't simultaneously edited
    processed = []
    for file in files:
        if file in skip_files:
            print(f"Skipping {file} due to simultaneous edit")
            continue
            
        if os.path.exists(file):
            print(f"Processing specific file: {file}")
            if sync_translations(file, ignore_patterns):
                processed.append(file)
        else:
            print(f"File not found: {file}")
    
    return processed

def delete_translated_files(deleted_files):
    """Delete corresponding translated files"""
    if not deleted_files:
        return
    
    files = [f.strip() for f in deleted_files.split(',') if f.strip().endswith('.md')]
    
    for file in files:
        path = Path(file)
        
        # Special case for README.md
        if path.name == "README.md":
            # Delete README.ja.md if it exists
            readme_ja = path.parent / "README.ja.md"
            if readme_ja.exists():
                print(f"Deleting translated file: {readme_ja}")
                os.remove(readme_ja)
            continue
        
        source_lang = get_file_language(file)
        if not source_lang:
            continue
            
        # Delete corresponding translation
        target_lang = "ja" if source_lang == "en" else "en"
        translated_path = get_translated_path(file, target_lang)
        
        if translated_path.exists():
            print(f"Deleting translated file: {translated_path}")
            os.remove(translated_path)

def main():
    parser = argparse.ArgumentParser(description='Translate markdown files for PR events')
    parser.add_argument('--initial-setup', action='store_true', help='Perform initial setup translation')
    parser.add_argument('--files', type=str, help='Comma-separated list of files to translate')
    parser.add_argument('--deleted-files', type=str, help='Comma-separated list of deleted files')
    args = parser.parse_args()

    # Load ignore patterns
    ignore_patterns = load_ignore_patterns()
    print(f"📋 Using {len(ignore_patterns)} ignore patterns")
    print(f"   Patterns: {', '.join(ignore_patterns[:5])}{'...' if len(ignore_patterns) > 5 else ''}")

    # Handle deleted files first
    if args.deleted_files:
        print(f"Deleting translated files for: {args.deleted_files}")
        delete_translated_files(args.deleted_files)

    # Track statistics
    processed_count = 0

    # Process translations
    if args.initial_setup:
        print("Performing initial setup translation")
        markdown_files = find_markdown_files(ignore_patterns)
        if not markdown_files:
            print("No markdown files found to translate")
            return
        
        print(f"Found {len(markdown_files)} markdown files to process (after filtering)")
        for file in markdown_files:
            if sync_translations(file, ignore_patterns):
                processed_count += 1
            
    elif args.files:
        print(f"Processing specific files: {args.files}")
        processed = process_specific_files(args.files, ignore_patterns)
        processed_count = len(processed)
    else:
        markdown_files = find_markdown_files(ignore_patterns)
        if not markdown_files:
            print("No markdown files found to translate")
            return
            
        print(f"Found {len(markdown_files)} markdown files to process (after filtering)")
        for file in markdown_files:
            if sync_translations(file, ignore_patterns):
                processed_count += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 Translation Summary:")
    print(f"   ✅ Processed: {processed_count} files")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()