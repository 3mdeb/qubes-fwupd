#!/bin/bash

FWUPD_UPDATES_DIR=/home/user/.cache/fwupd

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
            UPDATE=1
            URL=${1#--url=}
            FW_NAME=${1#--url=https://fwupd.org/downloads/}
            ;;
        --sha=*)
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

if [ ! -d $FWUPD_UPDATES_DIR ]; then
    echo "fwupd updates dir does not exist: $FWUPD_UPDATES_DIR" >&2
    exit 1
fi

if [ "$CHECK_ONLY" == "1" ]; then
    echo "Check only mode."
fi

if [ "$CLEAN" == "1" ]; then
    echo "Cleaning cache."
    rm -rf $FWUPD_UPDATES_DIR/metadata/*
    rm -rf $FWUPD_UPDATES_DIR/updates/*
fi

if [ "$METADATA" == "1" ]; then
    echo "Downloading metadata."
    rm -rf $FWUPD_UPDATES_DIR/metadata/*
    wget -P $FWUPD_UPDATES_DIR/metadata \
        https://cdn.fwupd.org/downloads/firmware.xml.gz
    wget -P $FWUPD_UPDATES_DIR/metadata \
        https://cdn.fwupd.org/downloads/firmware.xml.gz.asc
    gpg --verify $FWUPD_UPDATES_DIR/metadata/firmware.xml.gz.asc \
        $FWUPD_UPDATES_DIR/metadata/firmware.xml.gz
    if [ ! $? -eq 0 ]; then
        echo "Signature did NOT match. Exiting..."
        exit 1
    fi
fi

if [ "$UPDATE" == "1" ]; then
    echo "$SHASUM  $FWUPD_UPDATES_DIR/updates/$FW_NAME" \
        > $FWUPD_UPDATES_DIR/updates/sha1-$FW_NAME
    echo "Downloading firmware update $FW_NAME"
    wget -P $FWUPD_UPDATES_DIR/updates $URL
    sha1sum -c $FWUPD_UPDATES_DIR/updates/sha1-$FW_NAME
    if [ ! $? -eq 0 ]; then
        rm -f $FWUPD_UPDATES_DIR/updates/*
        echo "Computed checksum did NOT match. Exiting..."
        exit 1
    fi
fi
