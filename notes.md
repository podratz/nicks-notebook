
'''
notebook:
notebook [-h|--help]
notebook ls|list
notebook note new
notebook note
notebook new
notebook bind [NAME] #create a .pdf based on the notebook name with all files
               from the notebook directory concatenated
notebook create NOTEBOOK

TODO:
- read notebook directory from $NOTES variable
- create and set new notebook
- list existing notebooks by reading .notebooks file and displaying it
  with mpcurses to select from
- print current notebook by wrapping the read of $NOTES/$NOTEBOOK variable
  in formatted text output
- setup note as a subcommand and forward feed parameters as appropriate
'''

