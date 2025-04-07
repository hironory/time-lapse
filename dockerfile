# ベースイメージ
FROM python:3.9-slim

RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

# 必要なライブラリをインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && apt-get clean

#install packages
RUN apt-get update
RUN apt-get install sudo -y
RUN apt-get install -y vim nano wget

# Gradioのfrpcファイルを手動でダウンロード
RUN mkdir -p /usr/local/lib/python3.9/site-packages/gradio && \
    wget https://cdn-media.huggingface.co/frpc-gradio-0.2/frpc_linux_amd64 -O /usr/local/lib/python3.9/site-packages/gradio/frpc_linux_amd64_v0.2 && \
    chmod +x /usr/local/lib/python3.9/site-packages/gradio/frpc_linux_amd64_v0.2
#install pip packages

# 作業ディレクトリを設定
WORKDIR /app

# 必要なPythonパッケージをインストール
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ユーザーを作成
RUN groupadd -r user && useradd -r -g user user
RUN mkdir -p /home/user && chown -R user:user /home/user

WORKDIR /home/user
# 作成したユーザーに切り替える
USER user

# アプリケーションの実行
CMD ["python", "/app/timelapse-gui.py"]
