# Style Guide

For anything not specified here, defualt to PEP8.

### Two spaces for indentation.

I just like it better that way.

Remember pants.

TODO: I remember reading a post somewhere on the internet about how style guides should be treated like wearing pants. If you are in your own house, you can decide on whatever pants policy you like. But if you are in someone else's house and you are a guest, you should respect their pants policy. If I ever find that link, link the above line to that post.

### No line limit.

Instead I have my editor do word wrap.

I hate it when all I do is change the name of something and worry whether it will go over line limit. Comments are worse -- changing one line might mean changing many lines after it as well. I think a line in code should represent a logical line. that way I can do batch edits on code without having to worry about silly things like formatting.

That said, try to be reasonable about line length. If your line gets ridiculously long, try to see if the contents of the line should be split into multiple lines (e.g. if you are enumerating a list of things) or perhaps the logic of the line should be split into multiple parts.

### Naming convention

Function names are PascalCase.

An exception to this is when we are subclasses a class that already uses camelCase for its method names. In that case, we stay consistent by using camelCase (this is the case with all unit tests because of unittest.TestCase's method naming conventions).

### What I see

My Python.sublime-settings look as follows:

    {
        // The number of spaces a tab is considered equal to
        "tab_size": 2,

        // Set to true to insert spaces when tab is pressed
        "translate_tabs_to_spaces": true,

        // Disables horizontal scrolling if enabled.
        // May be set to true, false, or "auto", where it will be disabled for
        // source code, and otherwise enabled.
        "word_wrap": true,
    }

My Markdown.sublime-settings looks as follows:

    {
        // Disables horizontal scrolling if enabled.
        // May be set to true, false, or "auto", where it will be disabled for
        // source code, and otherwise enabled.
        "word_wrap": true,

        // Set to a value other than 0 to force wrapping at that column rather than the
        // window width
        "wrap_width": 80,
    }
