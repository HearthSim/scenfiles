#!/bin/bash

BASEDIR=$(readlink -f $(dirname "$0"))
CACHEDIR="$WINEPREFIX/drive_c/Program Files (x86)/Hearthstone/Cache"

cp "$CACHEDIR"/DeckRuleset/* "$BASEDIR"/DeckRuleset
cp "$CACHEDIR"/Scenario/* "$BASEDIR"/Scenario
cp "$CACHEDIR"/Subset/* "$BASEDIR"/Subset
