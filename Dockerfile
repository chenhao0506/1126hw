# 1. 選擇 Python 3.11 標準版 作為基礎
FROM python:3.11

# 2. 設定工作目錄
WORKDIR /code

# 3. 複製 requirements 並安裝
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 4. 建立一個非 Root 使用者 (User ID 1000)
RUN useradd -m -u 1000 user

# 5. 切換到該使用者
USER user

# 6. 設定環境變數
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    SOLARA_ASSETS_PROXY=False

# 7. 複製所有程式碼到工作目錄
COPY --chown=user . /code

# 8. 啟動指令
CMD ["solara", "run", "app.py", "--host=0.0.0.0", "--port=7860"]