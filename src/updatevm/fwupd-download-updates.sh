#!/bin/bash

FWUPD_UPDATEVM_DIR=/home/user/.cache/fwupd

echo "Running fwupd download script..."

CLEAN=
CHECK_ONLY=
METADATA=
SHASUM=
UPDATE=
URL=
FW_NAME=

while [ -n "$1" ]; do
    case $1 in
        --CHECK_ONLY)
            CHECK_ONLY=1
            ;;
        --clean)
            CLEAN=1
            ;;
        --metadata)
            METADATA=1
            ;;
        --url=*)
            URL=${1#--url=}
            FW_NAME=${1#--url=https://fwupd.org/downloads/}
            ;;
        --sha=*)
            UPDATE=1
            SHASUM=${1#--sha=}
            ;;
        -*)
            echo "Command $1 unknown. exiting..."
            exit 1
            ;;
        *)
            echo "Command $1 unknown. exiting..."
            exit 1
            ;;
    esac
    shift
done

if [ ! -d $FWUPD_UPDATEVM_DIR ]; then
    echo "fwupd updates dir does not exist: $FWUPD_UPDATEVM_DIR" >&2
    exit 1
fi

if [ "$CHECK_ONLY" == "1" ]; then
    echo "Check only mode."
fi

if [ "$CLEAN" == "1" ]; then
    echo "Cleaning cache."
    rm -rf $FWUPD_UPDATEVM_DIR/metadata/*
    rm -rf $FWUPD_UPDATEVM_DIR/updates/*
fi

if [[ "$URL" == *"--and--"* ]]; then
    URL=${URL//--and--/&}
    FW_NAME="untrusted.cab"
fi

if [[ "$URL" == *"%20"* ]]; then
    FW_NAME="untrusted.cab"
fi

if [[ "$URL" == *"--or--"* ]]; then
    URL=${URL//--or--/|}
    FW_NAME="untrusted.cab"
fi

if [[ "$URL" == *"--hash--"* ]]; then
    URL=${URL//--hash--/#}
    FW_NAME="untrusted.cab"
fi

if [ "$METADATA" == "1" ] && [ -z "$URL" ]; then
    echo "Downloading metadata."
    rm -rf $FWUPD_UPDATEVM_DIR/metadata/*
    wget -P $FWUPD_UPDATEVM_DIR/metadata \
        https://fwupd.org/downloads/firmware.xml.gz
    wget -P $FWUPD_UPDATEVM_DIR/metadata \
        https://fwupd.org/downloads/firmware.xml.gz.jcat
    wget -P $FWUPD_UPDATEVM_DIR/metadata \
        https://fwupd.org/downloads/firmware.xml.gz.asc
    gpg --verify $FWUPD_UPDATEVM_DIR/metadata/firmware.xml.gz.asc \
        $FWUPD_UPDATEVM_DIR/metadata/firmware.xml.gz
    if [ ! $? -eq 0 ]; then
        echo "Signature did NOT match. Exiting..."
        exit 1
    fi
fi

if [ "$METADATA" == "1" ] && [ -n "$URL" ]; then
    echo "Downloading metadata."
    rm -rf $FWUPD_UPDATEVM_DIR/metadata/*
    wget -P $FWUPD_UPDATEVM_DIR/metadata $URL
    wget -P $FWUPD_UPDATEVM_DIR/metadata $URL.jcat
    wget -P $FWUPD_UPDATEVM_DIR/metadata $URL.asc
    gpg --verify $FWUPD_UPDATEVM_DIR/metadata/$FW_NAME.asc \
        $FWUPD_UPDATEVM_DIR/metadata/$FW_NAME
    if [ ! $? -eq 0 ]; then
        echo "Signature did NOT match. Exiting..."
        exit 1
    fi
fi

if [ "$UPDATE" == "1" ]; then
    echo "$SHASUM  $FWUPD_UPDATEVM_DIR/updates/$FW_NAME" \
        > $FWUPD_UPDATEVM_DIR/updates/sha1-$FW_NAME
    echo "Downloading firmware update $FW_NAME"
    wget -O $FWUPD_UPDATEVM_DIR/updates/$FW_NAME $URL
    sha1sum -c $FWUPD_UPDATEVM_DIR/updates/sha1-$FW_NAME
    if [ ! $? -eq 0 ]; then
        rm -f $FWUPD_UPDATEVM_DIR/updates/*
        echo "Computed checksum did NOT match. Exiting..."
        exit 1
    fi
fi
