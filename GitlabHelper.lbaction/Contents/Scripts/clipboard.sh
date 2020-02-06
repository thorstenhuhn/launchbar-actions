#!/bin/bash

if [ "$LB_OPTION_ALTERNATE_KEY" == "1" ]; then
	osascript -e "tell application \"LaunchBar\" to paste in frontmost application \"$1\""
else
	echo -n "$1" | pbcopy
	osascript -e "tell application \"LaunchBar\" to hide"
fi

