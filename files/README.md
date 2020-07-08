# Howto: tarring streama's jar file in parts
- Github doesn't allow files larger then 100MB. That's why streama's jar file is packed in multiple parts.
- To pack the streama jar use the following command: 
    ```
    tar cvzf - streama.jar | split -b 49m - streama.tar.gz.
    ```
- Put the splitted tar files in here.
- This solves the 100MB problem.
