# 🔧 Hướng Dẫn Setup Virtual Environment

## 📋 Yêu Cầu

- **Python:** 3.11 hoặc cao hơn
- **uv:** Package manager (đã cài)
- **Project:** NaviAgent

---

## 🚀 Các Bước Setup

### **1. Xóa Virtual Environment Cũ (Nếu Có)**

```powershell
cd E:\NaviAgent
Remove-Item -Recurse -Force .venv
```

### **2. Kiểm Tra Python Version**

```powershell
python --version
# Phải là Python 3.11.x hoặc cao hơn
```

Nếu không có Python 3.11+, tải tại: https://www.python.org/downloads/

### **3. Tạo Virtual Environment Mới**

```powershell
cd E:\NaviAgent
python -m venv .venv
```

### **4. Sync Dependencies với UV**

```powershell
cd E:\NaviAgent
uv sync --python 3.11
```

Lệnh này sẽ:
- Tạo/cập nhật virtual environment
- Cài đặt tất cả dependencies từ `pyproject.toml`
- Link với Python 3.11

### **5. Test Installation**

```powershell
cd E:\NaviAgent\src\travel_planner
uv run python -c "import sys; print(f'Python {sys.version}')"
```

Expected output:
```
Python 3.11.9 ...
```

### **6. Test Model Config**

```powershell
cd E:\NaviAgent\src\travel_planner
uv run python -c "from config import model_settings; model_settings.print_config_summary()"
```

Expected output:
```
============================================================
🤖 AGENT MODEL CONFIGURATION
============================================================
📋 Default Provider: openai
📋 Default Model: gpt-4o-mini
...
```

### **7. Test Main Application**

```powershell
cd E:\NaviAgent\src\travel_planner
uv run python main.py
```

Expected output:
```
================================================================================
Starting Travel Planner API v1.0.0
================================================================================
✓ Configured providers: openai
🤖 Model Configuration:
   Provider: openai
   Model: gpt-4o-mini
...
```

---

## 🔄 Nếu Gặp Lỗi

### **Lỗi: "No Python at 'C:\Users\...\anaconda3\python.exe'"**

**Nguyên nhân:** UV đang tìm Python ở path cũ (Anaconda)

**Giải pháp:**
```powershell
# 1. Xóa .venv cũ
cd E:\NaviAgent
Remove-Item -Recurse -Force .venv

# 2. Sync lại với Python 3.11
uv sync --python 3.11
```

### **Lỗi: "requires-python >=3.12"**

**Nguyên nhân:** File `pyproject.toml` yêu cầu Python 3.12 nhưng bạn có 3.11

**Giải pháp:** File đã được update để hỗ trợ Python 3.11+, chỉ cần:
```powershell
uv sync --python 3.11
```

### **Lỗi: Module không tìm thấy**

**Giải pháp:**
```powershell
cd E:\NaviAgent
uv sync --python 3.11 --reinstall
```

---

## 🎯 Commands Hữu Ích

### **Chạy script với UV:**
```powershell
cd E:\NaviAgent\src\travel_planner
uv run python main.py
uv run python test_api.py
uv run python test_model_config.py
```

### **Activate virtual environment thủ công:**
```powershell
cd E:\NaviAgent
.\.venv\Scripts\Activate.ps1
python --version
```

### **Deactivate:**
```powershell
deactivate
```

### **Xem packages đã cài:**
```powershell
uv pip list
```

### **Cài package mới:**
```powershell
uv pip install package-name
```

### **Update tất cả packages:**
```powershell
uv sync --upgrade
```

---

## 📦 Dependencies Chính

- **agno==2.1.6** - AI agent framework
- **fastapi==0.115.0** - Web framework
- **openai>=1.60.0** - OpenAI API
- **pydantic==2.10.4** - Data validation
- **uvicorn==0.34.0** - ASGI server

Xem đầy đủ trong `pyproject.toml`

---

## ✅ Checklist Setup

- [ ] Python 3.11+ đã cài
- [ ] UV đã cài
- [ ] Virtual environment đã tạo
- [ ] Dependencies đã sync (`uv sync`)
- [ ] Model config hoạt động
- [ ] Main.py import thành công
- [ ] Server có thể khởi động

---

## 🎉 Hoàn Tất!

Sau khi setup xong, bạn có thể:

1. **Khởi động server:**
   ```powershell
   cd E:\NaviAgent\src\travel_planner
   uv run python main.py
   ```

2. **Test API:**
   ```powershell
   cd E:\NaviAgent\src\travel_planner
   uv run python test_api.py
   ```

3. **Thay đổi provider:** Edit `main.py` dòng ~75
   ```python
   model_settings.default_provider = ModelProvider.GOOGLE
   ```

---

## 📚 Tài Liệu Liên Quan

- **`HOW_TO_CHANGE_PROVIDER.md`** - Cách thay đổi AI provider
- **`AGENTS_UPDATED.md`** - Tổng kết các agents
- **`FIXED_MAIN.md`** - Sửa lỗi main.py
- **`config/HUONG_DAN_TIENG_VIET.md`** - Hướng dẫn model config

---

**Lưu ý:** Luôn dùng `uv run python` thay vì chỉ `python` để đảm bảo chạy trong virtual environment đúng!
