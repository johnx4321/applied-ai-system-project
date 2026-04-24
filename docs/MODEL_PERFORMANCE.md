# ⏱️ Model Performance Guide

## The Problem

You're seeing timeouts because **deepseek-r1:1.5b is very slow**:

```
⏱️ First query: 30-60 seconds (loading model into memory)
⏱️ Subsequent queries: 15-30 seconds (still slow)
```

This is **normal for deepseek-r1**, but if you want faster results, you have options.

---

## 🚀 Solution 1: Switch to a Faster Model (Recommended)

### Quick Method: Use the Model Switcher

```bash
python switch_model.py
```

This interactive tool will:
1. Show available faster models
2. Download the one you choose
3. Update the app automatically

---

### Model Comparison

| Model | Speed | Quality | Best For | Command |
|-------|-------|---------|----------|---------|
| **gemma2** | 🚀 2-5s | Good | Quick testing | `ollama pull gemma2` |
| **qwen2:1.5b** | ⚡ 5-15s | Very Good | Best balance | `ollama pull qwen2:1.5b` |
| **deepseek-r1:1.5b** | 🐢 30-60s | Excellent | Detailed reasoning | Already installed |

---

### Manual Switch (if script doesn't work)

1. **Download faster model:**
   ```bash
   # Download gemma2 (fastest)
   ollama pull gemma2
   ```

2. **Edit `ai_agent.py` line ~117:**
   ```python
   # Change this:
   def __init__(self, model: str = "deepseek-r1:1.5b", use_ollama: bool = True):
   
   # To this:
   def __init__(self, model: str = "gemma2", use_ollama: bool = True):
   ```

3. **Restart the app:**
   ```bash
   streamlit run app.py
   ```

---

## ⚡ Solution 2: Use Mock Mode (Instant)

No Ollama needed, instant results:

1. Open the app
2. Go to "AI Schedule" tab
3. **Uncheck "Use Ollama"** ✅
4. Click "Generate AI Schedule"
5. Results appear instantly!

✓ Good for testing/demos  
✓ No waiting  
✓ No Ollama required  

Switch back to Ollama once you have a faster model.

---

## 📊 Performance Expectations

### First Query (Model Loading)
- deepseek-r1: 30-60 seconds
- qwen2: 10-30 seconds
- gemma2: 5-15 seconds

### Subsequent Queries (Model Cached)
- deepseek-r1: 15-30 seconds
- qwen2: 5-15 seconds
- gemma2: 2-5 seconds

**Tip:** After the first query, subsequent ones are faster because the model stays in memory.

---

## 🧪 Test Current Setup

```bash
python diagnose_ollama.py
```

This will now show:
- ✅ If Ollama is running
- ✅ If model is available
- ⏱️ How long queries take
- 💡 Recommendations

---

## 💻 System Requirements

### For Fast Models (gemma2, qwen2)
- 4GB RAM (minimum)
- 10GB disk space

### For Slow Models (deepseek-r1)
- 8GB RAM (recommended)
- 20GB disk space
- Patience ☕

---

## Quick Decision Tree

```
Do you want fast results?
├─ YES → Use gemma2 (2-5s per query)
│  └─ Run: python switch_model.py
│
└─ NO, want best quality → Use deepseek-r1
   └─ Be patient, first query ~30-60s
   
Want results RIGHT NOW?
└─ Use Mock Mode (uncheck Ollama)
   └─ Instant, no waiting!
```

---

## Recommendation

**Best for most people:**
```bash
# 1. Download faster model
ollama pull gemma2

# 2. Switch to it
python switch_model.py

# 3. Enjoy 2-5 second response times!
```

---

## Still Too Slow?

If even gemma2 is slow:

1. **Check system resources:**
   ```bash
   # See available RAM
   vm_stat
   ```

2. **Close other apps** (free up RAM)

3. **Use Mock Mode** (instant results, no Ollama)

4. **Consider smaller model:**
   - Try neural-chat (even smaller)
   - Or just use Mock Mode permanently

---

## FAQ

**Q: Why is deepseek-r1 so slow?**
A: It's a 1.5B parameter model that does very detailed reasoning. More parameters = slower.

**Q: Will it get faster after the first query?**
A: Yes! Subsequent queries are faster because the model is already in VRAM. But still slower than smaller models.

**Q: Can I run multiple models?**
A: Yes, Ollama can download multiple. But you can only use one at a time in the app. Switch with `python switch_model.py`

**Q: Will Mock Mode always be available?**
A: Yes! It's the fallback for when Ollama is too slow or not running. Just uncheck "Use Ollama".

**Q: What if I want to keep deepseek for quality?**
A: Use Mock Mode for testing, then click with Ollama enabled when you want the best reasoning (be patient with the 30-60s wait).

---

## Summary

| Issue | Solution | Time |
|-------|----------|------|
| Too slow | Switch to gemma2 | 2-5s queries |
| Still too slow | Use Mock Mode | Instant |
| Want best quality | Keep deepseek | 30-60s/query |

Pick your priority! 🎯
