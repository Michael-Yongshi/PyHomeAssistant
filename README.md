# PyHomeAssistant

## How to

## Development
https://wltd.org/posts/how-to-make-complex-automations-with-appdaemon-easily

NOTE: the log in appdaemon prints from bottom to top!

### apps.yaml
file that lists all runnable scripts in the format:
```
<name>
  module: <filename>
  class: <classname>
```

### emitters
scripts that emit an event to the home assistant so listeners can act upon it, i.e. a doorbell script that emits a 'DOORBELL_PRESSED_EVENT'.

### listeners
scripts that listen for events or state changes before running, i.e. a ringer that plays only if the 'DOORBELL_PRESSED_EVENT' is received.

### generic
scripts that contain generic methods to be reused in listeners, i.e. script to play a sound, which might be called by both a ringer and a smoke alarm script.

## Build

## Test

## Licence
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007