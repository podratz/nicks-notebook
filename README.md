# Nick's Notebook

Manage your personal notes in markdown files.

## Conceptual

Every file is to be considered a thought. A thought can be seen as a buidling
block to be used in various contexts in different ways. A thought is an atomic
thing that should maintain self-consistency throughout. The contexts that can
use the thought can be of different forms, allowing it to be reused. A thought
may become part of different papers, different books, or different thought
collections. A thought is identified by the very instant of its inception. Even
thought it may evolve over time, we do not amend its moment of inception after
its first manifestation.

## Installation

## Aliases

Create/Edit your daily note:
``` sh
func n() (cd $NOTES && note --date='day' "$@")
alias N='cd $NOTES'
```

## Limitations

Currently, only the Vi family of editors are supported.

## Recommendations

### For VIM Users

Install the [unimpaired.vim](github.com/tpope/vim-unimpaired) plugin to easily
navigate between notes in a named directory or in the .chrono directory using
the ]f and [f shortcuts.
cojsdeiwo
