FROM ubuntu:16.04

MAINTAINER info@noumena.io

# BCN-ENERGY

# PYTHON
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip
#
#
#RUN apt-get update && apt-get upgrade -y && apt-get install wget -y
## PYTHON INSTALLATION
#ENV PATH /usr/local/bin:$PATH
## http://bugs.python.org/issue19846
## > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
#ENV LANG C.UTF-8
## extra dependencies (over what buildpack-deps already includes)
#RUN apt-get update && apt-get install -y --no-install-recommends \
#		tk-dev \
#		uuid-dev \
#	&& rm -rf /var/lib/apt/lists/*
#
#ENV GPG_KEY 0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D
#ENV PYTHON_VERSION 3.7.3
#RUN set -ex \
#	\
#	&& wget -O python.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" \
#	&& wget -O python.tar.xz.asc "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc" \
#	&& export GNUPGHOME="$(mktemp -d)" \
#	&& gpg --batch --keyserver ha.pool.sks-keyservers.net --recv-keys "$GPG_KEY" \
#	&& gpg --batch --verify python.tar.xz.asc python.tar.xz \
#	&& { command -v gpgconf > /dev/null && gpgconf --kill all || :; } \
#	&& rm -rf "$GNUPGHOME" python.tar.xz.asc \
#	&& mkdir -p /usr/src/python \
#	&& tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
#	&& rm python.tar.xz \
#	\
#	&& cd /usr/src/python \
#	&& gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)" \
#	&& ./configure \
#		--build="$gnuArch" \
#		--enable-loadable-sqlite-extensions \
#		--enable-shared \
#		--with-system-expat \
#		--with-system-ffi \
#		--without-ensurepip \
#	&& make -j "$(nproc)" \
#	&& make install \
#	&& ldconfig \
#	\
#	&& find /usr/local -depth \
#		\( \
#			\( -type d -a \( -name test -o -name tests \) \) \
#			-o \
#			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
#		\) -exec rm -rf '{}' + \
#	&& rm -rf /usr/src/python \
#	\
#	&& python3 --version
## make some useful symlinks that are expected to exist
#RUN cd /usr/local/bin \
#	&& ln -s idle3 idle \
#	&& ln -s pydoc3 pydoc \
#	&& ln -s python3 python \
#	&& ln -s python3-config python-config
## if this is called "PIP_VERSION", pip explodes with "ValueError: invalid truth value '<VERSION>'"
#ENV PYTHON_PIP_VERSION 19.1.1
#RUN set -ex; \
#	\
#	wget -O get-pip.py 'https://bootstrap.pypa.io/get-pip.py'; \
#	\
#	python get-pip.py \
#		--disable-pip-version-check \
#		--no-cache-dir \
#		"pip==$PYTHON_PIP_VERSION" \
#	; \
#	pip --version; \
#	\
#	find /usr/local -depth \
#		\( \
#			\( -type d -a \( -name test -o -name tests \) \) \
#			-o \
#			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
#		\) -exec rm -rf '{}' +; \
#	rm -f get-pip.py
#
##CMD ["python3"]
#
### This is not ideal. The tarballs are not named nicely and EnergyPlus versioning is strange
##ARG ENERGYPLUS_VERSION
##ARG ENERGYPLUS_TAG
##ARG ENERGYPLUS_SHA
##ARG ENERGYPLUS_INSTALL_VERSION
##ENV ENERGYPLUS_VERSION=$ENERGYPLUS_VERSION
##ENV ENERGYPLUS_TAG=v$ENERGYPLUS_VERSION
##ENV ENERGYPLUS_SHA=$ENERGYPLUS_SHA
##
### This should be x.y.z, but EnergyPlus convention is x-y-z
##ENV ENERGYPLUS_INSTALL_VERSION=$ENERGYPLUS_INSTALL_VERSION
##
### Downloading from Github
### e.g. https://github.com/NREL/EnergyPlus/releases/download/v8.3.0/EnergyPlus-8.3.0-6d97d074ea-Linux-x86_64.sh
##ENV ENERGYPLUS_DOWNLOAD_BASE_URL https://github.com/NREL/EnergyPlus/releases/download/$ENERGYPLUS_TAG
##ENV ENERGYPLUS_DOWNLOAD_FILENAME EnergyPlus-$ENERGYPLUS_VERSION-$ENERGYPLUS_SHA-Linux-x86_64.sh
##ENV ENERGYPLUS_DOWNLOAD_URL $ENERGYPLUS_DOWNLOAD_BASE_URL/$ENERGYPLUS_DOWNLOAD_FILENAME
##
##
### Collapse the update of packages, download and installation into one command
### to make the container smaller & remove a bunch of the auxiliary apps/files
### that are not needed in the container
##RUN apt-get update && apt-get install -y ca-certificates curl \
##    && rm -rf /var/lib/apt/lists/* \
##    && curl -SLO $ENERGYPLUS_DOWNLOAD_URL \
##    && chmod +x $ENERGYPLUS_DOWNLOAD_FILENAME \
##    && echo "y\r" | ./$ENERGYPLUS_DOWNLOAD_FILENAME \
##    && rm $ENERGYPLUS_DOWNLOAD_FILENAME \
##    && cd /usr/local/EnergyPlus-$ENERGYPLUS_INSTALL_VERSION \
##    && rm -rf DataSets Documentation ExampleFiles WeatherData MacroDataSets PostProcess/convertESOMTRpgm \
##    PostProcess/EP-Compare PreProcess/FMUParser PreProcess/ParametricPreProcessor PreProcess/IDFVersionUpdater
##
### Remove the broken symlinks
##RUN cd /usr/local/bin \
##    && find -L . -type l -delete
##
### Add in the test files
##ADD test /usr/local/EnergyPlus-$ENERGYPLUS_INSTALL_VERSION/test_run
##RUN cp /usr/local/EnergyPlus-$ENERGYPLUS_INSTALL_VERSION/Energy+.idd \
##        /usr/local/EnergyPlus-$ENERGYPLUS_INSTALL_VERSION/test_run/
##
##VOLUME /var/simdata
##WORKDIR /var/simdata
##
##CMD [ "/bin/bash" ]