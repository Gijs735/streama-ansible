# Pack the jar
- Github doesn't allow files larger then 100MB
- To pack the streama jar use: 
    tar cvzf - streama.jar | split -b 49m - streama.tar.gz.
- Put those files in here
- This solves the 100MB probmlem
