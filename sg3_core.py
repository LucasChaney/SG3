#!/usr/bin/env python3
"""
***sg3_core***
was made using Thonny
~~~~~~~~~~~~~~~~~~~~~
Authors: Gabriel Jackson, Caleb Jacobs, Luke Chaney, Paul Corbin
Date: 12/09/2025

SG3 core acts as the backend logic to the SG3 GUI.

*SG3 Core was also converted' from SG2 with minimal changes to logic.*

All user input and print statements have been removed so the GUI can control ALL interaction.

PROGRAMMER NOTES:
- This file contains NO GUI, NO input(), NO print().
- All functions now take parameters and return results.
"""

from os import path
from collections import defaultdict
from pathlib import Path
import string
from collections import defaultdict

# constant for extension checking
file_extension = "txt"


# ------------------------------------------------------------------------------------
# SG2 → SG3_core: promptUser() simply returns the string instead of printing
# ------------------------------------------------------------------------------------
def promptUser_message():
    """
    Returns the same description SG2 printed, but now as a string.
    The GUI will display this text in a popup window.
    """
    return (
        "This app reads up to 10 text files, stores each file into a wordlist, "
        "displays a summary table, shows how many times a specific word appears, "
        "and builds a concordance listing each word’s locations across all files."
    )


# ------------------------------------------------------------------------------------
# FILE VALIDATION (formerly getFile)
# ------------------------------------------------------------------------------------
def validate_filename(filename):
    """
    Validates the filename EXACTLY like SG2.getFile did,
    but instead of input() loops, this function returns:
      - (True, fullpath) if valid
      - (False, error_message) if invalid

    GUI will handle looping.
    """
    if len(filename) == 0:
        return False, "Input is empty."

    if not filename.lower().endswith(".txt"):
        return False, "Invalid file type. Must be a .txt file."

    file = Path(filename).resolve()
    if not file.exists():
        return False, "File does not exist in this directory."

    return True, str(file)


# ------------------------------------------------------------------------------------
# GET CONTENT (unchanged logic, but NO prints)
# ------------------------------------------------------------------------------------
def getContent(filename, with_pos: bool):
    """
    Reads text file & converts into word list using SG2's merging + hyphen rules.
    Takes bool for either including word position (concordance)
    or not.

    EXACT SG2 logic preserved.
    """
    wordlist = []
    positions = [] # For concordance
    endFunction = False

    removables = string.punctuation.replace("-", "") + "\n\r"

    while endFunction == False:
        with open(filename, "rt") as f:
            prev_word = ""
            mergePrevWord = False
            line_number = 0

            for line in f:
                #For concordance
                line_number += 1
                word_number = 0
                
                # If prev line ended with trailing "-" and current line does not
                if len(prev_word) > 0 and not line.startswith(" "):
                    mergePrevWord = True
                
                # Splits words on spaces
                words = line.split(" ")

                for idx, word in enumerate(words):
                    # Skips empty splits from multi spaces or trailing spaces
                    if word == "":
                        continue
                    # Skips standalone hyphens 
                    if word.strip() == "-":
                        continue
                    
                    endofLine = len(words) - 1
                    
                    if mergePrevWord:
                        # Merges previous word with current line word
                        merged = prev_word + words[0]
                        merged = merged.strip(removables)
                        if merged:
                            word_number += 1
                            lw = merged.lower()
                            wordlist.append(lw)
                            if with_pos:
                                positions.append((line_number, word_number, lw))
                        # Resets
                        prev_word = ""
                        mergePrevWord = False
                        if idx == 0:
                            continue
                            
                    # Handles current word
                    if word.endswith("-"):
                        # If this word is the LAST token on the line, and it ends
                        # with '-', it might be a cross-line hyphenation fragment.
                        if idx == endofLine:
                            # Save raw fragment (with trailing '-') for next line
                            prev_word = word
                        else:
                            # Internal '-' (not at the very end of the line): just
                            # remove any '-' that are not wanted and strip punctuation
                            cleaned = word.replace("-", "")
                            cleaned = cleaned.strip(removables)
                            if cleaned:
                                word_number += 1
                                lw = cleaned.lower()
                                wordlist.append(lw)
                                if with_pos:
                                    positions.append((line_number, word_number, lw))

                    elif word.startswith("-"):
                        # Leading '-' is treated as punctuation, not part of the word
                        cleaned = word.replace("-", "")
                        cleaned = cleaned.strip(removables)
                        if cleaned:
                            word_number += 1 
                            lw = cleaned.lower()
                            wordlist.append(lw)
                            if with_pos:
                                positions.append((line_number, word_number, lw))

                    else:
                        # Normal word: strip punctuation/newlines from the ends,
                        # but keep internal '-' intact
                        cleaned = word.strip(removables)
                        if cleaned:
                            word_number += 1
                            lw = cleaned.lower()
                            wordlist.append(lw)
                            if with_pos:
                                positions.append((line_number, word_number, lw))
            # For lines ending in '-' with nothing to merge
            if prev_word:
                tail = prev_word.rstrip("-").strip(removables)
                if tail:
                    lw = tail.lower()
                    wordlist.append(lw)
                    if with_pos:
                        positions.append((line_number, word_number + 1, lw))
        endFunction = True

    if with_pos:
        return positions
    else: 
        return wordlist


