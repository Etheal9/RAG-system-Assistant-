# Screenshots Guide

This directory contains screenshots and visual assets for the README.

## Required Screenshots

To complete Phase 3, take the following screenshots:

### 1. Main Chat Interface (`demo.png`)

**Steps:**
1. Start the Streamlit app: `streamlit run app.py`
2. Ask a question: "What is RAG?"
3. Wait for the answer
4. Take a screenshot of the full interface
5. Save as `assets/demo.png`

**Should show:**
- Chat interface
- Question and answer
- Sidebar with loaded documents

### 2. Source Citations (`sources.png`)

**Steps:**
1. Click "View Sources" on an answer
2. Take a screenshot showing the expanded sources
3. Save as `assets/sources.png`

**Should show:**
- Source document names
- Text snippets from sources

### 3. Document Loading (`loading.png`)

**Steps:**
1. Restart the app
2. Take a screenshot during the "Loading documents..." phase
3. Save as `assets/loading.png`

**Should show:**
- Loading spinner
- System initialization message

## Screenshot Tools

### Windows
- **Snipping Tool**: Win + Shift + S
- **Game Bar**: Win + G (for recording)

### macOS
- **Screenshot**: Cmd + Shift + 4
- **Screen Recording**: Cmd + Shift + 5

### Linux
- **GNOME Screenshot**: PrtScn
- **Flameshot**: `flameshot gui`

## After Taking Screenshots

1. Save all screenshots to this `assets/` directory
2. Verify filenames match:
   - `demo.png`
   - `sources.png`
   - `loading.png`

3. Update README.md line 9 to show actual screenshot:
   ```markdown
   ![RAG System Demo](assets/demo.png)
   ```

4. Optionally add more screenshots to README sections

## Optional: Demo GIF/Video

For extra impact, create a short demo video:

1. **Windows**: Use Xbox Game Bar (Win + G)
2. **macOS**: Use QuickTime Player
3. **Linux**: Use SimpleScreenRecorder

Convert to GIF using:
- [ezgif.com](https://ezgif.com)
- [CloudConvert](https://cloudconvert.com)

Save as `assets/demo.gif` and add to README.

## Tips for Good Screenshots

- ✅ Use full window (not just partial)
- ✅ Show realistic example questions
- ✅ Ensure text is readable
- ✅ Use light theme (better for docs)
- ❌ Don't include sensitive data
- ❌ Don't show API keys

---

**Once screenshots are added, Phase 3 is complete!**
