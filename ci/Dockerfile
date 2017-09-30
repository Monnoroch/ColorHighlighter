FROM buildpack-deps:jessie-scm

LABEL \
    Maintainer="Monnoroch" \
    Description="This image contains utilities required to run CI scripts in color_highlighter project."

# This code needs for ability to reset the docker build cache.
RUN echo Dokerfile version: 1

RUN \
    echo "deb http://ftp.de.debian.org/debian unstable main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends apt-utils=1.0.* psmisc=22.2* python3.5=3.5.* python3-pip=9.0.* \
        bzip2=1.0.* libgtk2.0-0=2.24.* xvfb=2:1.16* imagemagick=8:6.9.7.* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN \
    pip3 install setuptools==36.0.1

WORKDIR /tmp

RUN \
    FILE_NAME="sublime_text_3_build_3143_x64.tar.bz2" && \
    wget "https://download.sublimetext.com/$FILE_NAME" && \
    tar -jxvf "$FILE_NAME" && \
    mv sublime_text_3 /opt/sublime_text_3 && \
    rm -rf /tmp/*

RUN \
    FILE_NAME="Sublime Text 2.0.2 x64.tar.bz2" && \
    wget "https://download.sublimetext.com/$FILE_NAME" && \
    tar -jxvf "$FILE_NAME" && \
    mv "Sublime Text 2" /opt/sublime_text_2 && \
    rm -rf /tmp/*

WORKDIR /ColorHighlighter

# Install linters.

ARG LINTER_TOKEN

RUN \
    repo_path=/tmp/linters-repo && \
    git clone "http://linter:${LINTER_TOKEN}@gitlab.gxservers.com/monno/linters.git" "${repo_path}" && \
    (cd "${repo_path}" && git checkout 812c4a6cb2b894ed2f1efc3ca7abc32447c26e3e) && \
    mkdir -p generated && \
    linters=/opt/linters-system && \
    mv "${repo_path}"/linters ${linters} && \
    rm -rf "${repo_path}" && \
    linters_generator=${linters}/linters-generator && \
    curl -fksSL -o ${linters_generator} --header "PRIVATE-TOKEN: ${LINTER_TOKEN}" \
        "http://gitlab.gxservers.com/monno/linters/builds/artifacts/master/raw/artifacts/generator?job=release" && \
    chmod +x ${linters_generator} && \
    ${linters_generator} -config ${linters} \
        -tags python && \
    ${linters}/generated/install-linux.sh

RUN \
    pip3 install pytest==3.1.2 mockito==1.0.12

# This will create ~/.config/sublime-text-3 and ~/.config/sublime-text-2 and put the plugins there.
RUN \
    export DISPLAY=:1.0; \
    (Xvfb :1 -screen 0 1024x768x16 &> /opt/xvfb.log &); \
    sleep 3; \
    (/opt/sublime_text_3/sublime_text &); \
    sleep 5; \
    (/opt/sublime_text_2/sublime_text &); \
    sleep 5
