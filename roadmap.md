

Tree transformer.

* Verify structure
  * Only variable declarations, function definitions and struct definitions allowed at top level.
  * Only variable declarations and function definitions allowed inside struct definitions.
  * Function definitions and struct definitions are not allowed inside function definitions.
* Expand templates.
  * Find template instantiations.
  * Expand those templates into concrete structs and functions.
* Convert methods into functions.