# ------------------------------------------------------------------------------------
# SEARCH WORD VALIDATION (Non-GUI version of getSearchWord)
# ------------------------------------------------------------------------------------
def validate_search_word(word):
    """
    Replaces SG2.getSearchWord input loop. GUI handles the loop.

    Returns:
        (True, cleaned_word) if valid
        (False, error_message) if invalid
    """
    LegalCharacters = 'abcdefghijklmnopqrstuvwxyz-'

    if len(word) == 0:
        return False, "Please enter a word."

    # Character-level check
    for char in word:
        if char.lower() not in LegalCharacters:
            return False, f"Illegal character detected: '{char}'"

    # Hyphen placement rules
    if "-" in word:
        idx = word.find("-")
        if idx == 0 or idx == len(word) - 1:
            return False, "Hyphens must be between letters (no leading/trailing hyphens)."

    return True, word


# ------------------------------------------------------------------------------------
# COUNT OCCURRENCES (unchanged)
# ------------------------------------------------------------------------------------
def countOccurrences(wordList, searchWord):
    """
    SAME LOGIC AS SG2:
    - Case-insensitive
    """
    count = 0
    target = searchWord.casefold()

    for word in wordList:
        if word.casefold() == target:
            count += 1

    return count


# ------------------------------------------------------------------------------------
# FILE SUMMARY (returns table rows instead of printing)
# ------------------------------------------------------------------------------------
def generate_file_summary(all_wordlists):
    """
    Converts SG2 print_table into a returnable table structure.

    Returns:
        A dict with:
        {
          "header": (col1, col2, col3),
          "rows": [(filename, total_words, distinct_words), ...],
          "widths": (fn_width, t_width, d_width)
        }
    """
    if not all_wordlists:
        return {"error": "There are no files to display"}

    rows = []
    for fullpath, words in all_wordlists.items():
        FileName = Path(fullpath).name
        t_words = len(words)
        d_words = len(set(w.casefold() for w in words if len(w) > 0))
        rows.append((FileName, t_words, d_words))

    fn_width = max(len(r[0]) for r in rows)
    t_width = max(len(str(r[1])) for r in rows)
    d_width = max(len(str(r[2])) for r in rows)

    header_fn = "Filename"
    header_total = "TotalWords"
    header_distinct = "Distinct"

    fn_width = max(fn_width, len(header_fn))
    t_width = max(t_width, len(header_total))
    d_width = max(d_width, len(header_distinct))

    return {
        "header": (header_fn, header_total, header_distinct),
        "rows": rows,
        "widths": (fn_width, t_width, d_width)
    }


# ------------------------------------------------------------------------------------
# SG2 Concordance functions preserved EXACTLY; print removed where needed
# ------------------------------------------------------------------------------------
# Changed concordance to work through getContent with position
def build_Concordance(ignore_Words, file_numbers):
    # Now receives file number from gui object 
    concordance = defaultdict(list)

    for filename, file_Number in file_numbers.items():
        # Reuse getContent's logic, but with positions
        positions = getContent(filename, with_pos=True)

        for (line_Number, word_Number, w) in positions:
            if w in ignore_Words:
                continue
            concordance[w].append((file_Number, line_Number, word_Number))

    return concordance


def create_Concordance_text(concordance, highlight_Words):
    """
    Returns the concordance output as a list of formatted lines.
    GUI decides whether to show it or write to a file.
    """
    output_lines = []
    sort_Words = sorted(concordance.keys(), key=lambda w: w.replace("-", "\x00"))

    for word in sort_Words:
        display_word = word.upper() if word in highlight_Words else word
        locations = concordance[word]
        formatted = "; ".join(f"{f}.{l}.{w}" for f, l, w in locations)
        output_lines.append(f"{display_word} {formatted}.")

    return output_lines


def read_Extra_Lists(filename="ExtraLists.txt"):
    """
    SAME SG2 LOGIC.
    Returns (ignore_list, highlight_list)
    """
    ignore_Words = []
    highlight_Words = []
    section = None

    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.upper() == "IGNORE:":
                    section = "ignore"
                elif line.upper() == "HIGHLIGHT:":
                    section = "highlight"
                elif section == "ignore":
                    ignore_Words.append(line.lower())
                elif section == "highlight":
                    highlight_Words.append(line.lower())

    except FileNotFoundError:
        return [], []

    return ignore_Words, highlight_Words
